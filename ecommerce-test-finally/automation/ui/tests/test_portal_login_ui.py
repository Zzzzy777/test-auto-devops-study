"""
商城前台登录 UI 自动化测试。

测试页面：
http://localhost:8060/#/pages/public/login

商城前台账号：
用户名：test
密码：123456

测试场景：
1. 正确账号密码登录成功；
2. 错误密码登录失败；
3. 用户名为空登录失败；
4. 密码为空登录失败；
5. 用户名和密码都为空登录失败；
6. 登录页面元素完整性校验。

技术：
- Python
- pytest
- Playwright
- Allure
"""

from pathlib import Path

import allure
import pytest
from playwright.sync_api import Page, expect


# ============================================================
# 基础配置
# ============================================================

# 商城前台登录页面地址
LOGIN_URL = "http://localhost:8060/#/pages/public/login"

# 商城前台首页地址
HOME_URL = "http://localhost:8060/#/"

# 正确的商城用户名
PORTAL_USERNAME = "test"

# 正确的商城密码
PORTAL_PASSWORD = "123456"

# 错误密码，仅用于失败场景
WRONG_PASSWORD = "wrong_password"

# 截图目录
SCREENSHOT_DIR = Path("screenshots")


# ============================================================
# 公共方法
# ============================================================

def open_login_page(page: Page) -> None:
    """
    打开商城前台登录页面。

    参数：
        page：Playwright 页面对象
    """

    # 设置 Playwright 默认操作超时时间
    page.set_default_timeout(15000)

    # 确保截图目录存在
    SCREENSHOT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # 打开商城真实登录页面
    page.goto(
        LOGIN_URL,
        wait_until="domcontentloaded",
    )

    # 等待 uni-app 登录页面加载完成
    login_page = page.locator(
        "uni-page[data-page='pages/public/login']"
    )

    login_page.wait_for(
        state="visible",
        timeout=15000,
    )

    # 等待登录页面元素稳定
    page.wait_for_timeout(800)


def get_login_page(page: Page):
    """
    获取登录页面主体元素。
    """

    return page.locator(
        "uni-page[data-page='pages/public/login']"
    )


def get_username_input(page: Page):
    """
    获取用户名输入框。

    uni-app H5 页面最终会渲染为：

    <input type="text">
    """

    return page.locator(
        "uni-page[data-page='pages/public/login'] "
        "input[type='text']"
    )


def get_password_input(page: Page):
    """
    获取密码输入框。

    uni-app H5 页面最终会渲染为：

    <input type="password">
    """

    return page.locator(
        "uni-page[data-page='pages/public/login'] "
        "input[type='password']"
    )


def get_login_button(page: Page):
    """
    获取登录按钮。

    登录页面源码：

    <button class="confirm-btn" @click="toLogin">
        登录
    </button>

    uni-app H5 页面最终渲染为：

    <uni-button class="confirm-btn">
        登录
    </uni-button>
    """

    return page.locator(
        "uni-page[data-page='pages/public/login'] "
        "uni-button.confirm-btn"
    )


def get_experience_button(page: Page):
    """
    获取获取体验账号按钮。
    """

    return page.locator(
        "uni-page[data-page='pages/public/login'] "
        "uni-button.confirm-btn2"
    )


def get_username_placeholder(page: Page):
    """
    获取用户名输入框的 placeholder。

    实际 DOM 结构：

    <uni-input>
        <div class="uni-input-wrapper">
            <div class="uni-input-placeholder">
                请输入用户名
            </div>
            <input type="text">
        </div>
    </uni-input>

    注意：
    placeholder 不是 uni-input 的普通文本，
    需要先定位 input 的父节点，再定位
    .uni-input-placeholder。
    """

    username_input = get_username_input(page)

    return username_input.locator(
        "xpath=.."
    ).locator(
        ".uni-input-placeholder"
    )


def get_password_placeholder(page: Page):
    """
    获取密码输入框的 placeholder。
    """

    password_input = get_password_input(page)

    return password_input.locator(
        "xpath=.."
    ).locator(
        ".uni-input-placeholder"
    )


def fill_login_form(
    page: Page,
    username: str,
    password: str,
) -> None:
    """
    填写登录表单。

    参数：
        page：Playwright 页面对象；
        username：用户名；
        password：密码。
    """

    # 获取用户名输入框
    username_input = get_username_input(page)

    # 获取密码输入框
    password_input = get_password_input(page)

    # 校验输入框可见
    expect(username_input).to_be_visible()
    expect(password_input).to_be_visible()

    # 填写用户名
    username_input.fill(username)

    # 填写密码
    password_input.fill(password)

    # 校验填写结果
    expect(username_input).to_have_value(username)
    expect(password_input).to_have_value(password)


