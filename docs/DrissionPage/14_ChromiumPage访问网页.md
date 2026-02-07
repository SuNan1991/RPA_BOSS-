# ChromiumPage 访问网页

来源: https://drissionpage.cn/dp40docs/ChromiumPage/visit

`ChromiumPage` 对象和 `WebPage` 对象的 d 模式都能控制浏览器访问网页。

---

## get() 方法

该方法用于跳转到一个网址。当连接失败时，程序会进行重试。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `url` | `str` | 必填 | 目标 url，可指向本地文件路径 |
| `show_errmsg` | `bool` | `False` | 连接出错时是否显示和抛出异常 |
| `retry` | `int` | `None` | 重试次数，为 `None` 时使用页面参数，默认 3 |
| `interval` | `float` | `None` | 重试间隔（秒），为 `None` 时使用页面参数，默认 2 |
| `timeout` | `float` | `None` | 加载超时时间（秒） |

**返回类型**: `bool` - 是否连接成功

**示例**:

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.get('https://www.baidu.com')
```

---

## 设置超时和重试

网络不稳定时，访问页面不一定成功，`get()` 方法内置了超时和重试功能。

通过 `retry`、`interval`、`timeout` 三个参数进行设置。

如不指定 `timeout` 参数，该参数会使用 `ChromiumPage` 的 `timeouts` 属性的 `page_load` 参数中的值。

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.get('https://DrissionPage.cn', retry=1, interval=1, timeout=1.5)
```

---

## 加载模式

### 概述

加载模式是指程序在页面加载阶段的行为模式，有以下三种：

- **normal()**: 常规模式，会等待页面加载完毕，超时自动重试或停止，默认使用此模式
- **eager()**: 加载完 DOM 或超时即停止加载，不加载页面资源
- **none()**: 超时也不会自动停止，除非加载完成

前两种模式下，页面加载过程会阻塞程序，直到加载完毕才执行后面的操作。

`none()` 模式下，只在连接阶段阻塞程序，加载阶段可自行根据情况执行 `stop_loading()` 停止加载。

这样可以提供给用户非常大的自由度，可等到关键数据包或元素出现就主动停止页面加载，大幅提升执行效率。

**注意**:
- 加载完成是指主文档完成，并不包括由 js 触发的加载和重定向的加载
- 当文档加载完成，程序就判断加载完毕，此后发生的重定向或 js 加载数据需用其它逻辑处理

---

### 模式设置

可通过 ini 文件、`ChromiumOptions` 对象和页面对象的 `set.load_mode.****()` 方法进行设置。

运行时可随时动态设置。

**配置对象中设置**:

```python
from DrissionPage import ChromiumOptions, ChromiumPage

co = ChromiumOptions().set_load_mode('none')
page = ChromiumPage(co)
```

**运行中设置**:

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.set.load_mode.none()
```

---

### none 模式技巧

**示例 1：配合监听器**

跟监听器配合，可在获取到需要的数据包时，主动停止加载。

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.set.load_mode.none()  # 设置加载模式为none
page.listen.start('api/getkeydata')  # 指定监听目标并启动监听
page.get('http://www.hao123.com/')  # 访问网站
packet = page.listen.wait()  # 等待数据包
page.stop_loading()  # 主动停止加载
print(packet.response.body)  # 打印数据包正文
```

---

**示例 2：配合元素查找**

跟元素查找配合，可在获取到某个指定元素时，主动停止加载。

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.set.load_mode.none()  # 设置加载模式为none
page.get('http://www.hao123.com/')  # 访问网站
ele = page.ele('中国日报')  # 查找text包含"中国日报"的元素
page.stop_loading()  # 主动停止加载
print(ele.text)  # 打印元素text
```

---

**示例 3：配合页面特征**

可等待到页面到达某种状态时，主动停止加载。比如多级跳转的登录，可等待 title 变化到最终目标网址时停止。

```python
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.set.load_mode.none()  # 设置加载模式为none
page.get('http://www.hao123.com/')  # 访问网站
page.wait.title_change('hao123')  # 等待title变化出现目标文本
page.stop_loading()  # 主动停止加载
```

---

*文档获取时间: 2026-02-07*
