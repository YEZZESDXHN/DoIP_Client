# DoIP_Client

一个用于车辆诊断（DoIP / UDS — Diagnostic over IP / Unified Diagnostic Services）的 Python 客户端库与示例程序

> 注意：仓库中包含的实现为客户端示例和工具集合。具体的使用细节（IP/端口、会话处理、鉴权、报文格式）需根据目标 ECU / 测试平台调整；若用于真实车辆，请遵守厂商规范与安全流程。



## 项目简介
DoIP_Client 支持一下功能：
- [x] 支持多个配置
- [x] DoIP客户端实现，可手动发送DoIP请求并获取响应。
- [x] 添加删除UDS指令到UDS Service Tree，并双击发送。
- [x] 加载外部.py脚本实现自动化诊断流程或其他操作（v0.0.3打包release版本内置pycryptodome和crcmod库）。
- [x] 加载.py脚本实现27解锁服务。
- [x] UDS刷写，可自行配置刷写步骤，支持hex,bin,s19,但当前只验证了hex格式
- [x] 支持Vector设置,其他python-can支持的设备理论也可很轻松的集成
- [x] 支持单通道CAN IG模块，可用于唤醒ECU
- [x] 生成测试报告（只实现了运行外部脚本部分）。
- [x] 支持TSMaster，基于TC1016测试，但部分逻辑还需要优化，部分电脑无法识别，原因未知
- [ ] 导入导出配置文件。
- [ ] 加载符合vector规范的.dll实现27解锁服务（默认打包release程序为64位，如dll为32位会加载失败）。
- [ ] 可视化方式编写自动化诊断流程（保存到数据库部计划重构为只保存json）。


更多体验及细节持续优化。

---

## 软件截图

![app](/images/main_app.png)



## 仓库结构（主要文件/目录）

```
/
├─ .github/
│  └─ workflows/                    # GitHub Actions workflow 配置
├─ .gitignore                        # Git 忽略规则
├─ ExternalLib/
│  └─ __init__.py                    # ExternalLib 包初始化（占位）
├─ GenerateKeyExOpt/
│  └─ GenerateKeyExOptDemo.py       # 密钥算法演示脚本
├─ app/
│  ├─ core/                          # 应用核心模块
│  ├─ external_scripts/              # 执行外部脚本模块
│  ├─ flash/                         # 执行刷写模块
│  ├─ resources/                     # 静态资源（图标、布局等）
│  ├─ ui/                            # 界面层代码
│  ├─ windows/                       # 自定义界面
│  ├─ global_variables.py            # 全局变量与配置常量
│  ├─ user_data.py                   # 用户数据处理与持久化
│  └─ utils.py                       # 通用工具函数
├─ external_scripts/
│  ├─ api.py                         # 对外/脚本化 API 实现
│  └─ external_script_demo.py        # external_scripts 演示脚本
├─ logging.conf                       # 日志配置（Python logging）
├─ main.py                            # 程序入口 / 客户端主逻辑
├─ requirements.txt                   # Python 依赖列表
├─ tosun/
│  ├─ TSMasterApi/                   # TSMaster API 子模块
│  ├─ __init__.py                    # tosun 包初始化
│  └─ canlib.py                      # CAN 总线相关库封装
├─ tsmaster_test.py                   # 测试 / 示例脚本（TSMaster 相关）
└─ README.md
```

---

## 快速开始

1. 克隆仓库并进入目录
```bash
git clone https://github.com/YEZZESDXHN/DoIP_Client.git
cd DoIP_Client
```

2. 建议创建虚拟环境并安装依赖（推荐 Python 3.8+）
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```
3. 运行示例应用
```bash
python main.py
```
4. 配置
- 与DUT建立物理连接，以太网或CAN/CANFD，确保通信正常（当前支支持以太网）
- 编辑 `logging.conf` 以控制日志级别、文件位置与格式。
- 设置好UDS On IP/CAN的参数，点击连接

---



## 加载Python脚本实现27解锁

```
from typing import Any, Optional

# 解锁算法统一入口，不允许修改
def GenerateKeyExOpt(
        seed: bytes,               # Array for the seed [in]
        level: int,                # Security level [in]
        max_key_size: int = 64,    # Maximum length of the array for the key [in]
        variant: Any = None,       # Name of the active variant [in]
        options: Any = None,       # Optional parameter which might be used for OEM specific information [in]
        ) -> Optional[bytes]:
    key_out = None
    # 此处添加解锁算法
    # 支持导入标准库
    return key_out
