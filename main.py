import configparser
import logging.config
import os
import sys
from PySide6.QtWidgets import QApplication

from app.windows.MainWindow import MainWindow

# # 日志配置
# logging.config.fileConfig("./logging.conf")
# logger = logging.getLogger('UDSTool')


def setup_logging(config_file="./logging.conf", logger_name="UDSTool"):
    """
    加载日志配置，并自动创建日志存放目录

    Args:
        config_file: 日志配置文件路径
        logger_name: 要获取的 logger 名称

    Returns:
        配置好的 logger 实例
    """
    # 1. 先解析配置文件，获取日志文件路径
    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf-8')

    # 存储所有需要检查的日志路径
    log_paths = []

    # 遍历配置文件中的所有 handler
    for section in config.sections():
        if section.startswith('handler_'):
            # 获取 handler 的参数
            handler_args = config.get(section, 'args', fallback='')

            # 解析 args 中的文件路径（通常是元组形式，第一个元素是路径）
            # 例如：args=('logs/udstool.log', 'a', 'utf-8')
            if handler_args and '(' in handler_args and ')' in handler_args:
                # 提取括号内的内容并分割
                args_content = handler_args.strip('()').strip()
                # 分割参数（处理带引号的字符串）
                args_parts = args_content.split(',')
                if args_parts:
                    # 提取第一个参数（日志文件路径）并清理引号和空格
                    log_file_path = args_parts[0].strip().strip("'\"")
                    if log_file_path:
                        log_paths.append(log_file_path)

    # 2. 检查并创建日志目录
    for log_file in log_paths:
        # 获取日志文件所在的目录
        log_dir = os.path.dirname(log_file)

        # 如果目录不为空且不存在，则创建
        if log_dir and not os.path.exists(log_dir):
            try:
                # 递归创建目录，exist_ok=True 避免目录已存在时报错
                os.makedirs(log_dir, exist_ok=True)
                print(f"日志目录不存在，已自动创建: {log_dir}")
            except Exception as e:
                print(f"创建日志目录失败: {log_dir}, 错误: {e}")
                raise

    # 3. 加载 logging 配置
    logging.config.fileConfig(config_file)

    # 4. 获取 logger 实例
    _logger = logging.getLogger(logger_name)

    return _logger


if __name__ == "__main__":
    logger = setup_logging("./logging.conf", "UDSTool")
    app = QApplication(sys.argv)
    app.setStyle("WindowsVista")
    # app.setStyle("Fusion")
    w = MainWindow()
    version = 'v0.1.7'
    w.custom_status_bar.label_Version.setText(version)
    w.show()
    sys.exit(app.exec())
