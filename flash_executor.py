import logging
import os
import re
from time import sleep

from PySide6.QtCore import Signal, QObject

from FirmwareFileParser import FirmwareFileParser
from UDSClient import QUDSClient
from UI.FlashConfigPanel import FlashConfig
from global_variables import gFlashVars, FlashBaseVars

logger = logging.getLogger('UDSTool.' + __name__)


class QFlashExecutor(QObject):
    write_signal = Signal(str, str)

    def __init__(self, uds_client: QUDSClient, flash_config: FlashConfig, flash_file_paths: dict):
        super().__init__()
        self.uds_client = uds_client
        self.flash_config = flash_config
        self.flash_file_paths = flash_file_paths
        self.flash_file_parsers: dict[str: FirmwareFileParser] = {}
        self.flash_vars = gFlashVars
        self._array_pattern = re.compile(r'^(.+)\[(\d+)\]$')

    def start_flash(self):
        self.write_signal.emit("Flash", f"开始加载文件")
        self.flash_file_parsers.clear()
        try:
            for file in self.flash_config.files:
                if not os.path.exists(self.flash_file_paths[file.name]):
                    self.write_signal.emit("Flash", f"{file.name}路径错误，{self.flash_file_paths[file.name]}")
                else:
                    self.flash_file_parsers[file.name] = FirmwareFileParser()
                    self.flash_file_parsers[file.name].load(self.flash_file_paths[file.name])
                    if file.name not in self.flash_vars.files_vars:
                        return
                    self.flash_vars.files_vars[file.name].flash_block_vars.clear()
                    for addr, data in self.flash_file_parsers[file.name].get_segments():
                        base_vars = FlashBaseVars()
                        base_vars.addr = addr
                        base_vars.size = len(data)
                        base_vars.data = data

                        self.flash_vars.files_vars[file.name].flash_block_vars.append(base_vars)
        except Exception as e:
            logger.exception(f'{str(e)}')
            return

        self.write_signal.emit("Flash", f"开始执行刷写步骤")
        for step in self.flash_config.steps:
            try:
                self.write_signal.emit("Flash", f"{step.step_name}")

                if step.data[0] == 0x27 and step.data[1] % 2 == 0 and self.uds_client.security_key:
                    send_data = step.data + self.uds_client.security_key
                else:
                    send_data = step.data
                    for ext in step.external_data:
                        if '[' in ext:
                            # 尝试用正则解析 "name[index]"
                            match = self._array_pattern.match(ext)
                            if match:
                                ext_name = match.group(1)
                                # '_' : 分割符
                                # 1   : 只分割 1 次（确保只把最后一个部分切掉）
                                # [0] : 取分割后的第一部分（即前面的内容）
                                file_name = ext_name.rsplit('_', 1)[0]
                                ext_suffix = ext_name.rsplit('_', 1)[1]
                                index = int(match.group(2))
                                if file_name not in self.flash_vars.files_vars and \
                                        len(self.flash_vars.files_vars[file_name].flash_block_vars) < index + 1:
                                    return
                                ext_datas = self.flash_vars.files_vars[file_name].flash_block_vars[index]
                                if not hasattr(ext_datas, ext_suffix):
                                    return
                                ext_data = getattr(ext_datas, ext_suffix)
                                if isinstance(ext_data, int):
                                    if ext_suffix == 'size':
                                        ext_data = ext_data.to_bytes(
                                            length=self.flash_config.transmission_parameters.memory_size_parameter_length,
                                            byteorder='big',
                                            signed=False
                                        )
                                    elif ext_suffix == 'addr':
                                        ext_data = ext_data.to_bytes(
                                            length=self.flash_config.transmission_parameters.memory_address_parameter_length,
                                            byteorder='big',
                                            signed=False
                                        )
                                    else:
                                        ext_data = ext_data.to_bytes(
                                            length=4,
                                            byteorder='big',
                                            signed=False
                                        )
                                elif isinstance(getattr(ext_data, ext_suffix), bytes):
                                    pass
                                else:
                                    ext_data = b''
                                send_data = send_data + ext_data

                            else:
                                self.write_signal.emit("Flash", f"{ext}解析失败")

                resp = self.uds_client.send_payload(payload=send_data, display_trace=1)
                if resp:
                    if resp.code == 0:
                        self.write_signal.emit("Flash", f"{step.step_name} 执行成功")
                    else:
                        self.write_signal.emit("Flash", f"{step.step_name} 执行失败，code_name: {resp.code_name}")
                        try:
                            self.write_signal.emit("Flash", f"data:{resp.original_payload.hex(' ')}")
                        except:
                            pass
                        return
                else:
                    return
            except Exception as e:
                self.write_signal.emit("Flash", f"{e}")
                logger.exception(f"{str(e)}")
                return

    def stop_flash(self):
        print(self.flash_vars)
        print(self.flash_config)


