# DrissionPage 官方文档

本目录包含 DrissionPage 官方文档的离线版本，方便开发时快速查阅。

**来源**: https://drissionpage.cn/

**文档版本**: 4.1.1.2

**下载时间**: 2026-02-07

---

## 📚 文档目录

### 入门指南

- **[01_浏览器控制概述](./01_浏览器控制概述.md)** - 操作浏览器的基本逻辑和核心对象
  - 基本逻辑（5步操作流程）
  - 浏览器对象 (Chromium)
  - 标签页对象 (Tab)
  - 元素对象 (ChromiumElement)

- **[02_连接浏览器](./02_连接浏览器.md)** - Chromium 对象的使用详解
  - 直接创建浏览器
  - 通过配置信息创建
  - 接管已打开的浏览器
  - 多浏览器共存
  - 用户文件夹管理

- **[03_准备工作](./03_准备工作.md)** - 首次使用前的配置
  - 尝试启动浏览器
  - 设置浏览器路径
  - 配置验证

- **[04_基本概念](./04_基本概念.md)** - DrissionPage 核心概念
  - 网页自动化两种模式
  - 主要对象类型
  - ChromiumPage、SessionPage、WebPage
  - d 模式和 s 模式
  - 工作模式切换

### 进阶配置

- **[05_浏览器启动设置](./05_浏览器启动设置.md)** - ChromiumOptions 详解
  - 命令行参数设置
  - 运行路径及端口配置
  - 插件管理
  - 用户文件设置
  - 运行参数设置
  - 其他常用设置

- **[06_配置文件的使用](./06_配置文件的使用.md)** - ini 配置文件管理
  - 配置文件结构
  - 配置节说明
  - 读取和保存配置

---

## 🚀 快速开始

### 安装

```bash
pip install DrissionPage
```

### 基本使用

```python
from DrissionPage import ChromiumPage

# 创建页面对象
page = ChromiumPage()

# 访问网页
page.get('https://www.baidu.com')

# 查找元素并操作
page.ele('#kw').input('DrissionPage')
page.ele('@value=百度一下').click()
```

---

## 📖 核心概念

### 三种页面对象

1. **ChromiumPage** - 纯浏览器控制
2. **SessionPage** - 纯数据包收发
3. **WebPage** - 浏览器 + 数据包（双模式）

### 两种工作模式

- **d 模式 (Driver)** - 控制浏览器，功能强大但速度慢
- **s 模式 (Session)** - 收发数据包，速度快但功能受限

### 对象关系

```
ChromiumPage → ChromiumTab → ChromiumElement
SessionPage → SessionElement
WebPage → (ChromiumTab / SessionElement)
```

---

## 💡 常用操作

### 浏览器操作

```python
# 启动浏览器
browser = Chromium()

# 访问网址
tab.get('https://example.com')

# 新建标签页
new_tab = browser.new_tab('https://example.com')

# 获取标签页
tab = browser.latest_tab
```

### 元素查找

```python
# 通过ID查找
ele = page.ele('#id')

# 通过class查找
ele = page.ele('.class')

# 通过文本查找
ele = page.ele('text=文本内容')

# 通过xpath查找
ele = page.ele('xpath://div[@class="item"]')

# 查找多个元素
elements = page.eles('.item')
```

### 元素操作

```python
# 点击
ele.click()

# 输入文本
ele.input('文本')

# 获取属性
attr = ele.attr('class')

# 获取文本
text = ele.text

# 获取HTML
html = ele.html
```

---

## 🔗 相关链接

- **官方网站**: https://drissionpage.cn/
- **GitHub**: https://github.com/g1879/DrissionPage
- **Gitee**: https://gitee.com/g1879/DrissionPage
- **QQ群**: 391178600

---

## 📝 使用技巧

1. **首次使用**需要配置浏览器路径，参见 [准备工作](./03_准备工作.md)
2. **快速开发**使用 WebPage 实现 d 模式和 s 模式切换
3. **性能优化**使用 s 模式处理大量数据，d 模式处理复杂交互
4. **配置管理**使用 ini 文件管理不同项目的配置
5. **多浏览器**使用 auto_port() 或设置不同端口避免冲突

---

**注意**: 本文档为离线版本，最新内容请访问官方文档网站。
