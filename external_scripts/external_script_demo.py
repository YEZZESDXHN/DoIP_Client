from time import sleep
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api import ScriptAPI


def main(api: "ScriptAPI"):
    api.write("开始执行脚本")
    response = api.uds_send_and_wait_response(b'\x10\x03')
    if response.original_payload[0] != 1:
        api.write('')
    response = api.uds_send_and_wait_response(b'\x27\x01')
    data = b'\x27\x02'+api.uds_security_key
    response = api.uds_send_and_wait_response(data)
    sleep(10)
    response = api.uds_send_and_wait_response(b'\x10\x03')
    api.write('main finshed')



def on_load(ctx: "ScriptAPI"):
    print("on_load")
    print(ctx)
