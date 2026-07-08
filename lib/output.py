#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY233
import os
import time

from config.data import logging
from lib.resultio import save_results

class Output:
    def __init__(self, results, fmt, output_dir, library_dir):
        now = time.time()
        self.nowTime = time.strftime("%Y%m%d%H%M%S", time.localtime(now)) + f"{int((now % 1) * 1000):03d}"
        self.results = list(results or [])
        self.format = fmt
        self.output_dir = output_dir
        self.library_dir = library_dir
        self.filename_json = self.nowTime + '.json'
        self.filename_xls = self.nowTime + '.xlsx'
        self.path_json = os.path.join(self.output_dir, self.filename_json)
        self.path_xls = os.path.join(self.output_dir, self.filename_xls)
        self.path = ''

        if not self.results:
            return

        self.path = save_results(
            self.results,
            self.output_dir,
            self.format,
            timestamp=self.nowTime,
            library_dir=self.library_dir,
        )
        logging.success("结果文件输出路径为:{0}".format(self.path))
