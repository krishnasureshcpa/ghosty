"""Tests for phantom.catalog models — no TUI, no system calls, fast."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from phantom.catalog import Action, ActionType, Catalog, Chapter, Op, RiskLevel


class TestRiskLevel:
    def test_values(self):
        assert RiskLevel.AUDIT == 3
        assert RiskLevel.SAFE == 2
        assert RiskLevel.DESTRUCTIVE == 1


class TestOp:
    def test_minimal(self):
        op = Op(shell="echo")
        assert op.shell == "echo"
        assert op.args == ()
        assert op.capture is True
        assert op.idempotent is True

    def test_command_str(self):
        op = Op(shell="defaults", args=("write", "-g", "NSQuitAlwaysKeepsWindows", "-bool", "false"))
        assert "defaults write -g NSQuitAlwaysKeepsWindows -bool false" == op.command_str()

    def test_sudo_flag(self):
        op = Op(shell="pfctl", args=("-e",), requires_sudo=True)
        assert op.requires_sudo is True


class TestAction:
    def test_minimal(self):
        action = Action(
            id="test.id",
            chapter="Test",
            chapter_num=99,
            title="Test action",
            risk=RiskLevel.SAFE,
            type=ActionType.MUTATE,
            description="A test",
        )
        assert action.id == "test.id"

    def test_invalid_id_raises(self):
        with pytest.raises(ValidationError):
            Action(
                id="INVALID!",  # uppercase + bang
                chapter="Test",
                chapter_num=1,
                title="Bad",
                risk=RiskLevel.AUDIT,
                type=ActionType.READ,
                description="Should fail",
            )

    def test_full_action(self):
        action = Action(
            id="firewall.stealth",
            chapter="Firewall",
            chapter_num=6,
            title="Enable stealth mode",
            risk=RiskLevel.SAFE,
            type=ActionType.MUTATE,
            description="Enable TCP/IP stealth mode",
            ops=[Op(shell="defaults", args=("write", "/Library/Preferences/com.apple.alf", "stealthenabled", "-int", "1"), requires_sudo=True)],
            verify_ops=[Op(shell="defaults", args=("read", "/Library/Preferences/com.apple.alf", "stealthenabled"))],
            rollback_ops=[Op(shell="defaults", args=("write", "/Library/Preferences/com.apple.alf", "stealthenabled", "-int", "0"), requires_sudo=True)],
            tags=["firewall", "network"],
        )
        assert len(action.ops) == 1
        assert len(action.rollback_ops) == 1
        assert "firewall" in action.tags
        assert action.requires_reboot is False

    def test_risk_level_comparison(self):
        destructive = Action(id="risky", chapter="X", chapter_num=1, title="R", risk=RiskLevel.DESTRUCTIVE, type=ActionType.MUTATE, description="R")
        audit = Action(id="safe", chapter="X", chapter_num=1, title="S", risk=RiskLevel.AUDIT, type=ActionType.READ, description="S")
        assert destructive.risk < audit.risk  # 1 < 3
        assert audit.risk > destructive.risk


class TestChapter:
    def test_minimal(self):
        ch = Chapter(number=1, title="Test", summary="A chapter")
        assert ch.number == 1
        assert len(ch.actions) == 0

    def test_with_actions(self):
        ch = Chapter(
            number=6,
            title="Firewall",
            summary="Network isolation",
            actions=[
                Action(id="fw.stealth", chapter="Firewall", chapter_num=6, title="Stealth", risk=RiskLevel.SAFE, type=ActionType.MUTATE, description="Stealth mode"),
            ],
        )
        assert len(ch.actions) == 1
        assert ch.actions[0].id == "fw.stealth"


class TestCatalog:
    def test_empty(self):
        cat = Catalog(chapters=[])
        assert len(cat.chapters) == 0

    def test_with_chapters(self):
        cat = Catalog(
            chapters=[
                Chapter(number=1, title="Intro", summary="Getting started"),
                Chapter(number=6, title="Firewall", summary="Network isolation"),
            ]
        )
        assert len(cat.chapters) == 2

    def test_json_roundtrip(self):
        cat = Catalog(
            chapters=[
                Chapter(
                    number=1,
                    title="Intro",
                    summary="Start here",
                    actions=[
                        Action(id="intro.check", chapter="Intro", chapter_num=1, title="Check", risk=RiskLevel.AUDIT, type=ActionType.READ, description="System check"),
                    ],
                )
            ]
        )
        dumped = cat.model_dump_json(indent=2)
        loaded = Catalog.model_validate_json(dumped)
        assert len(loaded.chapters) == 1
        assert loaded.chapters[0].actions[0].id == "intro.check"


class TestActionType:
    def test_all_enum_values(self):
        assert ActionType.READ.value == "read"
        assert ActionType.MUTATE.value == "mutate"
        assert ActionType.VERIFY.value == "verify"
        assert ActionType.INSTALL.value == "install"
        assert ActionType.ROLLBACK.value == "rollback"
