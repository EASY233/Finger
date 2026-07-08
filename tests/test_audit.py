#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import tempfile
import unittest

from lib.audit import RuleAudit
from lib.runtime import RuntimePaths


class AuditCsvTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        cls.paths = RuntimePaths.from_root(root)

    def test_audit_csv_escapes_formula_like_cells(self):
        findings = [{
            "severity": "HIGH",
            "fingerprint": "=Danger",
            "hits": 1,
            "issue": "@issue",
            "detail": "detail,with,comma",
            "suggestion": "use \"quotes\" safely",
            "examples": ["=cmd|calc", "http://example.test/?q=\"x\""],
        }]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'audit.csv')
            RuleAudit(self.paths.library_dir).save_csv(findings, output_path)
            with open(output_path, 'r', encoding='utf-8-sig') as file:
                content = file.read()

        self.assertIn("'=Danger", content)
        self.assertIn("'@issue", content)
        self.assertIn("'=cmd|calc", content)

    def test_static_rule_findings_reports_alias_fragmentation_and_risky_rules(self):
        audit = RuleAudit(self.paths.library_dir)
        audit.rules = [
            {"cms": "Grafana", "method": "keyword", "location": "title", "keyword": ["Grafana"]},
            {"cms": "grafana", "method": "keyword", "location": "body", "keyword": ["grafana-app"]},
            {"cms": "Prometheus", "method": "keyword", "location": "url", "keyword": ["/graph"]},
            {"cms": "Prometheus", "method": "keyword", "location": "url", "keyword": ["/targets"]},
            {"cms": "Gitlab", "method": "keyword", "location": "header", "keyword": ["Set-Cookie: _gitlab_session="]},
            {"cms": "Gitlab", "method": "keyword", "location": "header", "keyword": ["_gitlab_session"]},
        ]

        findings = audit.run([])
        issues = {(item["fingerprint"], item["issue"]) for item in findings}

        self.assertIn(("prometheus", "URL 路径型规则偏多"), issues)
        self.assertIn(("gitlab", "高风险单头部规则偏多"), issues)

    def test_version_rule_findings_flags_high_value_version_regex(self):
        audit = RuleAudit(self.paths.library_dir)
        audit.rules = [
            {"cms": "Prometheus", "method": "keyword", "location": "title", "keyword": ["Prometheus"], "version_regex": "Prometheus\\s*v?([\\d.]+)", "version_location": "title"},
            {"cms": "Gitea", "method": "keyword", "location": "body", "keyword": ["Gitea"], "version_regex": "Version[:：]\\s*([\\d]+(?:\\.[\\d]+)+)", "version_location": "body"},
        ]

        findings = audit.run([])
        issues = {(item["fingerprint"], item["issue"]) for item in findings}

        self.assertIn(("Prometheus", "version_regex 可靠性需复核"), issues)

    def test_static_rule_findings_skip_aliases_already_canonicalized(self):
        audit = RuleAudit(self.paths.library_dir)
        audit.rules = [
            {"cms": "Grafana", "method": "keyword", "location": "title", "keyword": ["Grafana"]},
            {"cms": "grafana", "method": "keyword", "location": "body", "keyword": ["grafana-app"]},
            {"cms": "Swagger", "method": "keyword", "location": "url", "keyword": ["/swagger-ui.html"]},
        ]

        findings = audit.run([])
        issues = {(item["fingerprint"], item["issue"]) for item in findings}

        self.assertNotIn(("Grafana", "同产品名称碎片化"), issues)


if __name__ == '__main__':
    unittest.main()
