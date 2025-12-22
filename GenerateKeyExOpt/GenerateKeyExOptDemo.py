from typing import Any, Optional
from Crypto.Cipher import AES

def AES_CFB_encrypt(iv: bytes, key: bytes, data: bytes) -> bytes:
    """
    加密数据
    :param iv: IV
    :param key: key
    :param data: 待加密的字符串或bytes
    :return: hex字符串 (包含 IV + 密文)
    """
    # 1. 确保数据是 bytes 格式
    if isinstance(data, str):
        data = data.encode('utf-8')

    # 3. 初始化加密器
    # segment_size 默认为 8 (即 CFB-8)，这里我们使用默认设置
    cipher = AES.new(key, AES.MODE_CFB, iv=iv, segment_size=128)

    # 4. 加密 (CFB 是流模式，不需要填充/padding)
    ciphertext = cipher.encrypt(data)

    return ciphertext


def GenerateKeyExOpt(
        seed: bytes,            # Array for the seed [in]
        level: int,         # Security level [in]
        max_key_size: int = 64,       # Maximum length of the array for the key [in]
        variant: Any = None,              # Name of the active variant [in]
        options: Any = None,              # Optional parameter which might be used for OEM specific information [in]
        ) -> Optional[bytes]:
    # L1 ML
    aes_key_L1_ML = bytes([0x96] * 16)
    aes_iv_L1_ML  = bytes([0x28] * 16)

    # L61 ML
    aes_key_L61_ML = bytes([0x3F] * 16)
    aes_iv_L61_ML  = bytes([0x50] * 16)

    security_key: Optional[bytes] = None
    if level == 0x01:
        security_key = AES_CFB_encrypt(iv=aes_iv_L1_ML, key=aes_key_L1_ML, data=seed)
    elif level == 0x11:
        security_key = AES_CFB_encrypt(iv=aes_iv_L1_ML, key=aes_key_L1_ML, data=seed)
    elif level == 0x61:
        security_key = AES_CFB_encrypt(iv=aes_iv_L61_ML, key=aes_key_L61_ML, data=seed)
    return security_key