import pytest
import allure
from common.config import FRONTEND_LOGIN_URL

# pytest钩子：捕获每条用例执行结果，给fixture使用
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # 执行测试用例
    outcome = yield
    rep = outcome.get_result()
    # 把执行结果挂载到用例对象上，rep_call代表用例执行阶段
    setattr(item, "rep_" + rep.when, rep)

@pytest.fixture(scope="function")
def page(page, request):
    """
    playwright page夹具，每条用例独立浏览器页面
    :param page: playwright内置page对象
    :param request: pytest内置对象，用来获取当前用例执行结果
    """
    # 访问【登录页面】，不是index首页！
    page.goto(FRONTEND_LOGIN_URL)
    yield page

    # 用例执行完成，判断是否失败，失败则截图存入allure报告
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        allure.attach(
            page.screenshot(),
            name="用例失败截图",
            attachment_type=allure.attachment_type.PNG
        )
    # 关闭页面
    page.close()