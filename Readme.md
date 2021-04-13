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



## 跟新说明

### V2.0跟新

- 添加了md5识别方法，可在**config/config.py**配置文件种开启该功能默认关闭。
- 指纹库使用[wappalyzer](https://github.com/chorsley/python-Wappalyzer)库()和[TideFinger](https://github.com/TideSec/TideFinger)的cms指纹库。
- 优化了整个识别算法，让其识别更加准确更加高效。
- 修复了若干bug

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

指纹识别库在``library/end.json``中可执行添加修改,添加修改规则:

支持的规则如下:

- 从headers头中匹配规则
- 从html内容中匹配规则
- 从script中匹配规则
- 从meta中匹配规则
- 请求特定的页面进行规则匹配(md5或者keyword)

下面是一些例子:

```
{
	"name": "WordPress",
	"cats": "Application",
	"html": ["<link rel=[\"']stylesheet[\"'] [^>]+wp-(?:content|includes)", "<link[^>]+s\\d+\\.wp\\.com"],
	"meta": {
		"generator": "WordPress( [\\d.]+)?\\;version:\\1"
	}
	, {
	"name": "phpSQLiteCMS",
	"cats": "Application",
	"meta": {
		"generator": "^phpSQLiteCMS(?: (.+))?$\\;version:\\1"
	}
},{
	"name": "非凡建站",
	"cats": "Application",
	"matches": {
		"url": "/images/Jobs_resume_up.gif",
		"md5": "041718edc41fb801317c3a0b1f4b7ca9"
	}
}, {
	"name": "非凡建站",
	"cats": "Application",
	"matches": {
		"url": "/qq/images/mid4.gif",
		"md5": "a2d236f6cf10df3342e017a8aea7de31"
	}
}
```

一些注意事项:

- 注意按照格式填写规则，name识别名字和cats识别类型必须要填。cats目前只支持四类,Application(应用)，Language(语言)，System(操作系统),Server(服务)。

## 运行效果

![](https://picbed.easy233.top//imgimage-20210413095917458.png)
扫描报告样式取自Glass样式报告:
![](https://picbed.easy233.top//imgimage-20210413095949209.png)