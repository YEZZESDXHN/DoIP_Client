from dataclasses import dataclass, asdict

from doipclient.constants import TCP_DATA_UNSECURED, UDP_DISCOVERY
from doipclient.messages import RoutingActivationRequest


@dataclass
class DoIPConfig:
    # 主键字段（必填，无默认值）
    config_name: str = 'default_config'
    # 必填字段（无默认值，必须传入）
    tester_logical_address: int = 0x7e2
    dut_logical_address: int = 0x773
    dut_ipv4_address: str = '172.16.104.70'
    # 可选字段（有默认值，可省略）
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