def parse_response_json(response) -> dict:
    """
    尝试解析接口响应 JSON。

    某些异常场景下后端可能返回非 JSON 内容，
    因此这里使用 try-except 进行兼容处理。

    参数：
        response：Playwright Response 对象。

    返回：
        dict：接口响应字典；
        解析失败时返回空字典。
    """

    try:
        result = response.json()

        if isinstance(result, dict):
            return result

        return {}

    except Exception:
        return {}


def assert_login_page_stays_open(page: Page) -> None:
    """
    校验登录失败后仍然停留在登录页面。
    """

    # 失败场景不能跳转到其他页面
    assert "pages/public/login" in page.url, (
        "登录失败后不应该跳转到其他页面，"
        f"当前地址为：{page.url}"
    )

    # 失败场景不能跳转到商城首页
    assert page.url != HOME_URL, (
        "登录失败后不应该跳转到商城首页"
    )


def save_screenshot(
    page: Page,
    file_name: str,
) -> None:
    """
    保存页面截图。

    参数：
        page：Playwright 页面对象；
        file_name：截图文件名。
    """

    SCREENSHOT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    page.screenshot(
        path=str(
            SCREENSHOT_DIR / file_name
        ),
        full_page=True,
    )


# ============================================================
# 测试用例 1：正确账号密码登录成功
# ============================================================

@pytest.mark.smoke
@pytest.mark.login
@allure.epic("商城前台 UI 自动化测试")
@allure.feature("用户登录模块")
@allure.story("正确账号密码登录成功")
@allure.title("商城用户使用正确账号密码登录成功")
def test_portal_login_success(page: Page):
    """
    验证商城用户使用正确账号密码登录成功。

    测试步骤：
    1. 打开登录页面；
    2. 输入正确用户名；
    3. 输入正确密码；
    4. 点击登录按钮；
    5. 校验登录接口；
    6. 校验返回 token；
    7. 校验跳转到商城首页。
    """

    # 打开商城登录页面
    with allure.step("打开商城前台登录页面"):
        open_login_page(page)

        # 校验页面标题
        expect(page).to_have_title("登录")

        # 输出页面信息
        print("登录页面地址：", page.url)
        print("登录页面标题：", page.title())

        # 保存登录前截图
        save_screenshot(
            page,
            "portal-login-success-before.png",
        )

    # 填写正确账号密码
    with allure.step("填写正确的商城账号和密码"):
        fill_login_form(
            page=page,
            username=PORTAL_USERNAME,
            password=PORTAL_PASSWORD,
        )

    # 点击登录按钮并监听登录接口
    with allure.step("点击登录按钮"):
        login_button = get_login_button(page)

        # 校验登录按钮可见并且可用
        expect(login_button).to_be_visible()
        expect(login_button).to_be_enabled()

        # 监听真实登录接口
        with page.expect_response(
            lambda response: (
                "/sso/login" in response.url
                and response.request.method == "POST"
            ),
            timeout=15000,
        ) as response_info:

            # 点击登录按钮
            login_button.click()

    # 获取登录接口响应
    login_response = response_info.value

    # 输出接口基本信息
    print("登录接口地址：", login_response.url)
    print("登录接口状态码：", login_response.status)

    # HTTP 状态码应该为 200
    assert login_response.status == 200, (
        "登录接口请求失败，"
        f"HTTP 状态码为：{login_response.status}"
    )

    # 解析接口响应
    login_result = parse_response_json(login_response)

    # 输出接口响应
    print("登录接口响应：", login_result)

    # 业务状态码应该为 200
    assert login_result.get("code") == 200, (
        "登录业务失败，"
        f"实际响应为：{login_result}"
    )

    # 登录成功后应该返回 token
    login_data = login_result.get("data") or {}

    assert login_data.get("token"), (
        "登录成功但没有返回 token，"
        f"实际响应为：{login_result}"
    )

    # 等待前端保存 token 并跳转
    with allure.step("等待登录成功后跳转到商城首页"):
        page.wait_for_timeout(2500)

        print("登录成功后的页面地址：", page.url)

    # 保存登录成功截图
    save_screenshot(
        page,
        "portal-login-success-after.png",
    )

    # 登录成功后应该进入商城首页
    assert "#/" in page.url, (
        "登录成功后没有跳转到商城首页，"
        f"当前地址为：{page.url}"
    )

    # 不应该仍然停留在登录页面
    assert "pages/public/login" not in page.url, (
        "登录成功后仍然停留在登录页面，"
        f"当前地址为：{page.url}"
    )

    # 首页正文不能为空
    assert page.locator("body").inner_text().strip(), (
        "登录成功后商城首页没有页面内容"
    )


