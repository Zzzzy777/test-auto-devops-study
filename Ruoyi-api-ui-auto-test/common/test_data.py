"""
测试数据工厂。

测试数据必须具备以下特点：

1. 每次运行尽量唯一；
2. 能够根据前缀识别测试数据；
3. 测试结束后可以安全清理；
4. 不修改系统原有真实数据。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import uuid


@dataclass(frozen=True)
class UserData:
    """用户测试数据对象。"""

    username: str
    nickname: str
    password: str
    phone: str

    def to_dict(self) -> dict[str, str]:
        """转换成普通字典，方便日志和 Allure 附件使用。"""
        return asdict(self)


@dataclass(frozen=True)
class RoleData:
    """角色测试数据对象。"""

    role_name: str
    role_key: str
    role_sort: int = 1
    status: str = "0"

    def to_dict(self) -> dict[str, object]:
        """转换为角色新增接口所需的基础字段。"""
        return asdict(self)


def build_unique_user(
    prefix: str = "ui_test_",
) -> UserData:
    """
    构造唯一用户。

    例如：

    ui_test_a1b2c3d4
    api_test_e5f6g7h8
    """
    unique_id = uuid.uuid4().hex

    return UserData(
        username=f"{prefix}{unique_id[:8]}",
        nickname=f"自动化测试用户_{unique_id[8:14]}",
        password="123456",
        phone=(
            f"139"
            f"{int(unique_id[:8], 16) % 100_000_000:08d}"
        ),
    )


def build_unique_role(
    prefix: str = "api_test_role_",
) -> RoleData:
    """
    构造唯一角色。

    roleKey 通常比 roleName 更适合作为清理条件。
    """
    unique_id = uuid.uuid4().hex

    return RoleData(
        role_name=f"自动化测试角色_{unique_id[:8]}",
        role_key=f"{prefix}{unique_id[8:20]}",
    )


def build_user_payload(user: UserData) -> dict[str, object]:
    """?? RuoYi ????/?????????"""
    from common.config import DEFAULT_DEPT_ID
    return {
        "userName": user.username,
        "nickName": user.nickname,
        "password": user.password,
        "phonenumber": user.phone,
        "deptId": DEFAULT_DEPT_ID,
    }


def build_role_payload(role: RoleData) -> dict[str, object]:
    """?? RuoYi ???????????"""
    return {
        "roleName": role.role_name,
        "roleKey": role.role_key,
        "roleSort": role.role_sort,
        "status": role.status,
        # RuoYi ????????????? menuIds.length?
        # ????????????????????
        "menuCheckStrictly": True,
        "deptCheckStrictly": True,
        "menuIds": [],
    }
