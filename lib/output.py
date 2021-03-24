#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
import os
import time
import json
import base64
import xlsxwriter
from config.data import path,Webinfo,Save
from config.config import Version
from config.data import logging

class Output:
    def __init__(self):
        self.nowTime = time.strftime("%Y%m%d%H%M%S",time.localtime())
        self.filename_html = self.nowTime + '.html'
        self.filename_json = self.nowTime + '.json'
        self.filename_xls = self.nowTime + '.xls'
        self.path_html = os.path.join(path.output,self.filename_html)
        self.path_json = os.path.join(path.output,self.filename_json)
        self.path_xls = os.path.join(path.output,self.filename_xls)
        if Save.format == 'html':
            self.outHtml()
        if Save.format == 'json':
            self.outJson()
        if Save.format == 'xls':
            self.outXls()

    def outHtml(self):
        num = 0
        trs = []
        reportTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        html = "PCFET0NUWVBFIGh0bWw+CjxodG1sIGxhbmc9ImVuIj4KICA8aGVhZD4KICAgIDxtZXRhIGNoYXJzZXQ9InV0Zi04Ij4KICAgIDxtZXRhIGh0dHAtZXF1aXY9IlgtVUEtQ29tcGF0aWJsZSIgY29udGVudD0iSUU9ZWRnZSI+CiAgICA8bWV0YSBuYW1lPSJ2aWV3cG9ydCIgY29udGVudD0id2lkdGg9ZGV2aWNlLXdpZHRoLCBpbml0aWFsLXNjYWxlPTEiPgoKICAgIDx0aXRsZT5GaW5nZXLmiavmj4/miqXlkYo8L3RpdGxlPgoKICAgIDxtZXRhIG5hbWU9ImRlc2NyaXB0aW9uIiBjb250ZW50PSJTb3VyY2UgY29kZSBnZW5lcmF0ZWQgdXNpbmcgbGF5b3V0aXQuY29tIj4KICAgIDxtZXRhIG5hbWU9ImF1dGhvciIgY29udGVudD0iTGF5b3V0SXQhIj4KCiAgICA8bGluayByZWw9InN0eWxlc2hlZXQiIGhyZWY9Imh0dHA6Ly9jZG4uYm9vdGNzcy5jb20vYm9vdHN0cmFwLzMuMy4wL2Nzcy9ib290c3RyYXAubWluLmNzcyI+IAogICAgPGxpbmsgcmVsPSJzdHlsZXNoZWV0IiBocmVmPSJodHRwOi8vY2RuLmJvb3Rjc3MuY29tL2ZvbnQtYXdlc29tZS80LjIuMC9jc3MvZm9udC1hd2Vzb21lLm1pbi5jc3MiPiAKCiAgPC9oZWFkPgogIDxib2R5PgoKICAgIDxkaXYgY2xhc3M9ImNvbnRhaW5lci1mbHVpZCI+Cgk8ZGl2IGNsYXNzPSJyb3ciPgoJCTxkaXYgY2xhc3M9ImNvbC1tZC0xMiI+CgkJCTxkaXYgY2xhc3M9InBhZ2UtaGVhZGVyIj4KCQkJCTxoMT4KCQkJCQlGaW5nZXLmiavmj4/miqXlkYogIDxzbWFsbD57e3ZlcnNpb259fTwvc21hbGw+CgkJCQk8L2gxPgoJCQk8L2Rpdj4gPHNwYW4gY2xhc3M9ImxhYmVsIGxhYmVsLXByaW1hcnkiPueUn+aIkOaXtumXtO+8mnt7cmVwb3J0VGltZX19PC9zcGFuPgogICAgICAgICAgICA8L2JyPjwvYnI+CgkJCTx0YWJsZSBjbGFzcz0idGFibGUiPgoJCQkJPHRoZWFkPgoJCQkJCTx0cj4KICAgIDx0aD4jPC90aD4KICAgIDx0aD5Vcmw8L3RoPgogICAgPHRoPlRpdGxlPC90aD4KICAgIDx0aD5BcHBsaWNhdGlvbjwvdGg+CiAgICA8dGg+U2VydmVyPC90aD4KICAgPHRoPkxhbmd1YWdlPC90aD4KICAgIDx0aD5TdGF0dXM8L3RoPgogICAgICAgICAgICAgICAgICAgICAgICAgICAgPC90cj4KCQkJCTwvdGhlYWQ+CiAgICAgICAgICAgICAgICAKCQkJCTx0Ym9keT4KICAgICAgICAgICAgICAgICAgICB7e2NvbnRlbnR9fQoJCQkJPC90Ym9keT4KCQkJPC90YWJsZT4KCQk8L2Rpdj4KCTwvZGl2Pgo8L2Rpdj4KICA8L2JvZHk+CjwvaHRtbD4="
        html = base64.b64decode(html).decode('utf-8')
        html = html.replace("{{reportTime}}", reportTime)
        html = html.replace("{{version}}", Version)
        for key,value in Webinfo.result.items():
            num = num + 1
            url = key
            title = value['title']
            application = value['App_Info']['Application']
            status = value['status']
            language = value['App_Info']['Language']
            server = value['App_Info']['Server']
            tr = "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td><td>{6}</td></tr>".format(
                num, url, title, application, server,language, status)
            trs.append(tr)
        html = html.replace("{{content}}", ''.join(trs))
        with open(self.path_html, 'w', encoding='utf-8') as f:
            f.write(html)
        print()
        successMsg = "结果文件输出路径为:{0}".format(self.path_html)
        logging.success(successMsg)

    def outJson(self):
        with open(self.path_json,'w') as file:
            file.write(json.dumps(Webinfo.result))
        print()
        successMsg = "结果文件输出路径为:{0}".format(self.path_json)
        logging.success(successMsg)

    def outXls(self):
        with xlsxwriter.Workbook(self.path_xls) as workbook:
            worksheet = workbook.add_worksheet('Finger scan')
            bold = workbook.add_format({"bold":True})
            worksheet.set_column('A:A', 30)
            worksheet.set_column('B:B', 30)
            worksheet.set_column('C:C', 30)
            worksheet.set_column('D:D', 30)
            worksheet.set_column('E:E', 30)
            worksheet.set_column('F:F', 30)
            worksheet.set_column('G:G', 30)
            worksheet.write('A1', 'Url', bold)
            worksheet.write('B1', 'Title', bold)
            worksheet.write('C1', 'Application', bold)
            worksheet.write('D1', 'Server', bold)
            worksheet.write('E1', 'Language', bold)
            worksheet.write('F1', 'Status', bold)
            row = 1
            col = 0
            for key, value in Webinfo.result.items():
                url = key
                title = value['title']
                application = value['App_Info']['Application']
                status = value['status']
                language = value['App_Info']['Language']
                server = value['App_Info']['Server']
                worksheet.write(row, col, url)
                worksheet.write(row, col+1, title)
                worksheet.write(row, col+2, application)
                worksheet.write(row, col+3, server)
                worksheet.write(row, col+4, language)
                worksheet.write(row, col+5, status)
                row = row + 1
        print()
        successMsg = "结果文件输出路径为:{0}".format(self.path_xls)
        logging.success(successMsg)










