# Tab 对象访问网页

来源: https://drissionpage.cn/browser_control/visit

本节介绍 Tab 对象访问网页的相关内容。

---

## get() 方法

该方法用于跳转到一个网址。当连接失败时，程序会进行重试。可指定本地文件路径。

### 通用参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `url` | `str` | 必填 | 目标 url，可指向本地文件路径 |
| `show_errmsg` | `bool` | `False` | 连接出错时是否显示和抛出异常 |
| `retry` | `int` | `None` | 重试次数，为 `None` 时使用页面参数，默认 `3` |
| `interval` | `float` | `None` | 重试间隔（秒），为 `None` 时使用页面参数，默认 `2` |
| `timeout` | `float` | `None` | 加载超时时间（秒） |

### s 模式专用参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `params` | `dict` | `None` | url 请求参数 |
| `data` | `dict` `str` | `None` | 携带的数据 |
| `json` | `dict` `str` | `None` | 要发送的 JSON 数据 |
| `headers` | `dict` | `None` | 请求头 |
| `cookies` | `dict` | `None` | cookies 信息 |
| `files` | `Any` | `None` | 要上传的文件 |
| `auth` | `Any` | `None` | 身份认证信息 |
| `allow_redirects` | `bool` | `True` | 是否允许重定向 |
| `proxies` | `dict` | `None` | 代理信息 |

**返回**: `bool` - 访问是否成功

**示例**:

```python
from DrissionPage import Chromium

tab = Chromium().latest_tab
tab.get('http://DrissionPage.cn')
```

---

## post() 方法

此方法用内置的 `Session` 对象以 POST 方式发送请求。

因为 `post()` 是使用 `requests` 的 `post()` 方法发送请求，参数和用法与 `requests` 一致。

此方法返回请求结果 `Response` 对象。

s 模式时，`post()` 后结果还可用页面对象的 `html` 或 `json` 属性获取。

**返回**: `Response` 对象

---

## 设置超时和重试

网络不稳定时，访问页面不一定成功，`get()` 方法内置了超时和重试功能。

通过 `retry`、`interval`、`timeout` 三个参数进行设置。

```python
from DrissionPage import Chromium

tab = Chromium().latest_tab
tab.get('http://DrissionPage.cn', retry=1, interval=1, timeout=1.5)
```

---

## 加载模式

### 概述

加载模式是指 d 模式下程序在页面加载阶段的行为模式，有以下三种：

- **normal()**: 常规模式，会等待页面加载完毕，超时自动重试或停止，默认使用此模式
- **eager()**: 加载完 DOM 或超时即停止加载，不加载页面资源
- **none()**: 超时也不会自动停止，除非加载完成

前两种模式下，页面加载过程会阻塞程序，直到加载完毕才执行后面的操作。

`none()` 模式下，只在连接阶段阻塞程序，加载阶段可自行根据情况执行 `stop_loading()` 停止加载。

---

### 模式设置

可通过 ini 文件、`ChromiumOptions` 对象和页面对象的 `set.load_mode.****()` 方法进行设置。

**配置对象中设置**:

```python
from DrissionPage import ChromiumOptions, Chromium

co = ChromiumOptions().set_load_mode('none')
browser = Chromium(co)
```

**运行中设置**:

```python
from DrissionPage import Chromium

tab = Chromium().latest_tab
tab.set.load_mode.none()
```

---

### none 模式技巧

**示例 1：配合监听器**

```python
from DrissionPage import Chromium

tab = Chromium().latest_tab
tab.set.load_mode.none()
tab.listen.start('api/getkeydata')
tab.get('http://www.hao123.com/')
packet = tab.listen.wait()
tab.stop_loading()
print(packet.response.body)
```

---

**示例 2：配合元素查找**

```python
from DrissionPage import Chromium

tab = Chromium().latest_tab
tab.set.load_mode.none()
tab.get('http://www.hao123.com/')
ele = tab.ele('中国日报')
tab.stop_loading()
print(ele.text)
```

---

**示例 3：配合页面特征**

```python
from DrissionPage import Chromium

tab = Chromium().latest_tab
tab.set.load_mode.none()
tab.get('http://www.hao123.com/')
tab.wait.title_change('hao123')
tab.stop_loading()
```

---

*文档获取时间: 2026-02-07*
