from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api import Context


def main(ctx: "Context"):
    print("main")
    print(ctx.uds_client.uds_send_and_wait_response(b'\x10\x01'))


def on_load(ctx: "Context.uds_client"):
    print("on_load")
    print(ctx)
