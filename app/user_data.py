# from __future__ import annotations
import base64
import binascii
import dataclasses
import enum
import json
import pprint
from dataclasses import dataclass, asdict, fields, is_dataclass, field
from enum import Enum
from functools import cached_property
from typing import Any, Optional, Type, get_args, get_origin

from doipclient.constants import TCP_DATA_UNSECURED, UDP_DISCOVERY
from doipclient.messages import RoutingActivationRequest


@dataclass
class DiagCase:
    id: Optional[int] = None
    case_name: str = ''
    config_name: str = ''
    type: int = 0  # 0:case,1:group
    level: int = 0
    parent_id: int = -1  # -1:顶级节点

    @classmethod
    def from_dict(cls, data: dict) -> "DiagCase":
        """从字典转回 DiagCase 对象（兼容 DataFrame 行转对象）"""
        return cls(
            id=data.get("id", 0),
            case_name=data.get("case_name", ""),
            config_name=data.get("config_name", ""),
            type=data.get("type", 0),
            level=data.get("level", 0),
            parent_id=data.get("parent_id")
        )

    def get_attr_names(self) -> tuple:
        """返回属性名字元组"""
        # fields(self) 按定义顺序返回所有数据属性，提取 name 组成元组
        return tuple(_field.name for _field in fields(self))

    def to_tuple(self) -> tuple:
        """返回所有数据属性的元组（枚举字段返回value，其他字段返回原值）"""
        tuple_values = []
        for _field in fields(self):
            value = getattr(self, _field.name)
            tuple_values.append(value)
        return tuple(tuple_values)

    def to_json(self) -> str:
        """数据类转json字符串"""
        data_dict = asdict(self)
        data_json = json.dumps(data_dict)
        return data_json

    def to_dict(self) -> dict:
        """数据类转dict"""
        data_dict = asdict(self)
        return data_dict

    def _get_field_type(self, field_name: str) -> Optional[Type]:
        """辅助方法：获取属性的类型"""
        if not is_dataclass(self):
            return None
        cls = type(self)
        return cls.__annotations__.get(field_name)

    def update_from_dict(self, data_dict: dict):
        """从dict更新数据类"""
        for key, value in data_dict.items():
            if not hasattr(self, key):
                continue
            field_type = self._get_field_type(key)

            try:

                if field_type in (Optional[int], float, str) and value is not None:
                    setattr(self, key, value)

            except Exception as e:
                # 类型转换失败时打印提示，保留原值（也可改为raise抛出异常）
                print(f"警告：属性{key}赋值失败（{e}）,待赋值：{value}")
                continue

    def update_from_json(self, json_str: str):
        """从json更新数据类"""
        data_dict = json.loads(json_str)
        self.update_from_dict(data_dict)

@dataclass
class _DiagnosticSessionControl:
    name: str = ''
    payload: bytes = b''


@dataclass
class _ECUReset:
    name: str = ''
    payload: bytes = b''


@dataclass
class _ReadDataByIdentifier:
    name: str = ''
    payload: bytes = b''


@dataclass
class _InputOutputControlByIdentifier:
    name: str = ''
    payload: bytes = b''


@dataclass
class _ReadDTCInformation:
    name: str = ''
    payload: bytes = b''


@dataclass
class _RequestDownload:
    name: str = ''
    payload: bytes = b''


@dataclass
class _RequestUpload:
    name: str = ''
    payload: bytes = b''


@dataclass
class _TransferData:
    name: str = ''
    payload: bytes = b''


@dataclass
class _RequestTransferExit:
    name: str = ''
    payload: bytes = b''


@dataclass
class _SecurityAccess:
    name: str = ''
    payload: bytes = b''


@dataclass
class _TesterPresent:
    name: str = ''
    payload: bytes = b''


@dataclass
class _Routine:
    name: str = ''
    payload: bytes = b''


@dataclass
class _RoutineControl:
    startRoutine: list[_Routine] = field(default_factory=list)
    stopRoutine: list[_Routine] = field(default_factory=list)
    requestRoutineResults: list[_Routine] = field(default_factory=list)

    def _get_field_type(self, field_name: str) -> Optional[Type]:
        """辅助方法：获取属性的类型"""
        if not is_dataclass(self):
            return None
        cls = type(self)
        return cls.__annotations__.get(field_name)


