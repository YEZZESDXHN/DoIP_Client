from typing import Any, Optional


def GenerateKeyExOpt(
        seed: bytes,            # Array for the seed [in]
        level: int,         # Security level [in]
        max_key_size: int = 64,       # Maximum length of the array for the key [in]
        variant: Any = None,              # Name of the active variant [in]
        options: Any = None,              # Optional parameter which might be used for OEM specific information [in]
        ) -> Optional[bytes]:
    print(seed.hex(' '))
    print(level)
    print(max_key_size)
    print(variant)
    print(options)
    return seed
