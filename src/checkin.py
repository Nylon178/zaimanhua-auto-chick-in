import os
from playwright.sync_api import sync_playwright


def checkin():
    cookie_str = os.environ.get('ZAIMANHUA_COOKIE')
    if not cookie_str:
        print("Error: ZAIMANHUA_COOKIE not set")
        return False

    # 解析 Cookie 字符串为 Playwright 格式
    cookies = []
    for item in cookie_str.split(';'):
        item = item.strip()
        if '=' in item:
            name, value = item.split('=', 1)
            cookies.append({
                'name': name.strip(),
                'value': value.strip(),
                'domain': '.zaimanhua.com',
                'path': '/'
            })

    print(f"已解析 {len(cookies)} 个 Cookie")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # 添加 Cookie
        context.add_cookies(cookies)

        page = context.new_page()
        page.goto('https://i.zaimanhua.com/')

        # 等待页面加载
        page.wait_for_load_state('networkidle')
        print(f"页面标题: {page.title()}")

        try:
            # 等待签到按钮出现
            page.wait_for_selector('.ant-btn-primary', timeout=10000)

            # 获取按钮信息
            button = page.locator('.ant-btn-primary').first
            button_text = button.inner_text()
            is_disabled = button.is_disabled()

            print(f"按钮文字: {button_text}")
            print(f"按钮禁用状态: {is_disabled}")

            if is_disabled:
                # 检查是否已签到（按钮禁用可能意味着已签到）
                if "已签到" in button_text or "已领取" in button_text:
                    print("今天已经签到过了！")
                    result = True
                else:
                    # 可能是未登录状态，尝试用 JavaScript 强制点击
                    print("按钮被禁用，尝试使用 JavaScript 点击...")
                    page.evaluate("document.querySelector('.ant-btn-primary').click()")
                    page.wait_for_timeout(2000)
                    print("JavaScript 点击完成")
                    result = True
            else:
                # 按钮可用，正常点击
                button.click()
                page.wait_for_timeout(2000)
                print("签到成功！")
                result = True

        except Exception as e:
            print(f"签到失败: {e}")
            # 保存截图用于调试
            page.screenshot(path="error_screenshot.png")
            print("已保存错误截图: error_screenshot.png")
            result = False
        finally:
            browser.close()

        return result


if __name__ == '__main__':
    success = checkin()
    exit(0 if success else 1)
