from time import sleep
from typing import TYPE_CHECKING

# 忽略导入报错（工具内已打包crcmod和pycryptodome/Crypto库）
import crcmod.predefined
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


if TYPE_CHECKING:
    from api import ScriptAPI

def aes128_encrypt(plain_data: bytes, key: bytes, mode: str = "ECB", iv: bytes = b"") -> bytes:
    """
    AES128加密函数
    :param plain_data: 待加密明文（bytes类型）
    :param key: 加密密钥（bytes类型，必须16字节，AES128要求）
    :param mode: 加密模式，ECB（默认）/CBC，硬件/车载测试常用
    :param iv: CBC模式必填初始向量（bytes类型，必须16字节），ECB模式无需传
    :return: 加密后的密文（bytes类型）
    :raise: 密钥错误、模式错误、IV错误、加解密异常等
    """
    # 密钥校验：AES128必须16字节密钥
    if len(key) != 16:
        raise ValueError(f"AES128密钥长度错误，要求16字节，实际{len(key)}字节")
    # 模式选择
    if mode.upper() == "ECB":
        cipher = AES.new(key, AES.MODE_ECB)
    elif mode.upper() == "CBC":
        # CBC模式IV校验：必须16字节
        if len(iv) != 16:
            raise ValueError(f"CBC模式IV长度错误，要求16字节，实际{len(iv)}字节")
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    else:
        raise ValueError(f"不支持的AES模式：{mode}，仅支持ECB/CBC")
    # PKCS7补码（AES要求数据长度为16字节整数倍）+ 加密
    padded_data = pad(plain_data, AES.block_size, style='pkcs7')
    cipher_data = cipher.encrypt(padded_data)
    return cipher_data


def test_1001(api: "ScriptAPI"):
    api.test_step("发送1001")
    response = api.uds_send_and_wait_response(b'\x10\x01')
    if response.original_payload[0] == 0x50:
        api.test_step_pass("检查 10 01 响应", response.original_payload)
    else:
        # 执行此语句会导致测试结果Fail,并打印信息
        api.test_step_fail("检查 10 01 响应", response.original_payload)

    sleep(1)

    api.test_step("发送1001")
    response = api.uds_send_and_wait_response(b'\x10\x01')
    if response.original_payload[0] == 0x50:
        # 执行此语句会导致测试结果Fail,并打印信息
        api.test_step_fail("检查 10 01 响应", response.original_payload)
    else:
        api.test_step_pass("检查 10 01 响应", response.original_payload)


def test_1001_with_assert(api: "ScriptAPI"):
    api.test_step("发送1001")
    response = api.uds_send_and_wait_response(b'\x10\x01')

    # 执行此语句会根据结果判断case的结果，但不会打印信息
    assert response.original_payload[0] == 0x50

def test_parser_hex(api: "ScriptAPI"):
    api.test_step("解析hex文件")
    hex_parser = api.create_firmware_parser()
    hex_parser.load('Hello_World.hex')
    range = hex_parser.get_range()
    if range:
        api.test_step_pass("成功获取hex文件地址范围",f"起始地址：{range[0]},结束地址：{range[0]}")
    else:
        api.test_step_fail("获取hex文件地址范围失败")

    api.test_step("计算block1的crc32")
    segments = hex_parser.get_segments()
    if not segments:
        api.test_step_fail("获取hex数据失败")
        return
    block1_data = segments[0][1]

    # 工具内以及打包crcmod库，可忽略报错直接使用
    crc32_func = crcmod.predefined.mkPredefinedCrcFun('crc-32')
    crc32 = crc32_func(block1_data)
    if crc32:
        api.test_step_pass("成功计算crc32",f"crc：{crc32}")
    else:
        api.test_step_fail("计算crc32失败")


    AES128_KEY = b"1234567890abcdef"  # 16字节密钥，必须修改为实际密钥
    AES128_MODE = "ECB"               # 加密模式：ECB/CBC，按需切换
    AES128_IV = b"0000000000000000"   # CBC模式必填16字节IV，ECB模式可忽略
    aes_cipher = aes128_encrypt(
        plain_data=block1_data,
        key=AES128_KEY,
        mode=AES128_MODE,
        iv=AES128_IV
    )

    api.test_step_pass("AES128加密成功", f"加密模式：{AES128_MODE}，密文（16进制）：{aes_cipher.hex().upper()}")