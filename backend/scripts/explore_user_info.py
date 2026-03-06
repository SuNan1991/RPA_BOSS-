"""
使用 Playwright 探测 BOSS 直聘登录后的用户信息选择器

这个脚本会：
1. 启动浏览器
2. 导航到 BOSS 直聘登录页
3. 等待用户手动扫码登录
4. 登录成功后探测页面结构，找到用户名和头像的正确选择器
5. 生成修复后的代码建议

使用方法:
    cd backend
    python scripts/explore_user_info.py
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path

# 设置输出目录
OUTPUT_DIR = Path(__file__).parent / "exploration_results"
OUTPUT_DIR.mkdir(exist_ok=True)


async def explore_user_info():
    """探测 BOSS 直聘登录后的用户信息"""
    try:
        from playwright.async_api import async_playwright

        print("=" * 70)
        print("   BOSS 直聘用户信息探测脚本")
        print("=" * 70)
        print("\n此脚本将帮助你找到正确的用户信息选择器")
        print("请在浏览器打开后手动扫码登录\n")

        async with async_playwright() as p:
            # 启动浏览器（非无头模式，需要用户交互）
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--lang=zh-CN",
                ]
            )

            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                locale="zh-CN",
                timezone_id="Asia/Shanghai",
            )

            # 注入反检测脚本
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            page = await context.new_page()

            # 导航到登录页
            print("正在导航到 BOSS 直聘登录页...")
            await page.goto("https://login.zhipin.com/", wait_until="networkidle")
            print("✓ 已打开登录页，请使用手机 APP 扫码登录")

            # 等待登录成功（URL 变化）
            print("\n等待登录...")
            max_wait = 300  # 5分钟

            start_time = datetime.now()
            logged_in = False

            while (datetime.now() - start_time).total_seconds() < max_wait:
                current_url = page.url
                if "login.zhipin.com" not in current_url:
                    logged_in = True
                    break
                await asyncio.sleep(2)
                elapsed = (datetime.now() - start_time).total_seconds()
                print(f"\r⏳ 等待中... {int(elapsed)}秒 ", end="", flush=True)

            if not logged_in:
                print("\n\n❌ 登录超时，请重新运行脚本")
                await browser.close()
                return

            print(f"\n\n✓ 登录成功！当前 URL: {page.url}")

            # 等待页面完全加载
            await asyncio.sleep(3)

            # 开始探测用户信息
            print("\n" + "=" * 70)
            print("   开始探测用户信息选择器...")
            print("=" * 70)

            exploration_result = {
                "timestamp": datetime.now().isoformat(),
                "url": page.url,
                "selectors_tested": [],
                "found_selectors": {},
                "recommended_code": None,
            }

            # ==================== 探测用户名选择器 ====================
            print("\n[1] 探测用户名选择器...")

            # 扩展的用户名选择器列表
            username_selectors = [
                # BOSS直聘已知的类名
                ".nav-figure-text",       # 导航栏用户名
                ".info-primary-name",     # 个人中心用户名
                ".user-name",             # 通用用户名
                ".nav-user-name",         # 导航栏用户名变体
                ".username",              # 通用

                # 属性选择器
                "[class*='user-name']",
                "[class*='username']",
                "[class*='userName']",
                "[class*='nav-figure']",

                # 数据属性
                "[data-selector='user-name']",
                "[data-user-name]",
                "[data-name]",

                # 组合选择器
                "header .name",
                ".header .name",
                ".nav .name",
                "nav .name",

                # BOSS直聘特定的导航结构
                ".nav-figure .name",
                ".nav-figure span",
                ".nav-figure a",

                # 个人中心页面
                ".user-info .name",
                ".user-info .username",
                ".info-primary .name",
            ]

            found_username_selectors = []

            for selector in username_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        for el in elements:
                            text = await el.inner_text()
                            is_visible = await el.is_visible()
                            classes = await el.get_attribute("class") or ""

                            # 过滤掉空白文本和过长的文本
                            text = text.strip()
                            if text and is_visible and 1 < len(text) < 30:
                                result = {
                                    "selector": selector,
                                    "text": text,
                                    "class": classes,
                                }
                                found_username_selectors.append(result)
                                print(f"  ✓ 找到: {selector}")
                                print(f"    文本: '{text}'")
                                print(f"    类名: '{classes}'")
                except Exception:
                    pass

            # ==================== 探测头像选择器 ====================
            print("\n[2] 探测头像选择器...")

            avatar_selectors = [
                # BOSS直聘已知的头像类名
                ".nav-figure img",
                ".nav-avatar",
                ".nav-avatar img",
                ".user-avatar img",
                ".figure-box img",

                # 属性选择器
                "[class*='avatar'] img",
                "[class*='user-img']",
                "[class*='figure'] img",

                # 组合选择器
                "header img.avatar",
                "header img[class*='user']",
                ".nav img",
                ".header img",

                # BOSS直聘特定的导航结构
                ".nav-figure-box img",
                ".nav-figure a img",
            ]

            found_avatar_selectors = []

            for selector in avatar_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        for el in elements:
                            src = await el.get_attribute("src")
                            is_visible = await el.is_visible()
                            classes = await el.get_attribute("class") or ""

                            if src and is_visible:
                                # 过滤掉非头像图片
                                if any(x in src.lower() for x in ["avatar", "user", "head", "photo", "face"]):
                                    result = {
                                        "selector": selector,
                                        "src": src,
                                        "class": classes,
                                    }
                                    found_avatar_selectors.append(result)
                                    print(f"  ✓ 找到: {selector}")
                                    print(f"    图片: '{src[:60]}...'")
                except Exception:
                    pass

            # ==================== 使用 JavaScript 深度探测 ====================
            print("\n[3] 通过 JavaScript 深度探测...")

            js_result = await page.evaluate("""
                () => {
                    const results = {
                        navStructure: null,
                        userInfo: {},
                        localStorage: {},
                        possibleUsernameElements: [],
                        possibleAvatarElements: [],
                    };

                    // 获取导航栏结构
                    const nav = document.querySelector('nav, .nav, header, .header');
                    if (nav) {
                        results.navStructure = nav.outerHTML.substring(0, 2000);
                    }

                    // 查找所有可能的用户名元素
                    document.querySelectorAll('span, a, div, p').forEach(el => {
                        const text = (el.innerText || '').trim();
                        const className = el.className || '';

                        // 跳过空文本和过长的文本
                        if (!text || text.length > 30) return;

                        // 检查类名是否包含用户相关关键词
                        const classKeywords = ['user', 'name', 'nav', 'figure', 'username', 'account'];
                        const hasKeyword = classKeywords.some(k =>
                            className.toLowerCase().includes(k)
                        );

                        if (hasKeyword && el.offsetParent !== null) {  // 可见元素
                            results.possibleUsernameElements.push({
                                tag: el.tagName,
                                class: className,
                                text: text,
                                selector: el.id ? `#${el.id}` : `.${className.split(' ')[0]}`,
                            });
                        }
                    });

                    // 查找所有可能的头像元素
                    document.querySelectorAll('img').forEach(img => {
                        const src = img.src || '';
                        const className = img.className || '';

                        if (img.offsetParent !== null && src) {
                            const isAvatar =
                                src.includes('avatar') ||
                                src.includes('user') ||
                                src.includes('head') ||
                                src.includes('photo') ||
                                className.includes('avatar') ||
                                className.includes('user');

                            if (isAvatar) {
                                results.possibleAvatarElements.push({
                                    src: src,
                                    class: className,
                                    selector: className ? `.${className.split(' ')[0]}` : 'img',
                                });
                            }
                        }
                    });

                    // 检查 localStorage
                    for (let i = 0; i < localStorage.length; i++) {
                        const key = localStorage.key(i);
                        if (key && (
                            key.includes('user') ||
                            key.includes('info') ||
                            key.includes('account') ||
                            key.includes('userInfo')
                        )) {
                            try {
                                results.localStorage[key] = JSON.parse(localStorage.getItem(key));
                            } catch {
                                results.localStorage[key] = localStorage.getItem(key);
                            }
                        }
                    }

                    // 尝试从页面获取用户信息
                    // BOSS直聘可能在 window 对象中存储用户信息
                    if (window.__INITIAL_STATE__) {
                        results.userInfo.windowState = window.__INITIAL_STATE__;
                    }
                    if (window.__NUXT__) {
                        results.userInfo.nuxtState = window.__NUXT__;
                    }
                    if (window.pageData) {
                        results.userInfo.pageData = window.pageData;
                    }

                    return results;
                }
            """)

            print(f"\n  可能的用户名元素: {len(js_result.get('possibleUsernameElements', []))} 个")
            for item in js_result.get('possibleUsernameElements', [])[:5]:
                print(f"    <{item['tag']}> class='{item['class'][:30]}' text='{item['text']}'")

            print(f"\n  可能的头像元素: {len(js_result.get('possibleAvatarElements', []))} 个")
            for item in js_result.get('possibleAvatarElements', [])[:5]:
                print(f"    class='{item['class'][:30]}' src='{item['src'][:40]}...'")

            print(f"\n  localStorage 键: {list(js_result.get('localStorage', {}).keys())}")

            # 检查 localStorage 中的用户信息
            local_storage_user_info = js_result.get('localStorage', {})
            if local_storage_user_info:
                print("\n  localStorage 用户信息内容:")
                for key, value in local_storage_user_info.items():
                    print(f"    {key}: {str(value)[:100]}...")

            # ==================== 导航到个人中心页面获取更多信息 ====================
            print("\n[4] 导航到个人中心页面获取更多信息...")

            try:
                await page.goto("https://www.zhipin.com/web/user/", wait_until="networkidle")
                await asyncio.sleep(2)

                # 在个人中心页面再次探测
                personal_page_selectors = [
                    ".info-primary-name",
                    ".info-primary .name",
                    ".user-name",
                    ".user-info .name",
                    "[class*='userName']",
                    "[class*='user-name']",
                ]

                for selector in personal_page_selectors:
                    try:
                        element = await page.query_selector(selector)
                        if element:
                            text = await element.inner_text()
                            is_visible = await element.is_visible()
                            if text and is_visible:
                                text = text.strip()
                                if 1 < len(text) < 30:
                                    print(f"  ✓ 个人中心找到: {selector} -> '{text}'")
                                    found_username_selectors.append({
                                        "selector": selector,
                                        "text": text,
                                        "page": "personal_center",
                                    })
                    except Exception:
                        pass

            except Exception as e:
                print(f"  导航到个人中心失败: {e}")

            # ==================== 生成推荐代码 ====================
            print("\n" + "=" * 70)
            print("   生成推荐的修复代码")
            print("=" * 70)

            # 选择最佳的选择器
            best_username_selector = None
            best_avatar_selector = None

            if found_username_selectors:
                # 优先选择 BOSS直聘特有的类名
                for item in found_username_selectors:
                    if "nav-figure" in item.get("selector", ""):
                        best_username_selector = item["selector"]
                        break
                if not best_username_selector:
                    best_username_selector = found_username_selectors[0]["selector"]

            if found_avatar_selectors:
                best_avatar_selector = found_avatar_selectors[0]["selector"]

            # 生成代码
            recommended_code = generate_fix_code(
                best_username_selector,
                best_avatar_selector,
                found_username_selectors,
                found_avatar_selectors,
                js_result
            )

            print("\n" + recommended_code)

            # 保存结果
            exploration_result["found_selectors"] = {
                "username": found_username_selectors,
                "avatar": found_avatar_selectors,
            }
            exploration_result["recommended_code"] = recommended_code
            exploration_result["js_result"] = js_result

            output_file = OUTPUT_DIR / f"exploration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(exploration_result, f, ensure_ascii=False, indent=2, default=str)

            print(f"\n\n✓ 探测结果已保存到: {output_file}")

            # 总结
            print("\n" + "=" * 70)
            print("   探测总结")
            print("=" * 70)

            if best_username_selector:
                print(f"\n✅ 推荐的用户名选择器: {best_username_selector}")
            else:
                print("\n❌ 未找到用户名选择器")

            if best_avatar_selector:
                print(f"\n✅ 推荐的头像选择器: {best_avatar_selector}")
            else:
                print("\n❌ 未找到头像选择器")

            # 等待用户确认
            print("\n\n按 Enter 关闭浏览器...")
            input()

            await browser.close()

            return exploration_result

    except ImportError:
        print("错误: 未安装 playwright")
        print("\n请运行以下命令安装:")
        print("  pip install playwright")
        print("  python -m playwright install chromium")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


def generate_fix_code(username_selector, avatar_selector, username_results, avatar_results, js_result):
    """生成修复代码"""

    code = '''
# ==================== 推荐的 extract_user_info 修复代码 ====================
# 将以下代码替换到 backend/app/services/rpa_service.py 中的 extract_user_info 方法

def extract_user_info(self, browser) -> Optional[dict[str, Any]]:
    """
    从页面提取用户信息

    Returns:
        dict with user info or None
    """
    try:
        user_info = {}

        # ==================== 提取用户名 ====================
        # 优先级顺序的选择器列表
'''

    if username_selector:
        code += f"        # 首选选择器（探测发现）\n"
        code += f"        primary_username_selector = \"{username_selector}\"\n\n"

    code += '''        username_selectors = [
'''

    # 添加探测到的选择器
    seen_selectors = set()
    for item in username_results:
        sel = item.get("selector", "")
        if sel and sel not in seen_selectors:
            code += f'            "{sel}",  # {item.get("text", "")}\n'
            seen_selectors.add(sel)

    # 添加备选选择器
    code += '''            # 备选选择器
            ".nav-figure-text",
            ".info-primary-name",
            ".user-name",
            ".nav-user-name",
            "[class*='user-name']",
            "[class*='username']",
        ]

        for selector in username_selectors:
            try:
                element = browser.find(selector)
                if element:
                    text = element.text.strip()
                    if text and 1 < len(text) < 30:  # 合理的用户名长度
                        user_info["username"] = text
                        logger.info(f"提取到用户名: {text} (选择器: {selector})")
                        break
            except Exception:
                continue

        # ==================== 提取头像 ====================
'''

    if avatar_selector:
        code += f"        # 首选头像选择器（探测发现）\n"
        code += f"        primary_avatar_selector = \"{avatar_selector}\"\n\n"

    code += '''        avatar_selectors = [
'''

    # 添加探测到的头像选择器
    seen_avatar = set()
    for item in avatar_results:
        sel = item.get("selector", "")
        if sel and sel not in seen_avatar:
            code += f'            "{sel}",\n'
            seen_avatar.add(sel)

    code += '''            # 备选选择器
            ".nav-figure img",
            ".nav-avatar img",
            ".user-avatar img",
            "[class*='avatar'] img",
        ]

        for selector in avatar_selectors:
            try:
                element = browser.find(selector)
                if element:
                    src = element.attr("src")
                    if src:
                        user_info["avatar"] = src
                        logger.info(f"提取到头像: {src[:50]}...")
                        break
            except Exception:
                continue

        # ==================== 尝试从 localStorage/API 获取更多信息 ====================
        try:
            # 使用 JavaScript 获取 localStorage 中的用户信息
            js_result = browser.run_js("""
                () => {
                    const result = {};

                    // 检查 localStorage
                    for (let i = 0; i < localStorage.length; i++) {
                        const key = localStorage.key(i);
                        if (key && (
                            key.includes('user') ||
                            key.includes('info') ||
                            key.includes('userInfo')
                        )) {
                            try {
                                result[key] = JSON.parse(localStorage.getItem(key));
                            } catch {
                                result[key] = localStorage.getItem(key);
                            }
                        }
                    }

                    // 检查 window 对象
                    if (window.__INITIAL_STATE__) {
                        result.windowState = window.__INITIAL_STATE__;
                    }

                    return result;
                }
            """)

            if js_result:
                # 从 localStorage 或 window 对象中提取用户信息
                for key, value in js_result.items():
                    if isinstance(value, dict):
                        # 尝试提取用户名
                        if not user_info.get("username"):
                            for name_key in ["name", "username", "nickname", "realName"]:
                                if value.get(name_key):
                                    user_info["username"] = value[name_key]
                                    break

                        # 尝试提取头像
                        if not user_info.get("avatar"):
                            for avatar_key in ["avatar", "avatarUrl", "headImg", "photo"]:
                                if value.get(avatar_key):
                                    user_info["avatar"] = value[avatar_key]
                                    break

                logger.debug(f"从 JavaScript 获取到额外信息: {list(js_result.keys())}")

        except Exception as e:
            logger.debug(f"JavaScript 获取用户信息失败: {e}")

        # ==================== 验证结果 ====================
        if user_info:
            logger.info(f"成功提取用户信息: {user_info}")
            return user_info
        else:
            logger.warning("未能提取到任何用户信息")
            return None

    except Exception as e:
        logger.error(f"提取用户信息失败: {e}")
        return None

# ==================== 错误原因分析 ====================
'''

    # 添加错误分析
    code += '''
## 原代码的错误原因:

1. **选择器过时或不正确**
   - 原代码使用的选择器可能是旧版本页面的选择器
   - BOSS直聘的页面结构可能已经更新

2. **没有足够的备选选择器**
   - 只尝试了几个选择器，没有覆盖所有可能的情况
   - 应该按照优先级尝试多个选择器

3. **没有使用 JavaScript 获取额外信息**
   - 很多网站会在 localStorage 或 window 对象中存储用户信息
   - 忽略了这个重要的信息来源

4. **没有日志记录**
   - 找不到元素时没有记录日志，难以调试
   - 应该记录每个选择器的尝试结果

5. **过早返回 None**
   - 一旦一个选择器失败就放弃
   - 应该尝试所有可能的选择器

## 避免此类错误的原则:

1. **永远不要假设选择器永远有效**
   - 网站会更新，选择器会失效
   - 总是准备多个备选选择器

2. **使用多种方式获取数据**
   - CSS 选择器
   - XPath
   - JavaScript 执行
   - API 请求拦截

3. **添加详细的日志**
   - 记录每个选择器的尝试结果
   - 记录成功获取的数据

4. **优先级策略**
   - 先尝试最可靠的选择器
   - 然后尝试备选方案
   - 最后使用通用方法
'''

    return code


if __name__ == "__main__":
    asyncio.run(explore_user_info())
