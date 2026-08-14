import pytest

@pytest.fixture(scope="module")
def my_data():
    print("\n【夹具：执行前置】")
    yield "我是夹具返回的数据"
    print("【夹具：执行后置清理】")


def test_demo1(my_data):
    print("test_demo1 拿到的数据：", my_data)

def test_demo2(my_data):
    print("test_demo2 拿到的数据：", my_data)