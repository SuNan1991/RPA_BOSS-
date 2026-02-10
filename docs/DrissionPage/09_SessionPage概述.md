# SessionPage 概述

来源: https://drissionpage.cn/dp40docs/SessionPage/intro

`SessionPage` 对象和 `WebPage` 对象的 s 模式，可用收发数据包的形式访问网页。

---

## 简介

顾名思义，`SessionPage` 是一个使用 `Session`（requests 库）对象的页面，它使用 POM 模式封装了网络连接和 html 解析功能，使收发数据包也可以像操作页面一样便利。

并且，由于加入了本库独创的查找元素方法，使数据的采集便利性远超 requests + beautifulsoup 等组合。

`SessionPage` 是本库几种页面对象中最简单的。

---

## 工作方式示例

获取 gitee 推荐项目第一页所有项目：

```python
# 导入
from DrissionPage import SessionPage

# 创建页面对象
page = SessionPage()

# 访问网页
page.get('https://gitee.com/explore/all')

# 在页面中查找元素
items = page.eles('t:h3')

# 遍历元素
for item in items[:-1]:
    # 获取当前元素下的元素
    lnk = item('tag:a')
    # 打印元素文本和href属性
    print(lnk.text, lnk.link)
```

**输出**:
```
七年觐汐/wx-calendar https://gitee.com/qq_connect-EC6BCC0B556624342/wx-calendar
ThingsPanel/thingspanel-go https://gitee.com/ThingsPanel/thingspanel-go
APITable/APITable https://gitee.com/apitable/APITable
Indexea/ideaseg https://gitee.com/indexea/ideaseg
CcSimple/vue-plugin-hiprint https://gitee.com/CcSimple/vue-plugin-hiprint
william_lzw/ExDUIR.NET https://gitee.com/william_lzw/ExDUIR.NET
anolis/ancert https://gitee.com/anolis/ancert
cozodb/cozo https://gitee.com/cozodb/cozo
后面省略...
```

---

## SessionPage vs ChromiumPage

### SessionPage 特点

- ✅ 速度快，效率高
- ✅ 资源占用少
- ✅ 适合数据采集
- ❌ 不能执行 JavaScript
- ❌ 不能处理复杂的交互

### ChromiumPage 特点

- ✅ 功能强大
- ✅ 可以执行 JavaScript
- ✅ 可以处理复杂交互
- ❌ 速度慢
- ❌ 资源占用多

---

## 使用场景

### 适合使用 SessionPage 的场景

1. 纯数据采集
2. API 调用
3. 简单表单提交
4. 不需要 JavaScript 的场景
5. 需要高性能、高并发的场景

### 适合使用 ChromiumPage 的场景

1. 需要执行 JavaScript
2. 复杂的页面交互
3. 需要模拟真实用户行为
4. 处理验证码、加密等

---

*文档获取时间: 2026-02-07*
