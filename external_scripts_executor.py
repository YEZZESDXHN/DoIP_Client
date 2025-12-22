import importlib.util
import logging
import os
import sys

from PySide6.QtCore import QObject, Slot

from Context import RuntimeContext
from UDSClient import QUDSClient

logger = logging.getLogger('UDSOnIPClient.' + __name__)


class QExternalScriptsExecutor(QObject):
    def __init__(self, uds_client: QUDSClient):
        super().__init__()
        self.uds_client = uds_client
        self.external_module = None
        self.external_script_path: str = ''

    @Slot(str)
    def load_external_script(self):
        file_path = self.external_script_path
        if not os.path.exists(file_path):
            logger.error(f"错误: 文件不存在 {file_path}")
            return
        script_dir = os.path.dirname(file_path)
        if script_dir not in sys.path:
            sys.path.append(script_dir)
        try:
            logger.info(f"--- 正在加载模块: {file_path} ---")
            spec = importlib.util.spec_from_file_location("external_script", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 保存模块到实例变量
            self.external_module = module

            # 尝试调用 on_load
            if hasattr(self.external_module, 'on_load'):
                self.external_module.on_load(self.uds_client)
            else:
                logger.warning("警告: 脚本中没找到 on_load 函数")

        except Exception as e:
            logger.exception(f"加载阶段出错: {e}")
            self.external_module = None  # 加载失败清空

    @Slot()
    def run_external_script(self):
        if not self.external_module:
            logger.warning("错误: 未加载任何模块")
            return

        try:
            if hasattr(self.external_module, 'main'):
                context = RuntimeContext(self.uds_client)
                self.external_module.main(context)
            else:
                logger.error("错误: 脚本中未定义 main")
        except Exception as e:
            pass

    @Slot()
    def stop_external_script(self):
        if not self.external_module:
            return

        try:
            if hasattr(self.external_module, 'on_stop'):
                self.external_module.on_stop(self.uds_client)
            else:
                logger.warning("提示: 脚本中未定义 on_stop (跳过清理)")
        except Exception as e:
            logger.exception(f"停止阶段出错: {e}")

        self.external_module = None

