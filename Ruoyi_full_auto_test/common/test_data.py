from __future__ import annotations

from dataclasses import asdict, dataclass
import uuid


@dataclass(frozen=True)
class UserData:
    username: str
    nickname: str
    password: str
    phone: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def build_unique_user(prefix: str = "ui_test_") -> UserData:
    """Create data that can be safely used in a repeatable UI test."""
    unique_id = uuid.uuid4().hex
    return UserData(
        username=f"{prefix}{unique_id[:8]}",
        nickname=f"UI自动化_{unique_id[8:14]}",
        password="123456",
        phone=f"139{int(unique_id[:8], 16) % 100_000_000:08d}",
    )