@dataclass
class UdsService:
    """服务数据类"""
    DiagnosticSessionControl: list[_DiagnosticSessionControl] = field(default_factory=list)
    ECUReset: list[_ECUReset] = field(default_factory=list)
    ReadDataByIdentifier: list[_ReadDataByIdentifier] = field(default_factory=list)
    InputOutputControlByIdentifier: list[_InputOutputControlByIdentifier] = field(default_factory=list)
    ReadDTCInformation: list[_ReadDTCInformation] = field(default_factory=list)
    RequestDownload: list[_RequestDownload] = field(default_factory=list)
    RequestUpload: list[_RequestUpload] = field(default_factory=list)
    TransferData: list[_TransferData] = field(default_factory=list)
    RequestTransferExit: list[_RequestTransferExit] = field(default_factory=list)
    SecurityAccess: list[_SecurityAccess] = field(default_factory=list)
    TesterPresent: list[_TesterPresent] = field(default_factory=list)
    RoutineControl: _RoutineControl = field(default_factory=_RoutineControl)

    def _get_field_type(self, field_name: str) -> Optional[Type]:
        """辅助方法：获取属性的类型"""
        if not is_dataclass(self):
            return None
        cls = type(self)
        return cls.__annotations__.get(field_name)

    @staticmethod
    def _json_default_converter(obj):
        """数据类转换json时，不支持的类型转换规则"""
        if isinstance(obj, bytes):
            # 1. Base64 编码 (bytes -> bytes)
            encoded_bytes = base64.b64encode(obj)
            # 2. 转换为 UTF-8 字符串 (bytes -> str)
            return encoded_bytes.decode('utf-8')

        if isinstance(obj, DiagnosisStepTypeEnum):
            return obj.value

        # 对于其他无法序列化的对象（如 datetime 对象），可以抛出 TypeError
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    def to_json(self) -> str:
        """数据类转json字符串"""
        data_dict = asdict(self)
        data_json = json.dumps(data_dict, default=self._json_default_converter)
        return data_json

    def to_dict(self) -> dict:
        """数据类转dict"""
        data_dict = asdict(self)
        return data_dict

    def update_from_dict(self, data_dict: dict):
        """从dict更新数据类"""
        for key, value in data_dict.items():
            if not hasattr(self, key):
                continue
            field_type = self._get_field_type(key)
            current_obj = getattr(self, key, None)

            try:
                if get_origin(field_type) is list and isinstance(value, list) and isinstance(current_obj, list):
                    current_obj.clear()
                    args = get_args(field_type)
                    for list_item in value:
                        if isinstance(list_item, dict) and 'payload' in list_item:
                            if isinstance(list_item['payload'], bytes):
                                pass
                            elif isinstance(list_item['payload'], str):
                                try:
                                    # 尝试Base64解码（失败则说明不是Base64字符串，跳过）
                                    bytes_decode = base64.b64decode(list_item['payload'].encode('utf-8'))
                                except (binascii.Error, ValueError):
                                    bytes_decode = b''
                                list_item['payload'] = bytes_decode
                            cls = args[0](**list_item)
                            current_obj.append(cls)
                elif dataclasses.is_dataclass(field_type) and isinstance(value, dict) and dataclasses.is_dataclass(current_obj):
                    self.update_from_dict(value)

            except Exception as e:
                print(f'更新失败：{str(e)}')

    def update_from_json(self, json_str: str):
        """从json更新数据类"""
        data_dict = json.loads(json_str)
        self.update_from_dict(data_dict)


DEFAULT_SERVICES = UdsService()
DEFAULT_SERVICES.DiagnosticSessionControl = [
    _DiagnosticSessionControl("defaultSession", bytes.fromhex('1001')),
    _DiagnosticSessionControl("programmingSession", bytes.fromhex('1002')),
    _DiagnosticSessionControl("extendedDiagnosticSession", bytes.fromhex('1003')),
]
DEFAULT_SERVICES.ECUReset = [
    _ECUReset("hardReset", bytes.fromhex('1101')),
    _ECUReset("keyOffOnReset", bytes.fromhex('1102')),
    _ECUReset("softReset", bytes.fromhex('1103')),
]
DEFAULT_SERVICES.SecurityAccess = [
    _SecurityAccess("RequestSeed L1", bytes.fromhex('2701')),
    _SecurityAccess("SendKey L1", bytes.fromhex('2702')),
    _SecurityAccess("RequestSeed L3", bytes.fromhex('2703')),
    _SecurityAccess("SendKey L1", bytes.fromhex('2703')),
    _SecurityAccess("RequestSeed L5", bytes.fromhex('2705')),
    _SecurityAccess("SendKey L1", bytes.fromhex('2705')),
]


class DiagnosisStepTypeEnum(Enum):
    NormalStep = "普通步骤"
    ExistingStep = "已有配置"


