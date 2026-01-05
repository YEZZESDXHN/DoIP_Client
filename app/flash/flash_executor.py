import logging
import os
import re
from enum import Enum
from time import sleep
from typing import Literal, Dict, Callable
from PySide6.QtCore import Signal, QObject

from app.core.ChecksumStrategy import ALGORITHM_REGISTRY, ChecksumStrategy
from app.core.FirmwareFileParser import FirmwareFileParser
from app.core.uds_client import QUDSClient
from app.global_variables import gFlashVars, FlashBaseVars
from app.windows.FlashConfigPanel import FlashConfig, Step

logger = logging.getLogger('UDSTool.' + __name__)


class FlashFinishType(Enum):
    success = "刷写成功"
    fail = "刷写失败"
    stop = "刷写终止"


def flash_wait(secs: float) -> None:
    sleep(secs)


FLASH_CALL: Dict[str, Callable] = {
    "Wait": flash_wait,
}


class QFlashExecutor(QObject):
    write_signal = Signal(str, str)
    flash_progress = Signal(int)
    flash_range = Signal(int)
    flash_finish = Signal(FlashFinishType)

    def __init__(self, uds_client: QUDSClient, flash_config: FlashConfig, flash_file_paths: dict):
        super().__init__()
        self.uds_client = uds_client
        self.flash_config = flash_config
        self.flash_file_paths = flash_file_paths
        self.flash_file_parsers: dict[str: FirmwareFileParser] = {}
        self.flash_vars = gFlashVars
        self._array_pattern = re.compile(r'^(.+)\[(\d+)]$')
        self.flash_step_num = 0
        self.display_trace = 0
        self.stop_flash_flag = False

    def get_checksum_calculator(self) -> ChecksumStrategy:
        """
        工厂方法：根据当前的 checksum_type 返回对应的算法实例
        """
        strategy_class = ALGORITHM_REGISTRY.get(self.flash_config.transmission_parameters.checksum_type)
        if not strategy_class:
            raise NotImplementedError(f"算法 {self.flash_config.transmission_parameters.checksum_type} 尚未实现")
        return strategy_class()

    def compute_checksum(self, cal_data: bytes) -> bytes:
        """
        快捷方法：直接计算数据的校验和
        """
        calculator = self.get_checksum_calculator()
        return calculator.calculate(cal_data)

    def calculate_flash_step_num(self) -> int:
        step_num = 0
        for step in self.flash_config.steps:
            _count = 1
            if step.data[0] == 0x36:
                external_data_len = len(self.get_external_data(step.external_data))
                _count = int(
                    external_data_len / (self.flash_config.transmission_parameters.max_number_of_block_length - 2)) + 1
            else:
                pass
            step_num = step_num + _count
        return step_num

    def start_flash(self):
        flash_progress = 0
        self.write_signal.emit("Flash", f"开始加载文件")
        self.stop_flash_flag = False

        self.flash_file_parsers.clear()
        try:
            for file in self.flash_config.files:
                if self.stop_flash_flag:
                    self.flash_finish.emit(FlashFinishType.stop)
                    return
                if not os.path.exists(self.flash_file_paths[file.name]):
                    self.write_signal.emit("Flash", f"{file.name}路径错误，{self.flash_file_paths[file.name]}")
                else:
                    self.flash_file_parsers[file.name] = FirmwareFileParser()
                    self.flash_file_parsers[file.name].load(self.flash_file_paths[file.name])
                    if file.name not in self.flash_vars.files_vars:
                        return
                    self.flash_vars.files_vars[file.name].flash_block_vars.clear()
                    for addr, block_data in self.flash_file_parsers[file.name].get_segments():
                        base_vars = FlashBaseVars()
                        base_vars.addr = addr
                        base_vars.size = len(block_data)
                        base_vars.data = bytes(block_data)
                        base_vars.checksum = self.compute_checksum(block_data)

                        self.flash_vars.files_vars[file.name].flash_block_vars.append(base_vars)

        except Exception as e:
            self.write_signal.emit("Flash", f"文件加载失败，{e}")
            self.flash_finish.emit(FlashFinishType.fail)
            logger.exception(f'{str(e)}')
            return

        self.flash_step_num = self.calculate_flash_step_num()
        self.flash_range.emit(self.flash_step_num)
        self.flash_progress.emit(flash_progress)

        self.write_signal.emit("Flash", f"开始执行刷写步骤")
        for step in self.flash_config.steps:
            if self.stop_flash_flag:
                self.flash_finish.emit(FlashFinishType.stop)
                return
            try:
                if step.is_call:
                    try:
                        self.write_signal.emit("Flash", f"执行函数{step.step_name}")
                        FLASH_CALL[step.step_name](int(step.external_data[0])/1000)
                    except Exception as e:
                        self.write_signal.emit("Flash", f"函数 {step.step_name} 执行失败：{e}")
                        self.flash_finish.emit(FlashFinishType.fail)
                        return
                else:
                    self.write_signal.emit("Flash", f"开始执行{step.step_name}")
                    send_data_list = self.construct_send_data_list(step)
                    for send_data in send_data_list:
                        if self.stop_flash_flag:
                            self.flash_finish.emit(FlashFinishType.stop)
                            return
                        resp = self.uds_client.send_payload(payload=send_data, display_trace=self.display_trace)
                        if resp:
                            if resp.code == 0:
                                try:
                                    if step.exp_resp_data:
                                        exp_data_len = len(step.exp_resp_data)
                                        if len(resp.original_payload) < exp_data_len:
                                            self.write_signal.emit("Flash", f"执行失败: Exp data:{step.exp_resp_data.hex(' ')},Resp data: {resp.original_payload}")
                                            self.flash_finish.emit(FlashFinishType.fail)
                                            return
                                        else:
                                            if step.exp_resp_data != resp.original_payload[:exp_data_len]:
                                                self.write_signal.emit("Flash",
                                                                       f"执行失败: Exp data:{step.exp_resp_data.hex(' ')},Resp data: {resp.original_payload}")
                                                return

                                except Exception as e:
                                    self.write_signal.emit("Flash",f"执行失败: {e}")
                                    self.flash_finish.emit(FlashFinishType.fail)
                                    return
                            else:
                                self.write_signal.emit("Flash", f"{step.step_name} 执行失败，code_name: {resp.code_name}")
                                try:
                                    self.write_signal.emit("Flash", f"data:{resp.original_payload.hex(' ')}")
                                except:
                                    pass
                                self.flash_finish.emit(FlashFinishType.fail)
                                return
                        else:
                            self.flash_finish.emit(FlashFinishType.fail)
                            return
                        flash_progress += 1
                        self.flash_progress.emit(flash_progress)
                    self.write_signal.emit("Flash", f"{step.step_name}执行成功")
                self.write_signal.emit("Flash", f"{step.step_name} 执行成功")

            except Exception as e:
                self.flash_finish.emit(FlashFinishType.fail)
                self.write_signal.emit("Flash", f"{e}")
                logger.exception(f"{str(e)}")
                return
        self.flash_finish.emit(FlashFinishType.success)
        self.flash_progress.emit(self.flash_step_num)

    def get_external_data(self, external_data: list[str], byteorder: Literal["little", "big"] = 'big') -> bytes:
        data = b''

        try:
            for ext in external_data:
                if '[' in ext:
                    # 尝试用正则解析 "name_crc[index]"
                    match = self._array_pattern.match(ext)
                    if match:
                        # match.group(1) ：返回正则中「第一个括号」匹配到的内容，“name_crc”
                        ext_name = match.group(1)

                        # '_' : 分割符
                        # 1   : 只分割 1 次（确保只把最后一个部分切掉）
                        # [0] : 取分割后的第一部分（即前面的内容）
                        file_name = ext_name.rsplit('_', 1)[0]  # 获取name
                        ext_suffix = ext_name.rsplit('_', 1)[1]  # 获取后缀crc
                        index = int(match.group(2))  # 获取下标
                        if file_name not in self.flash_vars.files_vars and \
                                len(self.flash_vars.files_vars[file_name].flash_block_vars) < index + 1:
                            return b''
                        ext_datas = self.flash_vars.files_vars[file_name].flash_block_vars[index]
                        if not hasattr(ext_datas, ext_suffix):
                            return b''
                        ext_data = getattr(ext_datas, ext_suffix)
                        if isinstance(ext_data, int):
                            length = 4
                            if ext_suffix == 'size':
                                length = self.flash_config.transmission_parameters.memory_size_parameter_length
                            elif ext_suffix == 'addr':
                                length = self.flash_config.transmission_parameters.memory_address_parameter_length
                            ext_data = ext_data.to_bytes(
                                length=length,
                                byteorder=byteorder,
                                signed=False
                            )
                        elif isinstance(ext_data, bytes):
                            pass
                        else:
                            ext_data = b''
                        data = data + ext_data

                    else:
                        self.write_signal.emit("Flash", f"{ext}解析失败")
        except Exception as e:
            logger.exception(f"获取external_data失败，{e}")
        return data

    def construct_send_data_list(self, step: Step) -> list[bytes]:
        send_data_list = []
        external_data = self.get_external_data(step.external_data)
        if step.data[0] == 0x27 and step.data[1] % 2 == 0 and self.uds_client.security_key:
            send_data = step.data + self.uds_client.security_key
            send_data_list.append(send_data)
        elif step.data[0] == 0x36:
            # 待发送的完整数据 = 原始指令段 + 外部补充数据
            total_send_data = step.data + external_data
            # 获取DOIP传输的单包最大长度限制
            max_block_len = self.flash_config.transmission_parameters.max_number_of_block_length
            # 核心：每一包都有【0x36(1字节)+序号(1字节)】，所以数据区要预留2字节头部
            max_data_len_per_pkg = max_block_len - 2

            # 判断：数据总长度超过阈值 → 需要分包发送
            if len(total_send_data) > max_block_len:
                seq = 0x01  # DOIP分包序号：从01开始自增
                current_pos = 1  # 数据读取游标，标记当前分包起始位置,第一字节为36，跳过
                total_data_len = len(total_send_data)

                # 循环分包，直到所有数据切分完毕
                while current_pos < total_data_len:
                    # 计算本次分包的实际数据长度（最后一包自动取剩余长度）
                    remain_data_len = total_data_len - current_pos
                    cur_data_len = min(remain_data_len, max_data_len_per_pkg)
                    # 截取当前分包的业务数据段
                    pkg_data = total_send_data[current_pos:current_pos + cur_data_len]

                    send_pkg = bytes([0x36, seq]) + pkg_data
                    send_data_list.append(send_pkg)

                    # 游标后移 + 序号自增
                    current_pos += cur_data_len
                    seq += 1
                    # 鲁棒性防护：序号最大为0xFF(单字节最大值)，超出后重置为01，防止溢出
                    if seq > 0xFF:
                        seq = 0x00

            # 数据长度未超限 → 无需分包，原始拼接数据直接发送
            else:
                pkg_data = total_send_data[1:]

                send_pkg = bytes([0x36, 1]) + pkg_data
                send_data_list.append(send_pkg)
        else:
            send_data = step.data + external_data
            send_data_list.append(send_data)
        return send_data_list



