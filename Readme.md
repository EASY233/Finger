## 前言

一直苦于没有用的顺手的web指纹识别工具，学习前辈s7ckTeam的[Glass](https://github.com/s7ckTeam/Glass)和broken5的[WebAliveScan](https://github.com/broken5/WebAliveScan)优秀开源程序开发的轻量型web指纹工具。

## 安装

### 开发语言

- python3

### 运行环境

- Linux
- Windows
- Mac

### 安装

```
git clone https://github.com/EASY233/Finger
cd Finger
pip3 install -r requirements.txt
```

## 使用方法

### 参数说明

```
optional arguments:
  -h, --help  show this help message and exit

Target:
  -u URL      Input your url target
  -f FILE     Input your target's file

Output:
  -o OUTPUT   Select the output format.eg(html,json,xml,default:html)
  
Usage:
单一URL识别: python3 Finger.py -u http://www.baidu.com or www.baidu.com 
批量URL识别: python3 Finger.py -f xx.txt
输出方式:
支持html，json，xml三种格式默认html格式
用法:python3 Finger.py -f xx.txt -o json
```

### 配置说明

默认线程数为20实际需要修改可以在``config/config.py``中进行修改

```
threads = 20
```

指纹识别库在``config/apps.json``中可执行添加修改,添加修改规则:

例如以下:

```
"phpliteadmin": {
        "cats": "Application",
        "html": [
          "<span id='logo'>phpLiteAdmin</span> <span id='version'>v([0-9.]+)<\\;version:\\1",
          "<!-- Copyright [0-9]+ phpLiteAdmin (?:http://www.phpliteadmin.org/) -->",
          "Powered by <a href='http://www.phpliteadmin\\.org/'"
        ],
        "icon": "phpliteadmin.png",
        "implies": [
          "PHP",
          "SQLite"
        ],
        "website": "http://www.phpliteadmin.org/"
      },
"thttpd": {
        "cats": "Server",
        "headers": {
          "Server": "\bthttpd(?:/([\\d.]+))?\\;version:\\1"
        },
        "icon": "thttpd.png",
        "website": "http://acme.com/software/thttpd"
      },
      
```

主要从两个方面进行识别一是headers头识别，二是html内容识别。无对应规则可不写例如下面JBoss:

```json
"Jboss": {
        "cats": "Application",
        "html": "Your JBoss Application Server",
        "website": "http://jboss.org"
      }
```

## 运行效果

![image-20210324111641053](https://picbed.easy233.top//imgimage-20210324111641053.png)

![](https://picbed.easy233.top//imgimage-20210324111811080.png)

