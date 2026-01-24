import importlib.util
import logging
import os
import sys
from time import sleep
from typing import List

from PySide6.QtCore import QObject, Slot, Signal

from app.core.db_manager import DBManager
from app.core.uds_client import QUDSClient
from app.external_scripts.ScriptAPI import ScriptAPI
from app.user_data import ExternalScriptConfig, ExternalScriptRunState
from app.windows.ExternalScript_Panel import ExternalScriptFinishType

logger = logging.getLogger('UDSTool.' + __name__)


class QExternalScriptsExecutor(QObject):
    write_signal = Signal(str, str)
    run_finish = Signal(ExternalScriptFinishType)
    run_state = Signal(ExternalScriptRunState, int)
    run_start = Signal()

    def __init__(self, uds_client: QUDSClient, db_manager: DBManager, config_name):
        super().__init__()
        self.config_name = config_name
        self.db_manager = db_manager
        self.uds_client = uds_client
        self.external_module = None
        self.external_scripts: List[ExternalScriptConfig] = []
        self.script_api = ScriptAPI(uds_client=self.uds_client, write_signal=self.write_signal)
        self.stop_flag = False

    def load_external_script(self, file_path) -> bool:
        if not os.path.exists(file_path):
            logger.error(f"错误: 文件不存在 {file_path}")
            return False
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
            self.script_api.script_name = os.path.basename(file_path)
            # 尝试调用 on_load
            if hasattr(self.external_module, 'on_load'):
                self.external_module.on_load(self.script_api)
            else:
                logger.warning("警告: 脚本中没找到 on_load 函数")
            return True
        except Exception as e:
            logger.exception(f"加载阶段出错: {e}")
            self.external_module = None  # 加载失败清空
            return False

    @Slot()
    def run_external_script(self):
        if not self.external_module:
            logger.warning("错误: 未加载任何模块")
            return

        try:
            if hasattr(self.external_module, 'main'):
                self.external_module.main(self.script_api)
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
                self.external_module.on_stop(self.script_api)
            else:
                logger.warning("提示: 脚本中未定义 on_stop (跳过清理)")
        except Exception as e:
            logger.exception(f"停止阶段出错: {e}")

        self.external_module = None

    def run_external_scripts(self):
        self.run_start.emit()
        self.external_scripts = self.db_manager.get_external_script_list_by_config(self.config_name)
        for index, script in enumerate(self.external_scripts):
            if not script.enable:
                continue
            if self.stop_flag:
                # self.run_state.emit(ExternalScriptRunState.RunningFailed, index)
                self.run_finish.emit(ExternalScriptFinishType.fail)
                return
            script_path = script.path
            if self.load_external_script(script_path):
                self.run_state.emit(ExternalScriptRunState.RunningPassed, index)
                self.run_external_script()
            # sleep(0.2)
        finish_type = ExternalScriptFinishType.success
        self.run_finish.emit(finish_type)

    def stop_run_external_scripts(self):
        self.stop_flag = True
