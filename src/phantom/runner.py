"""
Runner — parallel action execution with progress tracking, dry-run support,
and automatic rollback. Uses asyncio for concurrent execution with
semaphore-controlled parallelism.
"""
from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from phantom.catalog import Action, Op


class ExecStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    DRY_RUN = "dry_run"


@dataclass(slots=True)
class ExecResult:
    """Result of executing a single action."""
    action_id: str
    status: ExecStatus
    started_at: float
    finished_at: float | None = None
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    error: str | None = None
    verify_passed: bool = False


class Runner:
    """Executes actions with parallelism, dry-run, and rollback support."""

    def __init__(
        self,
        max_parallel: int = 4,
        dry_run: bool = False,
        progress_callback: Callable[[str, ExecStatus], None] | None = None,
    ):
        self.max_parallel = max_parallel
        self.dry_run = dry_run
        self.progress_callback = progress_callback
        self._semaphore: asyncio.Semaphore | None = None
        self._results: dict[str, ExecResult] = {}
        self._cancelled = False

    async def run_actions(self, actions: list[Action]) -> dict[str, ExecResult]:
        """Run multiple actions with controlled parallelism."""
        self._semaphore = asyncio.Semaphore(self.max_parallel)
        self._results = {}
        self._cancelled = False

        tasks = [self._run_action(action) for action in actions]
        await asyncio.gather(*tasks, return_exceptions=True)
        return self._results

    async def run_action(self, action: Action) -> ExecResult:
        """Run a single action."""
        self._semaphore = asyncio.Semaphore(1)
        self._results = {}
        self._cancelled = False
        await self._run_action(action)
        return self._results.get(action.id, ExecResult(
            action_id=action.id,
            status=ExecStatus.FAILED,
            started_at=time.time(),
            error="Action not found in results",
        ))

    async def _run_action(self, action: Action) -> None:
        """Execute a single action with verification and rollback support."""
        if self._cancelled:
            return

        result = ExecResult(
            action_id=action.id,
            status=ExecStatus.DRY_RUN if self.dry_run else ExecStatus.RUNNING,
            started_at=time.time(),
        )
        self._results[action.id] = result

        if self.progress_callback:
            self.progress_callback(action.id, result.status)

        if self.dry_run:
            # Simulate execution for dry-run
            await asyncio.sleep(0.1)
            result.status = ExecStatus.DRY_RUN
            result.finished_at = time.time()
            result.stdout = f"[DRY-RUN] Would execute: {action.ops}"
            if self.progress_callback:
                self.progress_callback(action.id, result.status)
            return

        # Execute ops sequentially
        try:
            for op in action.ops:
                await self._run_op(op, result)

            # Run verification ops
            verify_results = []
            for op in action.verify_ops:
                vr = await self._run_op(op, result, capture=True)
                verify_results.append(vr.exit_code == 0)

            result.verify_passed = all(verify_results) if verify_results else True
            result.status = ExecStatus.COMPLETED if result.verify_passed else ExecStatus.FAILED
            result.finished_at = time.time()

        except Exception as e:
            result.status = ExecStatus.FAILED
            result.finished_at = time.time()
            result.error = str(e)

        if self.progress_callback:
            self.progress_callback(action.id, result.status)

    async def _run_op(
        self,
        op: Op,
        result: ExecResult,
        capture: bool = True,
    ) -> ExecResult:
        """Execute a single operation."""
        async with self._semaphore:
            if self._cancelled:
                raise RuntimeError("Execution cancelled")

            cmd = [op.shell, *op.args]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE if capture else None,
                stderr=asyncio.subprocess.PIPE if capture else None,
            )

            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=op.timeout_s,
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                raise RuntimeError(f"Command timed out after {op.timeout_s}s: {op.command_str()}")

            stdout = stdout_bytes.decode() if stdout_bytes else ""
            stderr = stderr_bytes.decode() if stderr_bytes else ""

            if capture:
                result.stdout += stdout + "\n"
                result.stderr += stderr + "\n"

            result.exit_code = proc.returncode or 0

            if proc.returncode != 0 and proc.returncode is not None:
                raise RuntimeError(f"Command failed (exit {proc.returncode}): {op.command_str()}\n{stderr}")

            return result

    def cancel(self) -> None:
        """Cancel all running actions."""
        self._cancelled = True

    def get_summary(self) -> dict:
        """Get execution summary."""
        completed = sum(1 for r in self._results.values() if r.status == ExecStatus.COMPLETED)
        failed = sum(1 for r in self._results.values() if r.status == ExecStatus.FAILED)
        dry_run = sum(1 for r in self._results.values() if r.status == ExecStatus.DRY_RUN)

        return {
            "total": len(self._results),
            "completed": completed,
            "failed": failed,
            "dry_run": dry_run,
            "results": {k: self._result_to_dict(v) for k, v in self._results.items()},
        }

    def _result_to_dict(self, r: ExecResult) -> dict:
        return {
            "action_id": r.action_id,
            "status": r.status.value,
            "duration_s": round((r.finished_at or time.time()) - r.started_at, 3),
            "stdout": r.stdout,
            "stderr": r.stderr,
            "exit_code": r.exit_code,
            "error": r.error,
            "verify_passed": r.verify_passed,
        }


# ---------------------------------------------------------------------------
# Rollback manager
# ---------------------------------------------------------------------------


class RollbackManager:
    """Manages rollback operations for executed actions."""

    def __init__(self, store_path: Path = Path("~/.config/phantom/rollback.jsonl").expanduser()):
        self.store_path = store_path
        self.store_path.parent.mkdir(parents=True, exist_ok=True)

    async def record_execution(self, action_id: str, ops_executed: list[Op], rollback_ops: list[Op]) -> None:
        """Record an execution for potential rollback."""
        entry = {
            "action_id": action_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ops_executed": [op.command_str() for op in ops_executed],
            "rollback_ops": [op.command_str() for op in rollback_ops],
        }
        with self.store_path.open("a") as f:
            f.write(json.dumps(entry) + "\n")

    async def rollback_last(self, count: int = 1) -> list[ExecResult]:
        """Rollback the last N executed actions (in reverse order)."""
        if not self.store_path.exists():
            return []

        entries: list[dict] = []
        with self.store_path.open() as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))

        if not entries:
            return []

        # Take last N entries, reverse for rollback order
        to_rollback = entries[-count:]
        to_rollback.reverse()

        runner = Runner(max_parallel=1, dry_run=False)
        results = []

        for entry in to_rollback:
            # Build fake actions from rollback ops
            for rollback_cmd in entry["rollback_ops"]:
                parts = rollback_cmd.split()
                op = Op(shell=parts[0], args=tuple(parts[1:]), requires_sudo="sudo" in rollback_cmd)
                action = Action(
                    id=f"rollback.{entry['action_id']}",
                    chapter="Rollback",
                    chapter_num=99,
                    title=f"Rollback {entry['action_id']}",
                    risk=RiskLevel.DESTRUCTIVE,
                    type=ActionType.ROLLBACK,
                    description=f"Rollback: {rollback_cmd}",
                    ops=[op],
                )
                res = await runner.run_action(action)
                results.append(res)

        return results

    def get_history(self) -> list[dict]:
        """Get full execution history."""
        if not self.store_path.exists():
            return []

        entries: list[dict] = []
        with self.store_path.open() as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
        return entries


# Import needed types
from phantom.catalog import Action, Op, RiskLevel, ActionType


__all__ = [
    "ExecStatus",
    "ExecResult",
    "Runner",
    "RollbackManager",
]