# ============================================================
# 测试用例 2：错误密码登录失败
# ============================================================

@pytest.mark.login
@allure.epic("商城前台 UI 自动化测试")
@allure.feature("用户登录模块")
@allure.story("错误密码登录失败")
@allure.title("商城用户使用错误密码登录失败")
def test_portal_login_wrong_password(page: Page):
    """
    验证错误密码不能登录成功。
    """

    # 打开登录页面
    with allure.step("打开商城前台登录页面"):
        open_login_page(page)

        # 校验页面标题
        expect(page).to_have_title("登录")

        # 保存测试前截图
        save_screenshot(
            page,
            "portal-login-wrong-before.png",
        )

    # 输入正确用户名和错误密码
    with allure.step("输入正确用户名和错误密码"):
        fill_login_form(
            page=page,
            username=PORTAL_USERNAME,
            password=WRONG_PASSWORD,
        )

    # 点击登录按钮并监听接口
    with allure.step("点击登录按钮"):
        login_button = get_login_button(page)

        with page.expect_response(
            lambda response: (
                "/sso/login" in response.url
                and response.request.method == "POST"
            ),
            timeout=15000,
        ) as response_info:

            login_button.click()

    # 获取接口响应
    login_response = response_info.value

    # 解析接口响应
    login_result = parse_response_json(login_response)

    # 输出接口信息
    print(
        "错误密码登录接口地址：",
        login_response.url,
    )
    print(
        "错误密码登录状态码：",
        login_response.status,
    )
    print(
        "错误密码登录响应：",
        login_result,
    )

    # 错误密码不能登录成功
    if login_response.status == 200:
        # 如果 HTTP 为 200，则校验业务 code 不是 200
        assert login_result.get("code") != 200, (
            "错误密码登录不应该成功，"
            f"实际响应为：{login_result}"
        )
    else:
        # 非 200 状态码也必须是常见失败状态
        assert login_response.status in [
            400,
            401,
            403,
            500,
        ], (
            "错误密码返回了未预期的状态码："
            f"{login_response.status}"
        )

    # 等待失败提示出现
    page.wait_for_timeout(1000)

    # 保存失败截图
    save_screenshot(
        page,
        "portal-login-wrong-after.png",
    )

    # 校验页面仍然停留在登录页
    assert_login_page_stays_open(page)

    # 登录页面控件仍然存在
    expect(get_username_input(page)).to_be_visible()
    expect(get_password_input(page)).to_be_visible()
    expect(get_login_button(page)).to_be_visible()


# ============================================================
# 测试用例 3：用户名为空登录失败
# ============================================================

@pytest.mark.login
@allure.epic("商城前台 UI 自动化测试")
@allure.feature("用户登录模块")
@allure.story("用户名为空登录失败")
@allure.title("用户名为空时不能登录")
def test_portal_login_empty_username(page: Page):
    """
    验证用户名为空时不能登录。

    说明：
    用户名或密码为空时，前端会直接进行校验，
    不会调用后端 /sso/login 接口。
    """

    # 打开登录页面
    with allure.step("打开商城前台登录页面"):
        open_login_page(page)

        expect(page).to_have_title("登录")

    # 获取页面元素
    username_input = get_username_input(page)
    password_input = get_password_input(page)
    login_button = get_login_button(page)

    # 清空用户名
    with allure.step("清空用户名输入框"):
        username_input.fill("")

        expect(username_input).to_have_value("")

    # 输入正确密码
    with allure.step("输入正确密码"):
        password_input.fill(PORTAL_PASSWORD)

        expect(password_input).to_have_value(
            PORTAL_PASSWORD
        )

    # 点击登录按钮
    with allure.step("点击登录按钮"):
        login_button.click()

    # 等待前端提示
    page.wait_for_timeout(800)

    # 获取页面文本
    page_text = page.locator("body").inner_text()

    print(
        "用户名为空时页面文本：",
        page_text,
    )

    # 校验前端提示
    assert "请输入用户名和密码" in page_text, (
        "用户名为空时没有显示正确的提示信息"
    )

    # 保存截图
    save_screenshot(
        page,
        "portal-login-empty-username.png",
    )

    # 校验页面没有跳转
    assert_login_page_stays_open(page)

    # 校验登录控件仍然存在
    expect(username_input).to_be_visible()
    expect(password_input).to_be_visible()
    expect(login_button).to_be_visible()


