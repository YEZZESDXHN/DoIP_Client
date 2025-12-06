from dataclasses import dataclass, asdict, fields
from enum import Enum
from typing import Any

from doipclient.constants import TCP_DATA_UNSECURED, UDP_DISCOVERY
from doipclient.messages import RoutingActivationRequest

class DiagnosisStepTypeEnum(Enum):
    NormalStep = "普通步骤"
    ExistingStep = "已有配置"

@dataclass
class DiagnosisStepData:
    enable: int = 1
    step_type: DiagnosisStepTypeEnum = DiagnosisStepTypeEnum.NormalStep
    service: str = ''
    send_data: bytes = b''
    exp_resp_data: bytes = b''


    def get_attr_names(self) -> tuple:
        """返回属性名字元组"""
        # fields(self) 按定义顺序返回所有数据属性，提取 name 组成元组
        return tuple(field.name for field in fields(self))

    def to_tuple(self) -> tuple:
        """返回所有数据属性的元组（枚举字段返回value，其他字段返回原值）"""
        tuple_values = []
        for field in fields(self):
            value = getattr(self, field.name)
            # 对枚举类型字段，提取其value；其他字段直接用原值
            if isinstance(value, Enum):
                tuple_values.append(value.value)
            elif isinstance(value, bytes):
                tuple_values.append(value.hex(' '))
            else:
                tuple_values.append(value)
        return tuple(tuple_values)


@dataclass
class TableViewData:
    Time: str = ''
    Dir: str = ''
    Type: str = ''
    Destination_IP: str = ''
    Source_IP: str = ''
    DataLength: int = 0
    Data: str = ''
    ASCII: str = ''
    Data_bytes: bytes = b''
    code_name: str = ''
    uds_data: bytes = b''

    def Data_bytes_to_Data_hex(self):
        try:
            self.Data = self.Data_bytes.hex(' ')
        except Exception as e:
            raise e

    def uds_data_to_ascii(self):
        try:
            self.ASCII = self.uds_data.decode("ascii", errors="ignore")
        except Exception as e:
            raise e

    def to_tuple(self) -> tuple:
        """返回所有数据属性的元组（顺序与属性定义一致）"""
        # 遍历 fields 按定义顺序提取属性值
        return tuple(getattr(self, field.name) for field in fields(self))

    def get_attr_names(self) -> tuple:
        """返回属性名字元组（核心新增方法）"""
        # fields(self) 按定义顺序返回所有数据属性，提取 name 组成元组
        return tuple(field.name for field in fields(self))

    def is_empty(self) -> bool:
        """通用判断：所有属性是否均为默认空状态"""
        for attr_value in self.__dict__.values():
            # 判断当前属性是否为“非空有效数据”
            if self._is_non_empty_value(attr_value):
                return False  # 有任意非空属性，返回False
        return True  # 所有属性均为空，返回True

    @staticmethod
    def _is_non_empty_value(value) -> bool:
        """辅助方法：判断单个值是否为“非空有效数据”（可扩展类型）"""
        if isinstance(value, str):
            return value != ''  # 字符串非空
        elif isinstance(value, int):
            return value != 0  # 数字非零
        elif isinstance(value, bytes):
            return value != b''  # bytes非空
        elif isinstance(value, (list, dict, set)):
            return len(value) > 0  # 容器非空（后续若加容器属性可直接支持）
        elif value is not None:
            # 其他非None类型（如bool、datetime等），视为有效数据
            return True
        return False  # 空串、0、空bytes、None、空容器，均视为“空”


@dataclass
class DoIPConfig:
    config_name: str = 'default_config'
    tester_logical_address: int = 0x7e2
    dut_logical_address: int = 0x773
    dut_ipv4_address: str = '172.16.104.70'

    tcp_port: int = TCP_DATA_UNSECURED
    udp_port: int = UDP_DISCOVERY
    activation_type: int = RoutingActivationRequest.ActivationType.Default
    protocol_version: int = 0x02
    use_secure: int = 0
    is_routing_activation_use: int = 1
    is_oem_specific_use: int = 0
    oem_specific: int = 0

    def to_dict(self) -> dict:
        """转换为字典（用于 JSON 序列化或日志打印）"""
        return asdict(self)

    def to_update_dict(self) -> dict:
        """转换为数据库更新所需的字典（不含主键）"""
        data = asdict(self)
        data.pop('config_name')  # 移除主键
        return data

    def __str__(self) -> str:
        """自定义字符串输出，方便打印查看"""
        return (
            f"DoipConfig(config_name='{self.config_name}', "
            f"tester_logical_address={self.tester_logical_address}, "
            f"dut_logical_address={self.dut_logical_address}, "
            f"dut_ipv4_address='{self.dut_ipv4_address}', "
            f"is_routing_activation_use={'启用' if self.is_routing_activation_use == 1 else '禁用'}, "
            f"is_oem_specific_use={'启用' if self.is_oem_specific_use == 1 else '禁用'}, "
            f"oem_specific={self.oem_specific})"
        )