if __name__ == '__main__':
    print('start')
    step_36 = Step()
    step_36.step_name = 'step_36'
    step_36.data = b'\x36'
    step_36.external_data.append('test_data[0]')

    _flash_config = FlashConfig()
    _flash_config.transmission_parameters.max_number_of_block_length = 18
    from app.windows.FlashConfigPanel import FileConfig, FlashConfig, Step

    _flash_config.files.append(FileConfig(name='test'))
    _flash_config.steps.append(step_36)

    from app.global_variables import FlashFileVars

    test_data_0_FileVars = FlashFileVars()

    test_data_0_FlashBaseVars = FlashBaseVars()


    def gen_hex_bytes(length: int) -> bytes:
        """
        生成指定长度的bytes，内容0x00~0x0f循环填充
        :param length: 需要的bytes长度
        :return: 目标bytes对象
        """
        return bytes(i % 16 for i in range(length))

    test_data_0_FlashBaseVars.data = gen_hex_bytes(15)

    test_data_0_FileVars.flash_block_vars.append(test_data_0_FlashBaseVars)
    gFlashVars.files_vars['test'] = test_data_0_FileVars

    flash_executor = QFlashExecutor(uds_client=None, flash_config=_flash_config, flash_file_paths=None)
    send_list = flash_executor.construct_send_data_list(step_36)
    # print(test_data_0_FlashBaseVars.data.hex(' '))
    for _data in send_list:
        print(_data.hex(' '))