# ============================================================
# 测试用例 4：密码为空登录失败
# ============================================================

@pytest.mark.login
@allure.epic("商城前台 UI 自动化测试")
@allure.feature("用户登录模块")
@allure.story("密码为空登录失败")
@allure.title("密码为空时不能登录")
def test_portal_login_empty_password(page: Page):
    """
    验证密码为空时不能登录。
    """

    # 打开登录页面
    with allure.step("打开商城前台登录页面"):
        open_login_page(page)

        expect(page).to_have_title("登录")

    # 获取页面元素
    username_input = get_username_input(page)
    password_input = get_password_input(page)
    login_button = get_login_button(page)

    # 输入正确用户名
    with allure.step("输入正确用户名"):
        username_input.fill(PORTAL_USERNAME)

        expect(username_input).to_have_value(
            PORTAL_USERNAME
        )

    # 清空密码
    with allure.step("清空密码输入框"):
        password_input.fill("")

        expect(password_input).to_have_value("")

    # 点击登录按钮
    with allure.step("点击登录按钮"):
        login_button.click()

    # 等待前端提示
    page.wait_for_timeout(800)

    # 获取页面文本
    page_text = page.locator("body").inner_text()

    print(
        "密码为空时页面文本：",
        page_text,
    )

    # 校验前端提示信息
    assert "请输入用户名和密码" in page_text, (
        "密码为空时没有显示正确的提示信息"
    )

    # 保存截图
    save_screenshot(
        page,
        "portal-login-empty-password.png",
    )

    # 校验页面没有跳转
    assert_login_page_stays_open(page)

    # 校验控件仍然存在
    expect(username_input).to_be_visible()
    expect(password_input).to_be_visible()
    expect(login_button).to_be_visible()


# ============================================================
# 测试用例 5：用户名和密码都为空登录失败
# ============================================================

@pytest.mark.login
@allure.epic("商城前台 UI 自动化测试")
@allure.feature("用户登录模块")
@allure.story("用户名和密码都为空登录失败")
@allure.title("用户名和密码都为空时不能登录")
def test_portal_login_empty_username_and_password(
    page: Page,
):
    """
    验证用户名和密码都为空时不能登录。
    """

    # 打开登录页面
    with allure.step("打开商城前台登录页面"):
        open_login_page(page)

        expect(page).to_have_title("登录")

    # 获取页面元素
    username_input = get_username_input(page)
    password_input = get_password_input(page)
    login_button = get_login_button(page)

    # 清空用户名
    with allure.step("保持用户名为空"):
        username_input.fill("")

        expect(username_input).to_have_value("")

    # 清空密码
    with allure.step("保持密码为空"):
        password_input.fill("")

        expect(password_input).to_have_value("")

    # 点击登录按钮
    with allure.step("点击登录按钮"):
        login_button.click()

    # 等待前端提示
    page.wait_for_timeout(800)

    # 获取页面文本
    page_text = page.locator("body").inner_text()

    print(
        "用户名和密码都为空时页面文本：",
        page_text,
    )

    # 校验前端提示
    assert "请输入用户名和密码" in page_text, (
        "用户名和密码都为空时没有显示正确的提示信息"
    )

    # 保存截图
    save_screenshot(
        page,
        "portal-login-empty-username-and-password.png",
    )

    # 校验页面没有跳转
    assert_login_page_stays_open(page)

    # 校验控件仍然存在
    expect(username_input).to_be_visible()
    expect(password_input).to_be_visible()
    expect(login_button).to_be_visible()


# ============================================================
# 测试用例 6：登录页面元素完整性校验
# ============================================================

