"""Small behavioral checks; run with python3 -m unittest discover -s tests."""
from contextlib import redirect_stdout
from datetime import date
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_report.py"
spec = importlib.util.spec_from_file_location("audit_report", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class ReportAuditTests(unittest.TestCase):
    def test_local_files_fragments_and_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            (root / "image with space.png").write_bytes(b"fixture")
            (root / "other.html").write_text('<h1 id="target">Other</h1>')
            report = root / "report.html"
            report.write_text('<h1 id="same">A</h1><p id="same">B</p>'
                              '<img src="image%20with%20space.png">'
                              '<a href="other.html#target">Good</a>'
                              '<a href="#absent">Bad</a><img src="absent.png">'
                              '<a href="https://example.org/#unknown">Remote unchecked</a>')
            findings = []
            audit.audit_html(report, findings)
            self.assertEqual({x["code"] for x in findings},
                             {"duplicate_id", "missing_fragment", "missing_local_asset"})

    def test_manifest_arithmetic_dates_and_expiry(self):
        findings = []
        audit.audit_manifest({"party_size": 3, "currency": "EUR",
            "stays": [{"check_in": "2030-06-01", "check_out": "2030-06-03", "nights": 3}],
            "budgets": [{"name": "Example", "items": [{"label": "Stay", "group_amount": 90}],
                         "group_total": 100, "per_person": 30}],
            "claims": [{"label": "Offer", "checked_on": "2030-05-01", "valid_until": "2030-05-15", "status": "quoted"}]},
            date(2030, 6, 1), findings)
        self.assertEqual({x["code"] for x in findings},
                         {"night_count_mismatch", "budget_sum_mismatch", "per_person_mismatch", "expired_validity"})
        self.assertEqual(next(x["severity"] for x in findings if x["code"] == "expired_validity"), "warning")

    def test_bool_and_nonfinite_are_not_valid_amounts_or_party(self):
        findings = []
        audit.audit_manifest({"party_size": True, "currency": "EUR", "budgets": [
            {"name": "Invalid", "items": [{"label": "Cost", "group_amount": float("nan")}],
             "group_total": True, "per_person": float("inf")}]}, date(2030, 1, 1), findings)
        self.assertIn("invalid_party_size", {x["code"] for x in findings})
        self.assertEqual(sum(x["code"] == "invalid_amount" for x in findings), 3)

    def test_warning_only_cli_succeeds_and_ignores_script_text(self):
        with tempfile.TemporaryDirectory() as root:
            report = Path(root) / "report.html"
            report.write_text('<h1 id="top">Next sale opens soon</h1>'
                              '<a href="#top">Back</a><script>const s="sold out today";</script>')
            output = io.StringIO()
            with redirect_stdout(output):
                status = audit.main([str(report), "--as-of", "2030-01-01"])
            result = json.loads(output.getvalue())
            self.assertEqual(status, 0)
            self.assertTrue(result["ok"])
            self.assertEqual([x["code"] for x in result["findings"]], ["relative_schedule"])

    def test_missing_required_manifest_fields_fail_without_crashing(self):
        findings = []
        audit.audit_manifest({"budgets": [{"items": []}], "claims": [{}]}, date(2030, 1, 1), findings)
        self.assertGreater(len(findings), 4)
        self.assertTrue(all(x["severity"] == "error" for x in findings))

    def test_valid_manifest_rounds_per_person_to_cents(self):
        findings = []
        audit.audit_manifest({"party_size": 3, "currency": "EUR", "budgets": [
            {"name": "Example", "items": [{"label": "Cost", "group_amount": 100}],
             "group_total": 100, "per_person": 33.33}]}, date(2030, 1, 1), findings)
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
