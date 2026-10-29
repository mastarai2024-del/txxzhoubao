import importlib.util
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location(
    "check_access", Path(__file__).resolve().parents[1] / "scripts" / "check_access.py"
)
access = importlib.util.module_from_spec(spec)
spec.loader.exec_module(access)


class CheckAccessTests(unittest.TestCase):
    def test_redacts_credentials_and_private_identity(self):
        raw = {"access_token": "SENSITIVE_ACCESS", "identities": {"user": {
            "status": "ready", "verified": True, "scope": "search:docs:read",
            "refresh_token": "SENSITIVE_REFRESH", "userName": "PRIVATE_PERSON",
        }}}
        result = access.summarize_lark(raw)
        output = json.dumps(result)
        for secret in ("SENSITIVE_ACCESS", "SENSITIVE_REFRESH", "PRIVATE_PERSON"):
            self.assertNotIn(secret, output)
        self.assertEqual(result["resource_access"], "not_tested")
        self.assertEqual(result["categories"]["message_search"]["missing_scopes"],
                         ["search:message", "im:message.reactions:read"])

    def test_verified_refresh_is_not_forced_reauthorization(self):
        raw = {"identities": {"user": {"status": "needs_refresh", "verified": True}}}
        self.assertTrue(access.summarize_lark(raw)["authenticated_for_read_attempt"])
        raw["identities"]["user"]["verified"] = False
        self.assertFalse(access.summarize_lark(raw)["authenticated_for_read_attempt"])

    def test_project_pending_never_counts_as_authenticated(self):
        result = access.summarize_project({"status": "authorization_pending"})
        self.assertEqual(result["state"], "login_required")
        self.assertEqual(result["resource_access"], "not_tested")

    def test_search_grants_do_not_imply_body_or_artifact_access(self):
        scopes = "search:docs:read search:message im:message.reactions:read calendar:calendar.event:read minutes:minutes.search:read minutes:minutes.basic:read"
        result = access.summarize_lark({"identities": {"user": {
            "status": "ready", "verified": True, "scope": scopes
        }}})
        self.assertEqual(result["categories"]["message_search"]["missing_scopes"], [])
        self.assertEqual(result["categories"]["message_body"]["missing_scopes"], [
            "im:message.group_msg:get_as_user", "im:message.p2p_msg:get_as_user"
        ])
        self.assertEqual(result["categories"]["minutes_artifacts"]["missing_scopes"],
                         ["minutes:minutes.artifacts:read"])

    def test_backend_alternatives_request_only_read_access(self):
        for scope in ("im:message:readonly", "im:message"):
            result = access.summarize_lark({"identities": {"user": {
                "status": "ready", "scope": scope
            }}})
            self.assertEqual(result["categories"]["message_backend"]["missing_scopes"], [])
        result = access.summarize_lark({"identities": {"user": {"status": "ready"}}})
        self.assertEqual(result["categories"]["message_backend"]["missing_scopes"],
                         ["im:message:readonly"])

    @patch.object(access.shutil, "which", return_value="fake-cli")
    @patch.object(access.subprocess, "run")
    def test_cli_error_does_not_echo_server_text(self, run, which):
        run.return_value = subprocess.CompletedProcess([], 3, "", json.dumps({
            "ok": False, "error": {"message": "SENSITIVE_SERVER_TEXT"}
        }))
        self.assertEqual(access.probe("cli", []), {"probe_error": "cli_error"})

    @patch.object(access.shutil, "which", return_value="fake-cli")
    @patch.object(access.subprocess, "run", side_effect=subprocess.TimeoutExpired("fake-cli", 30))
    def test_timeout_is_distinct_from_missing_permissions(self, run, which):
        self.assertEqual(access.probe("cli", []), {"probe_error": "timeout"})


if __name__ == "__main__":
    unittest.main()
