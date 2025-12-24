import bincopy
import os
from typing import List, Tuple, Optional, Union


class FirmwareFileParser:
    """
    用于解析 S19, HEX, BIN 文件的通用类。
    底层基于 bincopy 库，提供统一的读写和数据访问接口。
    """

    def __init__(self):
        # bincopy.BinFile 是核心容器，用于存储稀疏的固件数据
        self._firmware = bincopy.BinFile()
        self._filepath = None

    def load(self, filepath: str, start_address: int = 0) -> None:
        """
        加载固件文件，自动根据扩展名识别格式。

        Args:
            filepath: 文件路径
            start_address: 仅针对 .bin 文件有效，指定二进制文件的起始加载地址
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        self._filepath = filepath
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()

        try:
            if ext in ['.s19', '.srec', '.mot']:
                self._firmware.add_srec_file(filepath)
            elif ext in ['.hex', '.ihex']:
                self._firmware.add_ihex_file(filepath)
            elif ext in ['.bin']:
                # 二进制文件没有地址信息，需要指定起始地址
                self._firmware.add_binary_file(filepath, address=start_address)
            elif ext in ['.txt']:
                # 支持 TI-TXT 格式
                self._firmware.add_ti_txt_file(filepath)
            else:
                # 尝试自动探测（bincopy 的通用加载器）
                self._firmware.add_file(filepath)
        except Exception as e:
            raise ValueError(f"Failed to parse {filepath}. Error: {str(e)}")

    def get_segments(self) -> List[Tuple[int, bytes]]:
        """
        获取固件的所有数据段。

        Returns:
            List[Tuple[address, data]]: 返回一个列表，包含 (起始地址, 数据bytes)
            这是处理非连续内存（Sparse Memory）的最佳方式。
        """
        segments = []
        for segment in self._firmware.segments:
            segments.append((segment.address, segment.data))
        return segments

    def get_merged_data(self, fill: int = 0xFF) -> Tuple[int, bytes]:
        """
        获取合并后的完整二进制数据（自动填充空洞）。

        Args:
            fill: 地址不连续时的填充字节（整数，例如 0xFF）

        Returns:
            (start_address, data): 整个固件块的起始地址和完整数据
        """
        if not self._firmware.segments:
            return 0, b""

        padding_bytes = bytes([fill])

        return self._firmware.minimum_address, self._firmware.as_binary(padding=padding_bytes)

    def get_size(self) -> int:
        """获取固件数据的实际字节大小（不包含空洞）"""
        return len(self._firmware)

    def get_range(self) -> Tuple[int, int]:
        """获取固件的地址范围 (min_addr, max_addr)"""
        if not self._firmware.segments:
            return 0, 0
        return self._firmware.minimum_address, self._firmware.maximum_address

    def export(self, output_path: str, fmt: str = 'bin', **kwargs) -> None:
        """
        将当前加载的固件转换为其他格式并保存。

        Kwargs:
            fill (int): 填充字节，默认 0xFF
            execution_addr (int): S19 文件的 S7/S8/S9 入口地址。如果不指定，默认尝试使用 0。
        """
        if fmt == 'bin':
            fill_val = kwargs.get('fill', 0xFF)
            padding_bytes = bytes([fill_val])

            with open(output_path, 'wb') as f:
                f.write(self._firmware.as_binary(padding=padding_bytes))

        elif fmt == 'hex':
            with open(output_path, 'w') as f:
                f.write(self._firmware.as_ihex())

        elif fmt == 's19':
            exec_addr = kwargs.get('execution_addr', 0xFFFFFFFF)
            self._firmware.execution_start_address = exec_addr

            with open(output_path, 'w') as f:
                f.write(self._firmware.as_srec(**kwargs))
        else:
            raise ValueError(f"Unsupported export format: {fmt}")

    def __repr__(self):
        if not self._firmware.segments:
            return "<UnifiedFirmwareParser: Empty>"

        min_addr = self._firmware.minimum_address
        max_addr = self._firmware.maximum_address
        size = len(self._firmware)
        return (f"<UnifiedFirmwareParser: {os.path.basename(self._filepath) if self._filepath else 'Memory'}, "
                f"Range: 0x{min_addr:08X}-0x{max_addr:08X}, "
                f"Size: {size} bytes, Segments: {len(self._firmware.segments)}>")


# --- 使用示例 ---

def main():
    # 1. 创建解析器
    parser = FirmwareFileParser()

    # 模拟场景：解析一个 HEX 文件
    # 假设你有一个名为 'firmware.hex' 的文件
    parser.load('C:/Workspace/3N1E/CS_test/Full_Hex_ML/VIU_3N1EML_R200RD1_111_AC_20251204_FULL.hex')
    # print(parser)

    # 为了演示，我们手动构造一些数据（模拟加载过程）
    # 在实际使用中，你只需要调用 parser.load('path/to/file.s19')
    print("--- 模拟加载数据 ---")
    # parser._firmware.add_binary(b'\x01\x02\x03\x04', address=0x08000000)  # Segment 1
    # parser._firmware.add_binary(b'\xAA\xBB', address=0x08000010)  # Segment 2 (中间有空洞)

    # 2. 获取分段数据 (统一接口)
    # print("\n--- 获取数据段 (Segments) ---")
    # for addr, data in parser.get_segments():
    #     print(f"Address: 0x{addr:08X} | Length: {len(data)} | Data: {data.hex().upper()}")
    #
    # # 3. 获取合并后的二进制流 (统一接口)
    # # 这常用于计算 CRC 或者刷写整个 Flash
    # start_addr, blob = parser.get_merged_data(fill=0xFF)
    # print(f"\n--- 合并数据 (Fill 0xFF) ---")
    # print(f"Start: 0x{start_addr:08X}")
    # print(f"Raw Blob (Hex): {blob.hex().upper()}")

    # 4. 格式转换 (例如 hex 转 bin, 或 s19 转 hex)
    # parser.export('output.bin', fmt='bin')
    parser.export('C:/Workspace/3N1E/CS_test/Full_Hex_ML/test_VIU_3N1EML_R200RD1_111_AC_20251204_FULL.s19', fmt='s19')
    print("\n--- 格式转换支持 ---")
    print("Supported exports: .bin, .hex, .s19")


if __name__ == "__main__":
    main()