class DiagnosisStepAddressEnum(Enum):
    Physical = "Phy"
    Function = "Fun"


class DiagnosisStepTestResultEnum(Enum):
    NotRun = "NotRun"
    Pass = "Pass"
    Fail = "Failed"
    Running = "Running"

@dataclass
class DiagnosisStepData:
    """诊断自动化测试步骤的数据类"""
    id: Optional[int] = None
    enable: bool = True
    step_type: DiagnosisStepTypeEnum = DiagnosisStepTypeEnum.NormalStep
    service: str = ''
    address: DiagnosisStepAddressEnum = DiagnosisStepAddressEnum.Physical
    send_data: bytes = b''
    exp_resp_data: bytes = b''
    delay: int = 50
    retry_times: int = 0
    is_stop_when_fail: bool = True
    result: DiagnosisStepTestResultEnum = DiagnosisStepTestResultEnum.NotRun

    case_id: int = 0
    step_sequence: int = 0

    def get_attr_names(self) -> tuple:
        """返回属性名字元组"""
        # fields(self) 按定义顺序返回所有数据属性，提取 name 组成元组
        return tuple(_field.name for _field in fields(self))

    def __setattr__(self, name, value):
        # 1. 先执行默认的属性赋值逻辑
        super().__setattr__(name, value)
        # 2. 若存在 to_tuple 缓存，自动清空
        cache_attr_name = 'to_tuple'
        if hasattr(self, cache_attr_name):
            delattr(self, cache_attr_name)

    @cached_property
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
            elif isinstance(value, bool):
                tuple_values.append(str(value))
            else:
                tuple_values.append(value)
        return tuple(tuple_values)

    @staticmethod
    def _json_default_converter(obj):
        """数据类转换json时，不支持的类型转换规则"""
        if isinstance(obj, bytes):
            # 1. Base64 编码 (bytes -> bytes)
            encoded_bytes = base64.b64encode(obj)
            # 2. 转换为 UTF-8 字符串 (bytes -> str)
            return encoded_bytes.decode('utf-8')

        elif isinstance(obj, Enum):
            return obj.value

        # 对于其他无法序列化的对象（如 datetime 对象），可以抛出 TypeError
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    def to_json(self) -> str:
        """数据类转json字符串"""
        data_dict = asdict(self)
        data_json = json.dumps(data_dict, default=self._json_default_converter)
        return data_json

    def to_dict(self) -> dict:
        """转换为字典"""
        data_dict = asdict(self)
        for key, value in data_dict.items():
            if isinstance(value, bytes):
                encoded_bytes = base64.b64encode(value)
                data_dict[key] = encoded_bytes.decode('utf-8')
            elif isinstance(value, Enum):
                data_dict[key] = value.value
            elif isinstance(value, bool):
                data_dict[key] = 'true' if value else 'false'

        return data_dict

    def _get_field_type(self, field_name: str) -> Optional[Type]:
        """辅助方法：获取属性的类型"""
        if not is_dataclass(self):
            return None
        cls = type(self)
        return cls.__annotations__.get(field_name)

    def update_by_value(self, attr_name: str, value: Any) -> bool:
        if not hasattr(self, attr_name):
            return False
        field_type = self._get_field_type(attr_name)
        try:
            if isinstance(field_type, type) and issubclass(field_type, enum.Enum):
                _value = field_type(value)
                setattr(self, attr_name, _value)
            # 处理基础类型转换（如字符串转数字）
            elif field_type in (int, float, bool, str) and value is not None:
                # bool类型特殊处理（避免"False"被转成True）
                if field_type == bool and isinstance(value, str):
                    _value = value.lower() in ("true", "1", "yes")
                    setattr(self, attr_name, _value)
                else:
                    _value = field_type(value)
                    setattr(self, attr_name, _value)
            elif field_type is bytes:
                if isinstance(value, bytes):
                    setattr(self, attr_name, value)
                elif isinstance(value, str):
                    try:
                        setattr(self, attr_name, bytes.fromhex(value))
                    except:
                        setattr(self, attr_name, b'')
        except Exception as e:
            print(f"警告：属性{attr_name}赋值失败（{str(e)}）")
            return False
        return True
    def update_from_dict(self, data_dict: dict):
        """从dict更新数据类"""
        for key, value in data_dict.items():
            if not hasattr(self, key):
                continue
            field_type = self._get_field_type(key)
            current_value = getattr(self, key, None)

            try:
                # 处理枚举类型（字符串/数字转枚举实例）
                if isinstance(field_type, type) and issubclass(field_type, enum.Enum):
                    value = field_type(value)
                # 处理基础类型转换（如字符串转数字）
                elif field_type in (int, float, bool, str) and value is not None:
                    # bool类型特殊处理（避免"False"被转成True）
                    if field_type == bool and isinstance(value, str):
                        value = value.lower() in ("true", "1", "yes")
                    else:
                        value = field_type(value)
                elif field_type is bytes:
                    if isinstance(value, bytes):
                        pass
                    elif isinstance(value, str):
                        try:
                            # 尝试Base64解码（失败则说明不是Base64字符串，跳过）
                            value = base64.b64decode(value.encode('utf-8'))
                        except (binascii.Error, ValueError):
                            value = b''

            except (ValueError, TypeError, enum.EnumError) as e:
                # 类型转换失败时打印提示，保留原值（也可改为raise抛出异常）
                print(f"警告：属性{key}赋值失败（{str(e)}），原值：{current_value}，待赋值：{value}")
                continue

                # 4. 最终赋值（仅当值有效时）
            if value is not None:
                setattr(self, key, value)

    def update_from_json(self, json_str: str):
        """从json更新数据类"""
        data_dict = json.loads(json_str)
        self.update_from_dict(data_dict)


