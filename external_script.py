from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api import Context


def on_run(ctx: "Context"):
    print("on_run")
    print(ctx.uds_client.send_payload(b'\x10\x01'))


def on_load(ctx: "Context.uds_client"):
    print("on_load")
    print(ctx)
