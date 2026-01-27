from time import sleep
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api import ScriptAPI


def test_1001_1003(api: "ScriptAPI"):
    api.test_step("发送1001", b'\x10\x01')
    response = api.uds_send_and_wait_response(b'\x10\x01')
    if response.original_payload[0] == 0x50:
        api.test_step_fail("检查 10 01 响应", response.original_payload[0])


def test_1003_sleep(api: "ScriptAPI"):
    api.test_step("发送1003", "发送1003")
    response = api.uds_send_and_wait_response(b'\x10\x03')
    assert response.original_payload[0] == 0x50