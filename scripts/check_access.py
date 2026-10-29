#!/usr/bin/env python3
"""Read-only, redacted CLI preflight. Never authorizes or reads business content."""
import argparse
import json
import shutil
import subprocess


REQUIRED = {
    "document_search": ("search:docs:read",),
    "message_search": ("search:message", "im:message.reactions:read"),
    "calendar": ("calendar:calendar.event:read",),
    "minutes_search": ("minutes:minutes.search:read",),
    "minutes_detail": ("minutes:minutes.basic:read",),
}


def probe(executable, arguments):
    command = shutil.which(executable)
    if not command:
        return {"probe_error": "tool_missing"}
    try:
        result = subprocess.run(
            [command] + arguments, capture_output=True, text=True, timeout=30
        )
    except subprocess.TimeoutExpired:
        return {"probe_error": "timeout"}
    except OSError:
        return {"probe_error": "execution_failed"}
    # Raw output may include credentials or arbitrary server text. Never echo it.
    for output in (result.stdout, result.stderr):
        try:
            payload = json.loads(output)
        except (ValueError, TypeError):
            continue
        if isinstance(payload, dict):
            if payload.get("ok") is False or payload.get("error"):
                return {"probe_error": "cli_error"}
            return payload
    return {"probe_error": "unreadable_response"}


def summarize_lark(payload):
    if payload.get("probe_error"):
        return {"state": payload["probe_error"], "resource_access": "not_tested"}
    user = (payload.get("identities") or {}).get("user") or {}
    scopes = user.get("scope") or ""
    granted = set(scopes.split() if isinstance(scopes, str) else scopes)
    status = user.get("status", "unknown")
    verified = user.get("verified") is True
    authenticated = status == "ready" or (status == "needs_refresh" and verified)
    categories = {
        name: {"missing_scopes": [scope for scope in required if scope not in granted]}
        for name, required in REQUIRED.items()
    }
    return {
        "state": status,
        "authenticated_for_read_attempt": authenticated,
        "server_verified": verified,
        "categories": categories,
        "resource_access": "not_tested",
        "scope_note": "Candidates only; actual command may require alternatives or extra read scopes.",
    }


def summarize_project(payload):
    if payload.get("probe_error"):
        return {"state": payload["probe_error"], "resource_access": "not_tested"}
    body = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    return {
        "state": "authenticated" if body.get("authenticated") is True else "login_required",
        "resource_access": "not_tested",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lark-cli", default="lark-cli", help="CLI name or local executable path")
    parser.add_argument("--meegle", default="meegle", help="CLI name or local executable path")
    args = parser.parse_args()
    lark = summarize_lark(probe(args.lark_cli, ["auth", "status", "--json", "--verify"]))
    project = summarize_project(probe(args.meegle, ["auth", "status", "--format", "json"]))
    ready = (
        lark.get("authenticated_for_read_attempt", False)
        and not any(c["missing_scopes"] for c in lark.get("categories", {}).values())
        and project["state"] == "authenticated"
    )
    print(json.dumps({"lark": lark, "project": project, "ready_for_read_attempts": ready,
                      "end_to_end_verified": False}, ensure_ascii=False, indent=2))
    return 0 if ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
