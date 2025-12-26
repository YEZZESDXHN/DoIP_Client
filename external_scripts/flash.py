from time import sleep
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api import ScriptAPI


def main(api: "ScriptAPI"):
    api.write("开始执行刷写脚本")





def on_load(ctx: "ScriptAPI"):
    print("on_load")
