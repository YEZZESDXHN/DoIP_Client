from typing import Union

class CanPluginAdapter(CANAdapter):
    def __init__(self): super().__init__("tosun")

    def get_display_text(self, config):
        return f"{config['interface']} - {config['name']} - channel {config['channel']}  {config['sn']}"

    def open_bus(self, interface, timing: Union[BitTiming, BitTimingFd]) -> can.Bus:
        try:
            # logger.debug(f"[*] 正在连接到 {interface['interface']} (通道: {interface['channel']}) ...")
            can_bus = can.Bus(**interface, timing=timing, app_name=APP_NAME)
            # if isinstance(timing, BitTimingFd):
            #     self.info_signal.emit(f"CAN接口初始化成功(CANFD)，nom_bitrate：{timing.nom_bitrate},"
            #                           f"nom_sample_point:{timing.nom_sample_point},"
            #                           f"data_bitrate:{timing.data_bitrate},"
            #                           f"data_sample_point:{timing.data_sample_point}")
            # elif isinstance(timing, BitTiming):
            #     self.info_signal.emit(
            #         f"CAN接口初始化成功(CAN)，bitrate:{timing.bitrate},sample_point:{timing.sample_point}")
            #
            # logger.debug(f"[+] 连接成功！总线状态: {can_bus.state}")
            return can_bus
        except Exception as e:
            return None

    def close_bus(self, bus):
        bus.shutdown()
