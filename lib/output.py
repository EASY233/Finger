#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
import os
import time
import json
import base64
import xlsxwriter
from config.data import path,Webinfo,Save,Urlerror
from config.data import logging

class Output:
    def __init__(self):
        self.nowTime = time.strftime("%Y%m%d%H%M%S",time.localtime())
        Webinfo.result = Webinfo.result + Urlerror.result
        self.filename_json = self.nowTime + '.json'
        self.filename_xls = self.nowTime + '.xlsx'
        self.path_json = os.path.join(path.output,self.filename_json)
        self.path_xls = os.path.join(path.output,self.filename_xls)
        if Save.format == 'json' and Webinfo.result:
            self.outJson()
        if Save.format == 'xlsx' and Webinfo.result:
            self.outXls()


    def outJson(self):
        with open(self.path_json,'w') as file:
            file.write(json.dumps(Webinfo.result))
        print()
        successMsg = "结果文件输出路径为:{0}".format(self.path_json)
        logging.success(successMsg)

    def outXls(self):
        with xlsxwriter.Workbook(self.path_xls) as workbook:
            worksheet = workbook.add_worksheet('Finger scan')
            bold = workbook.add_format({"bold":True,"valign":"center"})
            worksheet.set_column('A:A', 30)
            worksheet.set_column('B:B', 40)
            worksheet.set_column('C:C', 30)
            worksheet.set_column('D:D', 20)
            worksheet.set_column('E:E', 15)
            worksheet.set_column('F:F', 15)
            worksheet.set_column('G:G', 30)
            worksheet.set_column('H:H', 10)
            worksheet.set_column('I:I', 30)
            worksheet.set_column('J:J', 30)
            worksheet.write('A1', 'Url', bold)
            worksheet.write('B1', 'Title', bold)
            worksheet.write('C1', 'cms', bold)
            worksheet.write('D1', 'Server', bold)
            worksheet.write('E1', 'status', bold)
            worksheet.write('F1', 'size', bold)
            worksheet.write('G1', 'ip', bold)
            worksheet.write('H1', 'iscdn', bold)
            worksheet.write('I1', 'address', bold)
            worksheet.write('J1', 'isp', bold)
            row = 1
            col = 0
            for vaule in Webinfo.result:
                worksheet.write(row, col, vaule["url"])
                worksheet.write(row, col+1, vaule["title"])
                worksheet.write(row, col+2, vaule["cms"])
                worksheet.write(row, col+3, vaule["Server"])
                worksheet.write(row, col+4, vaule["status"])
                worksheet.write(row, col+5, vaule["size"])
                worksheet.write(row, col+6, vaule["ip"])
                worksheet.write(row, col+7, vaule["iscdn"])
                worksheet.write(row, col+8, vaule["address"])
                worksheet.write(row, col+9, vaule["isp"])
                row = row + 1

        print()
        successMsg = "结果文件输出路径为:{0}".format(self.path_xls)
        logging.success(successMsg)