class MessageDir(Enum):
    Tx = "Tx"
    Rx = "Rx"
    NoDir = ""


@dataclass
class DoIPMessageStruct:
    """DoIP消息数据类"""
    Time: str = ''
    Dir: MessageDir = MessageDir.NoDir
    Type: str = ''
    Destination_IP: str = ''
    Source_IP: str = ''
    DataLength: int = 0
    Data: str = ''
    ASCII: str = ''
    Data_bytes: bytes = b''
    code_name: str = ''
    uds_data: bytes = b''  # uds数据部分，如responses数据：62 f1 95 11 22 33,uds_data为：11 22 33

    def update_data_by_data_bytes(self):
        """将Data_bytes转为hex并更新到Data"""
        try:
            self.Data = self.Data_bytes.hex(' ')
        except Exception as e:
            raise e

    def update_ascii_by_uds_data(self):
        """将uds_data转为ascii并更新到ASCII"""
        try:
            self.ASCII = self.uds_data.decode("ascii", errors="ignore")
        except Exception as e:
            raise e

    def get_attr_names(self) -> tuple:
        """返回属性名字元组"""
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

    @staticmethod
    def _json_default_converter(obj):
        """数据类转换json时，不支持的类型转换规则"""
        if isinstance(obj, bytes):
            # 1. Base64 编码 (bytes -> bytes)
            encoded_bytes = base64.b64encode(obj)
            # 2. 转换为 UTF-8 字符串 (bytes -> str)
            return encoded_bytes.decode('utf-8')

        if isinstance(obj, DiagnosisStepTypeEnum):
            return obj.value

        # 对于其他无法序列化的对象（如 datetime 对象），可以抛出 TypeError
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    def to_json(self) -> str:
        """数据类转json字符串"""
        data_dict = asdict(self)
        data_json = json.dumps(data_dict, default=self._json_default_converter)
        return data_json

    def _get_field_type(self, field_name: str) -> Optional[type]:
        """辅助方法：获取属性的类型"""
        if not is_dataclass(self):
            return None
        cls = type(self)
        return cls.__annotations__.get(field_name)

    def update_from_dict(self, data_dict: dict):
        """从dict更新数据类"""
        for key, value in data_dict.items():
            if not hasattr(self, key):
                continue
            field_type = self._get_field_type(key)
            current_value = getattr(self, key, None)

            try:
                # 处理枚举类型（字符串/数字转枚举实例）
                if isinstance(field_type, type) and issubclass(field_type, enum.Enum):
                    value = field_type(value)
                # 处理基础类型转换（如字符串转数字）
                elif field_type in (int, float, bool, str) and value is not None:
                    # bool类型特殊处理（避免"False"被转成True）
                    if field_type == bool and isinstance(value, str):
                        value = value.lower() in ("true", "1", "yes")
                    else:
                        value = field_type(value)
                elif field_type is bytes:
                    if isinstance(value, bytes):
                        pass
                    elif isinstance(value, str):
                        try:
                            # 尝试Base64解码（失败则说明不是Base64字符串，跳过）
                            value = base64.b64decode(value.encode('utf-8'))
                        except (binascii.Error, ValueError):
                            value = b''

            except (ValueError, TypeError, enum.EnumError) as e:
                # 类型转换失败时打印提示，保留原值（也可改为raise抛出异常）
                print(f"警告：属性{key}赋值失败（{e}），原值：{current_value}，待赋值：{value}")
                continue

                # 4. 最终赋值（仅当值有效时）
            if value is not None:
                setattr(self, key, value)

    def update_from_json(self, json_str: str):
        """从json更新数据类"""
        data_dict = json.loads(json_str)
        self.update_from_dict(data_dict)


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
    is_routing_activation_use: bool = True
    is_oem_specific_use: bool = False
    oem_specific: int = 0
    GenerateKeyExOptPath: str = ''

    def get_attr_names(self) -> tuple:
        """返回属性名字元组"""
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

    def to_dict(self) -> dict:
        """转换为字典"""
        data_dict = asdict(self)
        for key, value in data_dict.items():
            if isinstance(value, bytes):
                encoded_bytes = base64.b64encode(value)
                data_dict[key] = encoded_bytes.decode('utf-8')
            elif isinstance(value, Enum):
                data_dict[key] = value.value

        return data_dict

    @staticmethod
    def _json_default_converter(obj):
        """数据类转换json时，不支持的类型转换规则"""
        if isinstance(obj, bytes):
            # 1. Base64 编码 (bytes -> bytes)
            encoded_bytes = base64.b64encode(obj)
            # 2. 转换为 UTF-8 字符串 (bytes -> str)
            return encoded_bytes.decode('utf-8')

        # 对于其他无法序列化的对象（如 datetime 对象），可以抛出 TypeError
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    def to_json(self) -> str:
        """数据类转json字符串"""
        data_dict = asdict(self)
        data_json = json.dumps(data_dict, default=self._json_default_converter)
        return data_json

    def _get_field_type(self, field_name: str) -> Optional[Type]:
        """辅助方法：获取属性的类型"""
        if not is_dataclass(self):
            return None
        cls = type(self)
        return cls.__annotations__.get(field_name)

    def update_from_dict(self, data_dict: dict):
        """从dict更新数据类"""
        for key, value in data_dict.items():
            if not hasattr(self, key):
                continue
            field_type = self._get_field_type(key)
            current_value = getattr(self, key, None)

            try:
                # 处理枚举类型（字符串/数字转枚举实例）
                if isinstance(field_type, type) and issubclass(field_type, enum.Enum):
                    value = field_type(value)
                # 处理基础类型转换（如字符串转数字）
                elif field_type in (int, float, bool, str) and value is not None:
                    # bool类型特殊处理（避免"False"被转成True）
                    if field_type == bool and isinstance(value, str):
                        value = value.lower() in ("true", "1", "yes")
                    else:
                        value = field_type(value)
                elif field_type is bytes:
                    if isinstance(value, bytes):
                        pass
                    elif isinstance(value, str):
                        try:
                            # 尝试Base64解码（失败则说明不是Base64字符串，跳过）
                            value = base64.b64decode(value.encode('utf-8'))
                        except (binascii.Error, ValueError):
                            value = b''

            except (ValueError, TypeError, enum.EnumError) as e:
                # 类型转换失败时打印提示，保留原值（也可改为raise抛出异常）
                print(f"警告：属性{key}赋值失败（{e}），原值：{current_value}，待赋值：{value}")
                continue

                # 4. 最终赋值（仅当值有效时）
            if value is not None:
                setattr(self, key, value)

    def update_from_json(self, json_str: str):
        """从json更新数据类"""
        data_dict = json.loads(json_str)
        self.update_from_dict(data_dict)


if __name__ == '__main__':
    # default_dict = DEFAULT_SERVICES.to_dict()
    # test_uds_service = UdsService()
    # print('==============default_dict===========')
    # pprint.pprint(default_dict)
    #
    # print('==============test_uds_service_dict===========')
    # test_uds_service.update_from_dict(default_dict)
    # test_uds_service_dict = test_uds_service.to_dict()
    # pprint.pprint(test_uds_service_dict)
    #
    # if default_dict == test_uds_service_dict:
    #     print('same')

    default_json = DEFAULT_SERVICES.to_json()
    test_uds_service = UdsService()
    print('==============default_dict===========')
    pprint.pprint(default_json)

    print('==============test_uds_service_dict===========')
    test_uds_service.update_from_json(default_json)
    test_uds_service_json = test_uds_service.to_json()
    pprint.pprint(test_uds_service_json)

    if DEFAULT_SERVICES == test_uds_service:
        print('same')

    # _type = DEFAULT_SERVICES._get_field_type('DiagnosticSessionControl')
    # print(_type)