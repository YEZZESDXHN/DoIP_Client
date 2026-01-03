from dataclasses import field, dataclass
from typing import Optional, Union


@dataclass
class FlashBaseVars:
    data: bytes = b''
    addr: int = 0
    size: int = 0
    checksum: bytes = b''


# @dataclass
# class FlashBlockVars:
#     BlockVars: list[FlashBaseVars] = field(default_factory=list)


@dataclass
class FlashFileVars:
    base_vars: FlashBaseVars = FlashBaseVars()
    flash_block_vars: list[FlashBaseVars] = field(default_factory=list)


@dataclass
class FlashFilesVars:
    files_vars: dict[str, FlashFileVars] = field(default_factory=dict)


gFlashVars = FlashFilesVars()
