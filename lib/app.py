#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from api.fofa import FofaClient
from api.quake import QuakeClient
from config.data import logging
from lib.audit import RuleAudit
from lib.checkenv import CheckEnv
from lib.finger import Finger
from lib.ip_attributable import IpAttributable
from lib.options import OptionError, build_run_config
from lib.output import Output


class FingerApplication:
    def __init__(self, root_dir=None):
        self.check = CheckEnv(root_dir=root_dir)

    def build_run_config(self, args):
        return build_run_config(args, root_dir=self.check.paths.root_dir)

    def collect_urls(self, run_config):
        urls = list(run_config.urls)

        if run_config.api_provider == 'fofa':
            fofa = FofaClient(
                email=run_config.fofa_email,
                key=run_config.fofa_key,
                default_size=run_config.fofa_size,
                proxy_url=run_config.proxy_url,
                user_agents=run_config.user_agents,
            )
            urls.extend(fofa.search_web_assets(run_config.api_query, size=run_config.api_size))
        elif run_config.api_provider == 'quake':
            quake = QuakeClient(
                token=run_config.quake_key,
                proxy_url=run_config.proxy_url,
                user_agents=run_config.user_agents,
            )
            urls.extend(quake.search_web_assets(run_config.api_query, size=run_config.api_size))

        if run_config.ip_targets:
            fofa = FofaClient(
                email=run_config.fofa_email,
                key=run_config.fofa_key,
                default_size=run_config.fofa_size,
                proxy_url=run_config.proxy_url,
                user_agents=run_config.user_agents,
            )
            urls.extend(fofa.search_ip_web_assets(run_config.ip_targets, size=run_config.api_size))

        return list(dict.fromkeys(urls))

    def run(self, args):
        try:
            run_config = self.build_run_config(args)
        except OptionError as exc:
            logging.error(str(exc))
            raise SystemExit(1)

        if run_config.fingerprint_update:
            self.check.update(proxy_url=run_config.proxy_url)

        try:
            urls = self.collect_urls(run_config)
        except Exception as exc:
            logging.error(str(exc))
            raise SystemExit(1)

        finger = Finger(config=run_config)
        results = finger.scan(urls)

        if run_config.geo:
            results = IpAttributable(results=results, library_dir=run_config.paths.library_dir).results

        output = Output(
            results=results,
            fmt=run_config.output_format,
            output_dir=run_config.paths.output_dir,
            library_dir=run_config.paths.library_dir,
        )

        if run_config.audit:
            self._run_audit(run_config, results, output)

        return results, output

    @staticmethod
    def _run_audit(run_config, results, output):
        audit = RuleAudit(library_dir=run_config.paths.library_dir)
        findings = audit.run(results)
        audit.print_summary(findings)
        if findings:
            latest = getattr(output, 'path', '') or os.path.join(run_config.paths.output_dir, output.filename_xls)
            csv_path = os.path.splitext(latest)[0] + '_audit.csv'
            audit.save_csv(findings, csv_path)
            logging.success(f"审计报告已保存: {csv_path}")
