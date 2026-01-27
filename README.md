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
- [ ] 导入导出配置文件。
- [ ] 加载符合vector规范的.dll实现27解锁服务（默认打包release程序为64位，如dll为32位会加载失败）。
- [ ] 可视化方式编写自动化诊断流程（保存到数据库部分采购为只保存json）。
- [ ] TSMaster暂不支，获取到设备后连接失败，部分电脑甚至无法获取设备列表，原因未知

更多体验及细节持续优化。

---


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

# api接口
class ScriptAPI:
    _uds_client: UDSClient
    _utils: Utils
    version: str

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

```
external_script_demo.py


from typing import TYPE_CHECKING

# 加载api文档用于代码提示，运行时不会导入，防止文件缺失时报错
if TYPE_CHECKING:
    from api import Context

# 外部脚本运行入口
def main(api: "ScriptAPI"):
    # 发送UDS诊断：10 01并获取响应
    response = api.uds_send_and_wait_response(b'\x10\x01')
    # 根据响应结果判断pass和fail，此处暂时使用print演示，后续会逐步增加api函数
    if response.original_payload[0] == 0x50:
        print("pass")
    else:
        print("fail")
```
此脚本支持导入Python标准库，语法与正常Python环境一致

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
