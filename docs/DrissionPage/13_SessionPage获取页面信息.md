# SessionPage 获取页面信息

来源: https://drissionpage.cn/dp40docs/SessionPage/get_page_info

成功访问网页后，可使用 `SessionPage` 自身属性和方法获取页面信息。

---

## 基本属性

```python
from DrissionPage import SessionPage

page = SessionPage()
page.get('http://www.baidu.com')

# 获取页面标题
print(page.title)

# 获取页面html
print(page.html)
```

**输出**:
```
百度一下，你就知道
```

---

## 常用属性和方法

### 页面内容属性

- `page.html` - 页面 HTML 内容
- `page.title` - 页面标题
- `page.url` - 当前页面 URL
- `page.json` - JSON 响应数据（如果响应是 JSON）

### 响应信息

- `page.response` - Response 对象
- `page.status_code` - HTTP 状态码
- `page.cookies` - Cookies
- `page.headers` - 响应头

### Session 相关

- `page.session` - 内置的 Session 对象
- `page.session_options` - Session 配置对象

---

## 使用示例

### 获取页面 HTML

```python
from DrissionPage import SessionPage

page = SessionPage()
page.get('https://www.example.com')

# 获取完整 HTML
html = page.html
print(html)
```

### 获取 JSON 数据

```python
from DrissionPage import SessionPage

page = SessionPage()
page.get('https://api.example.com/data')

# 获取 JSON 响应
data = page.json
print(data)
```

### 获取响应信息

```python
from DrissionPage import SessionPage

page = SessionPage()
page.get('https://www.example.com')

# 获取状态码
print(f"状态码: {page.status_code}")

# 获取 cookies
print(f"Cookies: {page.cookies}")

# 获取响应头
print(f"响应头: {page.headers}")
```

---

*文档获取时间: 2026-02-07*