```

---

## 加载Python脚本实现自动化诊断流程
api.py文件，程序对外SDK文件，随项目发布
```
api.py


class UDSClient:
    security_seed: bytes
    security_key: bytes

    def uds_send_and_wait_response(self, payload: bytes) -> Optional[Response]:
        pass


class Utils:
    def hex_str_to_bytes(self, hex_str: str) -> bytes:
        pass

class FirmwareFileParser:
    """
    用于解析 S19, HEX, BIN 文件的通用类。
    底层基于 bincopy 库，提供统一的读写和数据访问接口。
    """
    def load(self, filepath: str, start_address: int = 0) -> None:
        """
        加载固件文件，自动根据扩展名识别格式。

        Args:
            filepath: 文件路径
            start_address: 仅针对 .bin 文件有效，指定二进制文件的起始加载地址
        """
        pass

    def get_segments(self) -> List[Tuple[int, bytes]]:
        """
        获取固件的所有数据段。

        Returns:
            List[Tuple[address, data]]: 返回一个列表，包含 (起始地址, 数据bytes)
            这是处理非连续内存（Sparse Memory）的最佳方式。
        """
        pass

    def get_merged_data(self, fill: int = 0xFF) -> Tuple[int, bytes]:
        """
        获取合并后的完整二进制数据（自动填充空洞）。

        Args:
            fill: 地址不连续时的填充字节（整数，例如 0xFF）

        Returns:
            (start_address, data): 整个固件块的起始地址和完整数据
        """
        pass

    def get_size(self) -> int:
        """获取固件数据的实际字节大小（不包含空洞）"""
        pass

    def get_range(self) -> Tuple[int, int]:
        """获取固件的地址范围 (min_addr, max_addr)"""
        pass

    def export(self, output_path: str, fmt: str = 'bin', **kwargs) -> None:
        """
        将当前加载的固件转换为其他格式并保存。

        Kwargs:
            fill (int): 填充字节，默认 0xFF
            execution_addr (int): S19 文件的 S7/S8/S9 入口地址。如果不指定，默认尝试使用 0。
        """
        pass

# api接口
class ScriptAPI:
    # uds客户端实现，核心方法一提取到uds_send_and_wait_response
    _uds_client: UDSClient
    _utils: Utils
    version: str

    @staticmethod
    def create_firmware_parser() -> FirmwareFileParser:
        """
        生成刷写文件解析器，FirmwareFileParser
        """
        pass

    # 新增测速报告相关函数
    # 测速步骤
    def test_step(self, title: str, data: Optional[Union[str, bytes, List, bytearray, int, float]] = None):
        pass

    # 测速步骤Pass
    def test_step_pass(self, title, data: Optional[Union[str, bytes, List, bytearray, int, float]] = None):
        pass

    # 测速步骤Fail,即使脚本中没有使用assert，执行了此函数也会导致测试结果Fail
    def test_step_fail(self, title, data: Optional[Union[str, bytes, List, bytearray, int, float]] = None):
        pass

    def uds_send_and_wait_response(self, payload: bytes) -> Optional[Response]:
        pass

    @property
    def uds_security_key(self) -> bytes:
        return self._uds_client.security_key

    @property
    def uds_security_seed(self) -> bytes:
        return self._uds_client.security_seed

    def hex_str_to_bytes(self, hex_str: str) -> bytes:
        pass

    @staticmethod
    def sleep(secs: float) -> None:
        pass

    def write(self, text: str):
        pass
```


外部测试脚本Demo

```
external_script_demo.py


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
```
此脚本支持导入Python标准库，语法与正常Python环境一致

## 报告截图
![report](/images/html_report1.png)

## 外部脚本使用第三方库
对于实现27解锁和UDS自动化的外部脚本都支持加载第三方库，语法与支持Python一致
- 使用本地环境运行
  - 安装需要的第三方库后直接在外部脚本里导入即可
- 使用打包完成的exe程序运行
  - 打包环境里包含的库，如本仓库v0.0.3 release里的程序，内部包含pycryptodome和crcmod，外部脚本可直接导入使用
  - 打包环境里没有的库，如果是纯Python库，理论上支持将包下载到本地，放在脚本相同路径下或项目ExternalLib文件夹下，作为本地py文件导入（尚未进行验证）

## 调试与排查建议

- 如遇到问题可启用 DEBUG 日志，查看报错内容。
- 使用网络抓包工具（Wireshark）可查看完整通信过程 
- 对与DoIP通信，检查防火墙/路由与子网设置；在同一交换机/网段下。

---
