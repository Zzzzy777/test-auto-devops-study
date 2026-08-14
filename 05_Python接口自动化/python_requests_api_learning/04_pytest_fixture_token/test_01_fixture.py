import pytest

# 1、写一个夹具函数，加上装饰器 @pytest.fixture
@pytest.fixture()
def my_data():
    print("\n【夹具：执行前置】")
    yield "我是夹具返回的数据"   # 把数据交给测试用例
    print("【夹具：执行后置清理】")


# 2、测试用例，参数写上夹具名字 my_data
def test_demo1(my_data):
    print("test_demo1 拿到的数据：", my_data)


def test_demo2(my_data):
    print("test_demo2 拿到的数据：", my_data)