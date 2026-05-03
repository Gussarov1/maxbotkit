from __future__ import annotations

from maxbotkit.methods.delete_message import DeleteMessage
from maxbotkit.methods.edit_message import EditMessage
from maxbotkit.methods.get_chats import GetChats
from maxbotkit.methods.get_updates import GetUpdates
from maxbotkit.methods.send_message import SendMessage


def test_send_message_serialization() -> None:
    method = SendMessage(
        chat_id=123,
        text="hello",
        notify=False,
        format="markdown",
        link={"type": "reply", "mid": "mid.1"},
    )

    assert method.build_params() == {
        "chat_id": 123,
        "user_id": None,
        "disable_link_preview": None,
    }
    assert method.build_body() == {
        "text": "hello",
        "notify": False,
        "format": "markdown",
        "link": {"type": "reply", "mid": "mid.1"},
    }


def test_edit_message_serialization() -> None:
    method = EditMessage(message_id="mid.2", text="updated")

    assert method.build_params() == {"message_id": "mid.2"}
    assert method.build_body() == {
        "text": "updated",
        "notify": True,
        "format": None,
        "link": None,
    }


def test_delete_message_serialization() -> None:
    method = DeleteMessage(message_id="mid.3")

    assert method.build_params() == {"message_id": "mid.3"}


def test_get_updates_serialization() -> None:
    method = GetUpdates(limit=100, timeout=30, marker=50, types=["message_created", "bot_started"])

    assert method.build_params() == {
        "limit": 100,
        "timeout": 30,
        "marker": 50,
        "types": "message_created,bot_started",
    }
    assert method.request_timeout(10.0) == 35.0


def test_get_chats_serialization() -> None:
    method = GetChats(count=100, marker=10)

    assert method.build_params() == {"count": 100, "marker": 10}
