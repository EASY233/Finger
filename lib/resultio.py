#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import json
import os
import time

import xlsxwriter
from lib.rule_heuristics import normalize_cms_key


CSV_DANGEROUS_PREFIXES = ('=', '+', '-', '@')
XLSX_HEADERS = ['Url', 'Title', 'CMS', 'MaxConfidence', 'FingerprintDetails', 'Version',
                'Server', 'Status', 'Size', 'IP', 'Address', 'ISP',
                'DefaultCreds', 'ErrorType', 'ErrorDetail']
XLSX_WIDTHS = [30, 40, 30, 10, 50, 15, 10, 6, 6, 12, 25, 25, 18, 16, 40]


def normalize_text(value):
    if value is None:
        return ''
    return str(value)


def escape_csv_cell(value):
    text = normalize_text(value)
    if not text:
        return text
    stripped = text.lstrip()
    if text[0] in ('\t', '\r', '\n'):
        return "'" + text
    if text[0] in CSV_DANGEROUS_PREFIXES:
        return "'" + text
    if stripped and stripped[0] in CSV_DANGEROUS_PREFIXES:
        return "'" + text
    return text


def load_default_creds(library_dir):
    default_creds = {}
    creds_orig_keys = {}
    if not library_dir:
        return default_creds, creds_orig_keys

    creds_file = os.path.join(library_dir, 'default_creds.json')
    if not os.path.exists(creds_file):
        return default_creds, creds_orig_keys

    with open(creds_file, 'r', encoding='utf-8') as file:
        raw = json.load(file)

    for key, values in raw.items():
        normalized = normalize_cms_key(key)
        creds_orig_keys.setdefault(normalized, key)
        bucket = default_creds.setdefault(normalized, [])
        for value in values:
            if value not in bucket:
                bucket.append(value)
    return default_creds, creds_orig_keys


def collect_default_creds(cms, default_creds, creds_orig_keys):
    creds = []
    if not cms or cms == '-':
        return creds

    seen = set()
    for fingerprint in cms.split(','):
        fingerprint = fingerprint.strip()
        fingerprint_lower = normalize_cms_key(fingerprint)

        if fingerprint_lower in default_creds:
            label = creds_orig_keys.get(fingerprint_lower, fingerprint)
            for cred in default_creds[fingerprint_lower]:
                if '$hostname' in cred:
                    continue
                entry = f"[{label}] {cred}"
                if entry not in seen:
                    creds.append(entry)
                    seen.add(entry)

        for key, values in default_creds.items():
            if key != fingerprint_lower and len(key) >= 4 and key in fingerprint_lower:
                label = creds_orig_keys.get(key, key)
                for cred in values:
                    if '$hostname' in cred:
                        continue
                    entry = f"[{label}] {cred}"
                    if entry not in seen:
                        creds.append(entry)
                        seen.add(entry)

    return creds


def write_worksheet_cell(worksheet, row, col, value, cell_format=None):
    if isinstance(value, bool):
        worksheet.write_boolean(row, col, value, cell_format)
        return

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        worksheet.write_number(row, col, value, cell_format)
        return

    text = normalize_text(value)
    worksheet.write_string(row, col, text, cell_format)


def format_fingerprint_details(result):
    fingerprints = result.get("fingerprints") or []
    if not fingerprints:
        return ""
    details = []
    for item in fingerprints:
        cms = normalize_text(item.get("cms", ""))
        confidence = item.get("confidence", 0)
        version = normalize_text(item.get("version", ""))
        text = f"{cms}({confidence})"
        if version:
            text += f" {version}"
        details.append(text)
    return " | ".join(details)


def write_results_json(results, filepath):
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(results, file, ensure_ascii=False, indent=2)


def write_results_xlsx(results, filepath, library_dir=None):
    workbook = xlsxwriter.Workbook(
        filepath,
        {'strings_to_formulas': False, 'strings_to_urls': False},
    )
    try:
        worksheet = workbook.add_worksheet('Finger scan')
        bold = workbook.add_format({"bold": True, "valign": "center"})
        red = workbook.add_format({"bold": True, "font_color": "red", "valign": "center"})
        yellow = workbook.add_format({"bold": True, "font_color": "#FF8C00", "valign": "center"})

        for index, (header, width) in enumerate(zip(XLSX_HEADERS, XLSX_WIDTHS)):
            worksheet.set_column(index, index, width)
            write_worksheet_cell(worksheet, 0, index, header, bold)

        default_creds, creds_orig_keys = load_default_creds(library_dir)

        for row, value in enumerate(results, start=1):
            cms = normalize_text(value.get("cms", "-"))
            confidence = value.get("confidence", 0)
            cms_format = None
            if confidence >= 80:
                cms_format = red
            elif confidence >= 50:
                cms_format = yellow

            write_worksheet_cell(worksheet, row, 0, value.get("url", ""))
            write_worksheet_cell(worksheet, row, 1, value.get("title", ""))
            write_worksheet_cell(worksheet, row, 2, cms, cms_format)

            if cms != "-":
                write_worksheet_cell(worksheet, row, 3, confidence)
            else:
                write_worksheet_cell(worksheet, row, 3, "")

            write_worksheet_cell(worksheet, row, 4, format_fingerprint_details(value))
            write_worksheet_cell(worksheet, row, 5, value.get("version", ""))
            write_worksheet_cell(worksheet, row, 6, value.get("Server", ""))
            write_worksheet_cell(worksheet, row, 7, value.get("status", ""))
            write_worksheet_cell(worksheet, row, 8, value.get("size", ""))
            write_worksheet_cell(worksheet, row, 9, value.get("ip", ""))
            write_worksheet_cell(worksheet, row, 10, value.get("address", ""))
            write_worksheet_cell(worksheet, row, 11, value.get("isp", ""))

            creds = collect_default_creds(cms, default_creds, creds_orig_keys)
            write_worksheet_cell(worksheet, row, 12, ' | '.join(creds) if creds else "")
            write_worksheet_cell(worksheet, row, 13, value.get("error_type", ""))
            write_worksheet_cell(worksheet, row, 14, value.get("error_detail", ""))
    finally:
        workbook.close()


def save_results(results, output_dir, fmt, timestamp=None, library_dir=None):
    os.makedirs(output_dir, exist_ok=True)
    if not library_dir:
        raise ValueError("library_dir is required")

    if timestamp is None:
        now = time.time()
        timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime(now)) + f"{int((now % 1) * 1000):03d}"

    if fmt == "json":
        filepath = _unique_output_path(output_dir, timestamp, "json")
        write_results_json(results, filepath)
        return filepath

    if fmt == "xlsx":
        filepath = _unique_output_path(output_dir, timestamp, "xlsx")
        write_results_xlsx(results, filepath, library_dir=library_dir)
        return filepath

    raise ValueError(f"unsupported output format: {fmt}")


def _unique_output_path(output_dir, timestamp, extension):
    base = os.path.join(output_dir, f"{timestamp}.{extension}")
    if not os.path.exists(base):
        return base
    suffix = 1
    while True:
        candidate = os.path.join(output_dir, f"{timestamp}_{suffix}.{extension}")
        if not os.path.exists(candidate):
            return candidate
        suffix += 1


def write_csv_rows(rows, output_path):
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as file:
        writer = csv.writer(file)
        for row in rows:
            writer.writerow([escape_csv_cell(value) for value in row])
