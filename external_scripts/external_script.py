from time import sleep
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api import Context


def main(ctx: "Context"):

    response = ctx.uds_client.uds_send_and_wait_response(b'\x10\x03')
    response = ctx.uds_client.uds_send_and_wait_response(b'\x27\x01')
    data = b'\x27\x02'+ctx.uds_client.security_key
    response = ctx.uds_client.uds_send_and_wait_response(data)
    sleep(10)
    response = ctx.uds_client.uds_send_and_wait_response(b'\x10\x03')
    print('main finshed')



def on_load(ctx: "Context.uds_client"):
    print("on_load")
    print(ctx)
