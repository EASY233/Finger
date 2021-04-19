#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
import sqlite3
import os
from config.color import color
from config.config import Dbsave
from config.data import path,Db,Webinfo,logging

class Save:
    def __init__(self):
        self.Dbpath = os.path.join(path.library,'finger.db')
        self.conn = sqlite3.connect(self.Dbpath)
        self.cur = self.conn.cursor()
        if Db.type and Db.key:
            self.search()
        elif Dbsave and Webinfo.result:
            self.save()
        self.end()

    def save(self):
        for key,value in Webinfo.result.items():
            try:
                url = key
                title = value['title']
                application = value['Application']
                status = value['status']
                language = value['Language']
                server = value['Server']
                system = value['System']
                sql = 'select * from datas where url = "{0}"'.format(url)
                if self.cur.execute(sql).fetchall():
                    update_sql = 'UPDATE datas set title="{0}",application="{1}",server="{2}",language="{3}",system="{4}",status={5} where url="{6}"'.format(
                        title, application, server, language, system, int(status), url)
                    self.cur.execute(update_sql)
                else:
                    self.cur.execute(
                        'INSERT INTO datas(url,title,application,server,language,system,status) VALUES ("{0}","{1}","{2}","{3}","{4}","{5}",{6})'.format(
                            url, title, application, server, language, system, status))
            except:
                pass

    def search(self):
        logging.success("正从数据库:{0}中查询信息".format(self.Dbpath))
        sql = 'select * from datas where {0} like "%{1}%"'.format(Db.type,Db.key)
        self.cur.execute(sql)
        datas = self.cur.fetchall()
        for data in datas:
            Webinfo.result[data[1]] = {"title":data[2],"Application":data[3],"status":data[7],"Server":data[4],"System":data[6],"Language":data[5]}
            Msg = "{0} {1} {2} {4} {3}".format(color.green(data[3]),
                                               color.blue(data[4]), data[2],
                                               color.yellow(data[7]), data[1])
            logging.info(Msg)
        logging.info("共查询到{0}条数据".format(len(Webinfo.result)))

    def end(self):
        self.conn.commit()
        self.conn.close()



