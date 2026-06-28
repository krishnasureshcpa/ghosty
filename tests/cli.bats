#!/usr/bin/env bats
# Integration tests for phantom CLI.
# Uses `python -m phantom.cli` because entry points need a packaged build.

@test "phantom --help prints usage" {
    run uv run python -m phantom.cli --help
    [ "$status" -eq 0 ]
    echo "$output" | grep -qi "usage"
}

@test "phantom doctor runs without error" {
    run uv run python -m phantom.cli doctor
    [ "$status" -eq 0 ]
}

@test "phantom --version prints version" {
    run uv run python -m phantom.cli --version
    [ "$status" -eq 0 ]
    echo "$output" | grep -qE "phantom"
}

@test "phantom doctor --json produces valid JSON" {
    run uv run python -m phantom.cli doctor --json
    [ "$status" -eq 0 ]
    echo "$output" | python3 -c "import json,sys; json.loads(sys.stdin.read())"
}

@test "phantom snapshot save creates snapshot file" {
    run uv run python -m phantom.cli snapshot save --json
    [ "$status" -eq 0 ]
    echo "$output" | python3 -c "import json,sys; d=json.loads(sys.stdin.read())"
}

@test "phantom harden --help prints harden usage" {
    run uv run python -m phantom.cli harden --help
    [ "$status" -eq 0 ]
    echo "$output" | grep -qi "hardening"
}

@test "phantom snapshot --help prints snapshot usage" {
    run uv run python -m phantom.cli snapshot --help
    [ "$status" -eq 0 ]
    echo "$output" | grep -qi "snapshot"
}
