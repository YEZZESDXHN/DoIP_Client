from typing import Dict

import ifaddr


def get_ethernet_ips() -> Dict:
    """
    获取当前电脑上所有被识别为有线连接 (Ethernet) 的网卡 IPv4 地址。

    Returns:
        一个字典，键是网卡名称，值是其 IPv4 地址列表 (不包含 CIDR 前缀)。
        示例: {'Ethernet': ['172.16.10.5'], 'eth0': ['192.168.1.10']}
    """
    # 常见的以太网接口名称关键词 (需要根据具体操作系统调整)
    ETHERNET_KEYWORDS = [
        'eth',  # Linux/Unix/macOS (e.g., eth0, en0)
        'ethernet',  # Windows/macOS (e.g., Ethernet, enpXsY)
        'lan',  # Local Area Network
        'cable',  # Cable connection
        'pci',  # PCI network card
        'local area connection'  # Windows (old/localized names)
    ]
    ethernet_ips = {}

    try:
        adapters = ifaddr.get_adapters()

        for adapter in adapters:
            # 1. 过滤回环地址
            if adapter.nice_name.lower() in ('loopback', 'lo'):
                continue

            # 2. 检查名称是否包含以太网关键词 (大小写不敏感)
            is_ethernet = False
            for keyword in ETHERNET_KEYWORDS:
                if keyword in adapter.nice_name.lower():
                    is_ethernet = True
                    break

            # 如果适配器名称被识别为有线接口
            if is_ethernet:
                ips_v4 = []

                # 3. 遍历IP地址，只获取IPv4
                for ip in adapter.ips:
                    # 检查是否是IPv4，并且地址不是回环地址（127.x.x.x）
                    if ip.is_IPv4 and not ip.ip.startswith('127.'):
                        # 只返回IP地址，不带CIDR前缀
                        ips_v4 = ip.ip

                # 4. 记录有效地址
                if ips_v4:
                    ethernet_ips[adapter.nice_name] = ips_v4

    except Exception as e:
        print(f"获取网卡信息失败: {e}")
        return {}

    return ethernet_ips


def hex_str_to_int(hex_str: str) -> int:
    """
    将十六进制字符串转换为整数。失败时抛出包含输入str和错误信息的 ValueError。

    Args:
        hex_str: 待转换的十六进制字符串。

    Returns:
        转换后的整数值。

    Raises:
        ValueError: 如果字符串不是有效的十六进制格式，错误信息将包含输入str和原始错误详情。
    """

    # 确保输入是字符串
    if not isinstance(hex_str, str):
        # 如果输入类型错误，抛出 Type Error
        raise TypeError(f"输入类型错误，需要字符串，但收到了 {type(hex_str).__name__}。原始输入: '{hex_str}'")

    # 清理空格并转换为小写，便于 int() 处理
    cleaned_str = hex_str.strip().lower()

    try:
        # base=16 进行十六进制转换
        result = int(cleaned_str, 16)
        return result

    except ValueError as e:
        # 捕获原始的 ValueError，并抛出包含定制信息的新的 ValueError
        custom_error_msg = (
            f"十六进制转换失败。输入字符串: '{hex_str}\n"
            f"详细原因: {e}"
        )
        raise ValueError(custom_error_msg)