@pytest.mark.login
@allure.epic("商城前台 UI 自动化测试")
@allure.feature("用户登录模块")
@allure.story("登录页面元素完整性校验")
@allure.title("登录页面主要元素展示正常")
def test_portal_login_page_elements(page: Page):
    """
    验证商城前台登录页面主要元素展示正常。

    校验内容：
    1. 页面标题；
    2. LOGIN 标识；
    3. 欢迎语；
    4. 用户名标题；
    5. 用户名输入框；
    6. 用户名 placeholder；
    7. 密码标题；
    8. 密码输入框；
    9. 密码 placeholder；
    10. 登录按钮；
    11. 获取体验账号按钮；
    12. 忘记密码入口；
    13. 注册入口。
    """

    # 打开登录页面
    with allure.step("打开商城前台登录页面"):
        open_login_page(page)

    # 获取页面主体
    login_page = get_login_page(page)

    # ========================================================
    # 1. 页面标题校验
    # ========================================================

    with allure.step("校验登录页面标题"):
        expect(page).to_have_title("登录")

    # ========================================================
    # 2. LOGIN 标识校验
    # ========================================================

    with allure.step("校验 LOGIN 页面标识"):
        login_sign = login_page.locator(
            ".left-top-sign"
        )

        expect(login_sign).to_be_visible()
        expect(login_sign).to_contain_text("LOGIN")

    # ========================================================
    # 3. 欢迎语校验
    # ========================================================

    with allure.step("校验欢迎语"):
        welcome_text = login_page.locator(
            ".welcome"
        )

        expect(welcome_text).to_be_visible()
        expect(welcome_text).to_contain_text(
            "欢迎回来"
        )

    # ========================================================
    # 4. 用户名标题校验
    # ========================================================

    with allure.step("校验用户名标题"):
        username_item = login_page.locator(
            ".input-item"
        ).nth(0)

        expect(username_item).to_be_visible()
        expect(username_item).to_contain_text(
            "用户名"
        )

    # ========================================================
    # 5. 用户名输入框校验
    # ========================================================

    username_input = get_username_input(page)

    with allure.step("校验用户名输入框"):
        expect(username_input).to_be_visible()

        # 校验输入框类型
        expect(username_input).to_have_attribute(
            "type",
            "text",
        )

        # 页面首次打开时用户名应该为空
        expect(username_input).to_have_value("")

    # ========================================================
    # 6. 用户名 placeholder 校验
    # ========================================================

    with allure.step("校验用户名输入提示文字"):
        # 注意：
        # 不能使用：
        #
        # page.locator("uni-input").nth(0).inner_text()
        #
        # 因为 placeholder 在：
        #
        # .uni-input-wrapper
        #     └── .uni-input-placeholder
        #
        username_placeholder = get_username_placeholder(
            page
        )

        # 校验 placeholder 可见
        expect(username_placeholder).to_be_visible()

        # 校验 placeholder 文本
        expect(username_placeholder).to_contain_text(
            "请输入用户名"
        )

    # ========================================================
    # 7. 密码标题校验
    # ========================================================

    with allure.step("校验密码标题"):
        password_item = login_page.locator(
            ".input-item"
        ).nth(1)

        expect(password_item).to_be_visible()
        expect(password_item).to_contain_text(
            "密码"
        )

    # ========================================================
    # 8. 密码输入框校验
    # ========================================================

    password_input = get_password_input(page)

    with allure.step("校验密码输入框"):
        expect(password_input).to_be_visible()

        # 校验输入框类型
        expect(password_input).to_have_attribute(
            "type",
            "password",
        )

        # 页面首次打开时密码应该为空
        expect(password_input).to_have_value("")

    # ========================================================
    # 9. 密码 placeholder 校验
    # ========================================================

    with allure.step("校验密码输入提示文字"):
        password_placeholder = get_password_placeholder(
            page
        )

        # 校验 placeholder 可见
        expect(password_placeholder).to_be_visible()

        # 校验密码 placeholder 文本
        expect(password_placeholder).to_contain_text(
            "8-18位不含特殊字符"
        )

    # ========================================================
    # 10. 登录按钮校验
    # ========================================================

    with allure.step("校验登录按钮"):
        login_button = get_login_button(page)

        expect(login_button).to_be_visible()
        expect(login_button).to_contain_text("登录")
        expect(login_button).to_be_enabled()

    # ========================================================
    # 11. 获取体验账号按钮校验
    # ========================================================

    with allure.step("校验获取体验账号按钮"):
        experience_button = get_experience_button(
            page
        )

        expect(experience_button).to_be_visible()
        expect(experience_button).to_contain_text(
            "获取体验账号"
        )
        expect(experience_button).to_be_enabled()

    # ========================================================
    # 12. 忘记密码入口校验
    # ========================================================

    with allure.step("校验忘记密码入口"):
        forget_password = login_page.locator(
            ".forget-section"
        )

        expect(forget_password).to_be_visible()
        expect(forget_password).to_contain_text(
            "忘记密码"
        )

    # ========================================================
    # 13. 注册入口校验
    # ========================================================

    with allure.step("校验注册入口"):
        register_section = login_page.locator(
            ".register-section"
        )

        expect(register_section).to_be_visible()
        expect(register_section).to_contain_text(
            "还没有账号"
        )
        expect(register_section).to_contain_text(
            "马上注册"
        )

    # 保存页面元素校验截图
    save_screenshot(
        page,
        "portal-login-page-elements.png",
    )

    # 输出校验结果
    print("登录页面元素完整性校验通过")