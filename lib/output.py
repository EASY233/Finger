#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
import os
import time
import json
import base64
import xlsxwriter
from config.data import path,Webinfo,Save
from config.data import logging

class Output:
    def __init__(self):
        self.nowTime = time.strftime("%Y%m%d%H%M%S",time.localtime())
        self.filename_html = self.nowTime + '.html'
        self.filename_json = self.nowTime + '.json'
        self.filename_xls = self.nowTime + '.xlsx'
        self.path_html = os.path.join(path.output,self.filename_html)
        self.path_json = os.path.join(path.output,self.filename_json)
        self.path_xls = os.path.join(path.output,self.filename_xls)
        if Save.format == 'html' and Webinfo.result:
            self.outHtml()
        if Save.format == 'json' and Webinfo.result:
            self.outJson()
        if Save.format == 'xls' and Webinfo.result:
            self.outXls()

    def outHtml(self):
        Focus_num = 0
        num = 0
        Focus_assets = []
        assets = []
        html = "PCFET0NUWVBFIGh0bWw+CjxodG1sPgo8aGVhZD4KCTxtZXRhIGNoYXJzZXQ9InV0Zi04Ij4gCgk8dGl0bGU+RmluZ2Vy5omr5o+P5oql5ZGKPC90aXRsZT4KCTxsaW5rIHJlbD0ic3R5bGVzaGVldCIgaHJlZj0iaHR0cHM6Ly9jZG4uc3RhdGljZmlsZS5vcmcvdHdpdHRlci1ib290c3RyYXAvMy4zLjcvY3NzL2Jvb3RzdHJhcC5taW4uY3NzIj4gIAoJPHNjcmlwdCBzcmM9Imh0dHBzOi8vY2RuLnN0YXRpY2ZpbGUub3JnL2pxdWVyeS8yLjEuMS9qcXVlcnkubWluLmpzIj48L3NjcmlwdD4KCTxzY3JpcHQgc3JjPSJodHRwczovL2Nkbi5zdGF0aWNmaWxlLm9yZy90d2l0dGVyLWJvb3RzdHJhcC8zLjMuNy9qcy9ib290c3RyYXAubWluLmpzIj48L3NjcmlwdD4KCTxzY3JpcHQgc3JjPSJodHRwczovL2Nkbi5qc2RlbGl2ci5uZXQvbnBtL2VjaGFydHNANC43LjAvZGlzdC9lY2hhcnRzLm1pbi5qcyI+PC9zY3JpcHQ+CjwvaGVhZD4KPGJvZHk+Cgk8ZGl2IGNsYXNzPSJwYW5lbCBwYW5lbC1kZWZhdWx0Ij4KCQk8ZGl2IGNsYXNzPSJjb250YWluZXIiPgoJCQk8ZGl2IGNsYXNzPSJqdW1ib3Ryb24iPgoJCQkJPGgxPkZpbmdlcjwvaDE+CgkJCQk8aDI+5LiA5qy+57qi6Zif5Zyo5aSn6YeP55qE6LWE5Lqn5Lit5a2Y5rS75o6i5rWL5LiO6YeN54K55pS75Ye757O757uf5oyH57q55o6i5rWL5bel5YW3PC9oMj4KCQkJCSAgICAgICAgICAgIDxwIHN0eWxlPSJmb250LWZhbWlseTog5qW35L2TO2ZvbnQtc2l6ZTogMTZwdDtmb250LXdlaWdodDogYm9sZCI+5b2T5YmN6LWE5Lqn5oC75pWw77yae3t0b3RhbH19PC9wPgoJCQkJPCEtLSDlrZDln5/or6bmg4UgLS0+CgkJCQk8ZGl2PiAKCQkJCQk8ZGl2IGNsYXNzPSJwYW5lbC1oZWFkaW5nIj4KCQkJCQkJPGgzIGNsYXNzPSJwYW5lbC10aXRsZSI+CgkJCQkJCQk8c3BhbiBjbGFzcz0ibGFiZWwgbGFiZWwtaW5mbyI+6YeN54K55YWz5rOo6LWE5LqnPC9zcGFuPgoJCQkJCQk8L2gzPgoJCQkJCTwvZGl2PgoJCQkJCTxkaXYgY2xhc3M9InBhbmVsLWJvZHkiPgoJCQkJCQk8dGFibGUgY2xhc3M9InRhYmxlIHRhYmxlLWhvdmVyIiBzdHlsZT0id29yZC1icmVhazpicmVhay1hbGw7IHdvcmQtd3JhcDpicmVhay1hbGw7Ij4KCQkJCQkJCTx0aGVhZD4KCQkJCQkJCQk8dHI+CgkJCQkJCQkJCTx0aD5JRDwvdGg+CgkJCQkJCQkJCTx0aD51cmw8L3RoPgoJCQkJCQkJCQk8dGg+dGl0bGU8L3RoPgoJCQkJCQkJCQk8dGg+Y21zPC90aD4KCQkJCQkJCQkJPHRoPlNlcnZlcjwvdGg+CgkJCQkJCQkJCTx0aD5zdGF0dXM8L3RoPgoJCQkJCQkJCTwvdHI+CgkJCQkJCQk8L3RoZWFkPgoJCQkJCQkJPHRib2R5PgoJCQkJCQkJCQl7e0ZvY3VzX2Fzc2V0c319CgkJCQkJCQk8L3Rib2R5PgoJCQkJCQk8L3RhYmxlPgoJCQkJCQk8ZGl2PgoJCQkJCQk8L2Rpdj4KCQkJCQk8L2Rpdj4KCQkJCTwvZGl2PgoJCQkJPCEtLSDku7vliqHor6bmg4UgLS0+CgkJCQk8ZGl2PiAKCQkJCQk8ZGl2IGNsYXNzPSJwYW5lbC1oZWFkaW5nIj4KCQkJCQkJPGgzIGNsYXNzPSJwYW5lbC10aXRsZSI+CgkJCQkJCQk8c3BhbiBjbGFzcz0ibGFiZWwgbGFiZWwtaW5mbyI+5YW25LuW6LWE5LqnPC9zcGFuPgoJCQkJCQk8L2gzPgoJCQkJCTwvZGl2PgoJCQkJCTxkaXYgY2xhc3M9InBhbmVsLWJvZHkiPgoJCQkJCQk8dGFibGUgY2xhc3M9InRhYmxlIHRhYmxlLWhvdmVyIj4KCQkJCQkJCTx0aGVhZD4KCQkJCQkJCQk8dHI+CgkJCQkJCQkJCTx0aD5JRDwvdGg+CgkJCQkJCQkJCTx0aD51cmw8L3RoPgoJCQkJCQkJCQk8dGg+dGl0bGU8L3RoPgoJCQkJCQkJCQk8dGg+Y21zPC90aD4KCQkJCQkJCQkJPHRoPlNlcnZlcjwvdGg+CgkJCQkJCQkJCTx0aD5zdGF0dXM8L3RoPgoJCQkJCQkJCTwvdHI+CgkJCQkJCQk8L3RoZWFkPgoJCQkJCQkJPHRib2R5PgoJCQkJCQkJCQl7e2Fzc2V0c319CgkJCQkJCQk8L3Rib2R5PgoJCQkJCQk8L3RhYmxlPgoJCQkJCQk8ZGl2PgoJCQkJCQk8L2Rpdj4KCQkJCQk8L2Rpdj4KCQkJCTwvZGl2PgoJCQkJPCEtLSDmvI/mtJ7or6bmg4UgLS0+CgkJCQk8ZGl2PgoJCQkJCTxoMyBjbGFzcz0iZm9vdGVyLXRpdGxlIj7mnKzns7vnu5/npoHmraLov5vooYzmnKrmjojmnYPjgIHpnZ7ms5XmuJfpgI/mtYvor5U8L2gzPgoJCQkJCTxwPuivt+S9v+eUqOiAhemBteWuiOW9k+WcsOebuOWFs+azleW+i++8jOWLv+eUqOS6jumdnuaOiOadg+a1i+ivle+8jOWmguS9nOS7lueUqOaJgOaJv+WPl+eahOazleW+i+i0o+S7u+S4gOamguS4juS9nOiAheaXoOWFs++8jOS4i+i9veS9v+eUqOWNs+S7o+ihqOS9v+eUqOiAheWQjOaEj+S4iui/sOingueCueOAggoJCQkJCTxici8+CgkJCQkJ6K+m5oOF6K+36K6/6ZeuOiA8YSBocmVmPSJodHRwOi8vd3d3Lm5wYy5nb3YuY24vbnBjL3hpbndlbi8yMDE2LTExLzA3L2NvbnRlbnRfMjAwMTYwNS5odG0iIHRhcmdldD0iX2JsYW5rIj7jgIrkuK3ljY7kurrmsJHlhbHlkozlm73nvZHnu5zlronlhajms5XjgIs8L2E+CgkJCQkJPC9wPgoJCQkJPC9kaXY+CgkJCTwvZGl2PgoJCTwvZGl2PgoJPC9kaXY+CjwvYm9keT4KCgo8L2h0bWw+"
        html = base64.b64decode(html).decode('utf-8')
        for vaule in Webinfo.result:
            if vaule["cms"]:
                Focus_num = Focus_num + 1
                tr = "<tr><td>{0}</td><td><a href='{1}' target ='_blank'>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td></tr>".format(
                    Focus_num, vaule["url"], vaule["title"], vaule["cms"], vaule["Server"], vaule["status"])
                Focus_assets.append(tr)
            else:
                num = num + 1
                tr = "<tr><td>{0}</td><td><a href='{1}' target ='_blank'>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td></tr>".format(
                    num, vaule["url"], vaule["title"], vaule["cms"], vaule["Server"], vaule["status"])
                assets.append(tr)
        html = html.replace("{{Focus_assets}}", ''.join(Focus_assets))
        html = html.replace("{{assets}}", ''.join(assets))
        html = html.replace("{{total}}",str(len(Webinfo.result)))
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
            worksheet.write('A1', 'Url', bold)
            worksheet.write('B1', 'Title', bold)
            worksheet.write('C1', 'cms', bold)
            worksheet.write('D1', 'Server', bold)
            worksheet.write('E1', 'status', bold)
            worksheet.write('F1', 'size', bold)
            row = 1
            col = 0
            for vaule in Webinfo.result:
                worksheet.write(row, col, vaule["url"])
                worksheet.write(row, col+1, vaule["title"])
                worksheet.write(row, col+2, vaule["cms"])
                worksheet.write(row, col+3, vaule["Server"])
                worksheet.write(row, col+4, vaule["status"])
                worksheet.write(row, col+5, vaule["size"])
                row = row + 1
        print()
        successMsg = "结果文件输出路径为:{0}".format(self.path_xls)
        logging.success(successMsg)










