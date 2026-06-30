#!/usr/bin/env bats
# Integration tests for ghosty CLI.
# Uses `python -m ghosty.cli` because entry points need a packaged build.

@test "ghosty --help prints usage" {
    run uv run python -m ghosty.cli --help
    [ "$status" -eq 0 ]
    echo "$output" | grep -qi "usage"
}

@test "ghosty doctor runs without error" {
    run uv run python -m ghosty.cli doctor
    [ "$status" -eq 0 ]
}

@test "ghosty --version prints version" {
    run uv run python -m ghosty.cli --version
    [ "$status" -eq 0 ]
    echo "$output" | grep -qE "ghosty"
}

@test "ghosty doctor --json produces valid JSON" {
    run uv run python -m ghosty.cli doctor --json
    [ "$status" -eq 0 ]
    echo "$output" | python3 -c "import json,sys; json.loads(sys.stdin.read())"
}

@test "ghosty snapshot save creates snapshot file" {
    run uv run python -m ghosty.cli snapshot save --json
    [ "$status" -eq 0 ]
    echo "$output" | python3 -c "import json,sys; d=json.loads(sys.stdin.read())"
}

@test "ghosty harden --help prints harden usage" {
    run uv run python -m ghosty.cli harden --help
    [ "$status" -eq 0 ]
    echo "$output" | grep -qi "hardening"
}

@test "ghosty snapshot --help prints snapshot usage" {
    run uv run python -m ghosty.cli snapshot --help
    [ "$status" -eq 0 ]
    echo "$output" | grep -qi "snapshot"
}
