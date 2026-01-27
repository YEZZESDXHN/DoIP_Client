import html
import importlib.util
import json
import logging
import os
import sys
from datetime import datetime
from time import sleep
from typing import List, Optional

import pytest
from PySide6.QtCore import QObject, Slot, Signal
from _pytest.config import ExitCode
from pytest_html import extras

from app.core.db_manager import DBManager
from app.core.uds_client import QUDSClient
from app.external_scripts.ScriptAPI import ScriptAPI
from app.user_data import ExternalScriptConfig, ExternalScriptRunState, ExternalScriptsRunState
from contextlib import redirect_stdout, redirect_stderr

logger = logging.getLogger('UDSTool.' + __name__)


class UDSTestPlugin:
    """
    这是一个自定义的 Pytest 插件。
    它的作用是将应用程序中的 ScriptAPI 实例注入到 pytest 的测试用例中。
    """
    def __init__(self, api_instance):
        self._api = api_instance

    @pytest.fixture(scope="session")
    def api(self):
        """
        定义名为 'api' 的 fixture。
        测试脚本中的 test_xxx(api) 函数将自动获得这个对象。
        """
        return self._api

    @pytest.fixture(scope="function", autouse=True)
    def _manage_test_lifecycle(self):
        """
        autouse=True: 每个测试用例会自动执行此 fixture，无需手动传入参数
        """
        # === Setup 阶段 ===
        # 重置 API 数据和标志位
        self._api._reset_report_state()

        # 执行测试用例
        yield

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        """
        这是 Pytest 的钩子函数，用于在生成报告时处理结果。
        我们在这里把 api.report_steps 转换成 HTML 表格。
        """
        outcome = yield
        report = outcome.get_result()

        # 我们只关心测试执行阶段 (call) 的报告，不关心 setup/teardown
        if report.when == "call":
            # 如果 Pytest 认为测试 Passed，但我们的 API 记录里有 Fail
            if report.outcome == "passed" and not getattr(self._api, '_is_success', True):
                # 强行篡改结果为 failed
                report.outcome = "failed"
            steps = getattr(self._api, 'report_steps', [])

            if steps:
                # 生成自定义 HTML 表格
                html_table = self._generate_html_table(steps)
                # 将 HTML 添加到报告的 'extra' 部分
                report.extra = getattr(report, "extra", [])
                report.extra.append(extras.html(html_table))

    def _generate_html_table(self, steps):
        """
        生成类似截图样式的 HTML 表格，自动适配 data 的数据类型
        """
        # 定义 CSS 样式
        style = """
        <style>
            .uds-table { 
                width: 100%; 
                border-collapse: collapse; 
                font-family: Arial, sans-serif; 
                font-size: 13px; 
                margin-top: 10px; 
                color: #333; /* 设置默认文字颜色为深灰色 */
            }
            .uds-table th { 
                background-color: #d0d0d0; /* 表头背景变深 (#e0e0e0 -> #d0d0d0) */
                text-align: left; 
                padding: 8px; 
                border: 1px solid #999; /* 边框变深 (#ccc -> #999) */
                font-weight: bold;
            }
            .uds-table td { 
                padding: 8px; 
                border: 1px solid #999; /* 边框变深 (#ccc -> #999) */
                vertical-align: top; 
            }
            .uds-row-step { 
                background-color: #f0f0f0; /* 普通行背景变深 (#f9f9f9 -> #f0f0f0) */
            }
            /* Pass/Fail 的颜色已经很深了，保持不变 */
            .uds-result-pass { background-color: #28a745; color: white; text-align: center; font-weight: bold; }
            .uds-result-fail { background-color: #dc3545; color: white; text-align: center; font-weight: bold; }
            
            .uds-data-block { 
                background-color: #e0e0e0; /* 数据块背景变深 (#eee -> #e0e0e0) */
                padding: 5px; 
                margin-top: 5px; 
                border-left: 3px solid #333; /* 左侧边框变深 (#666 -> #333) */
                font-family: monospace; 
                word-break: break-all; 
            }
            .uds-data-pre { white-space: pre-wrap; margin: 0; } 
        </style>
        """

        rows_html = ""
        for step in steps:
            # 1. 处理结果列样式 (Pass/Fail)
            res_class = ""
            res_text = str(step['result'])
            if res_text.lower() == "pass":
                res_class = "uds-result-pass"
            elif res_text.lower() == "fail":
                res_class = "uds-result-fail"

            # 2. 核心逻辑：根据 data 类型自适应展示内容
            data_html = ""
            raw_data = step['data']

            if raw_data is not None:
                display_content = ""
                label = "Data"  # 默认标签

                # --- Case A: Bytes / ByteArray (显示为 Hex) ---
                if isinstance(raw_data, (bytes, bytearray)):
                    label = "Hex Dump"
                    # 转换成 "10 02 FF" 格式
                    display_content = " ".join([f"{b:02X}" for b in raw_data])

                # --- Case B: List / Dict (显示为 JSON 结构) ---
                elif isinstance(raw_data, (list, dict)):
                    label = "Structure"
                    try:
                        # 格式化 JSON，ensure_ascii=False 保证中文正常显示
                        json_str = json.dumps(raw_data, indent=2, ensure_ascii=False)
                        # 使用 <pre> 标签保留缩进格式
                        display_content = f"<pre class='uds-data-pre'>{html.escape(json_str)}</pre>"
                    except Exception:
                        # 如果序列化失败，退化为普通字符串
                        display_content = html.escape(str(raw_data))

                # --- Case C: String / 其他 (普通显示) ---
                elif isinstance(raw_data, (int, float)):
                    label = "int/float"
                    display_content = html.escape(str(raw_data))
                else:
                    label = "Details"
                    display_content = html.escape(str(raw_data))

                # 组装数据块 HTML
                data_html = f"""
                <div class="uds-data-block">
                    <strong>{label}:</strong><br>
                    {display_content}
                </div>
                """

            # 3. 组装整行 HTML
            row = f"""
            <tr class="uds-row-step">
                <td style="width: 120px;">{step['timestamp']}</td>
                <td style="width: 100px;">{step['type']}</td>
                <td>
                    <strong>{html.escape(str(step['title']))}</strong>
                    {data_html}
                </td>
                <td style="width: 80px;" class="{res_class}">{res_text}</td>
            </tr>
            """
            rows_html += row

        table_html = f"""
        {style}
        <table class="uds-table">
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Test Step</th>
                    <th>Title / Data</th>
                    <th>Result</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        """
        return table_html


class QExternalScriptsExecutor(QObject):
    write_signal = Signal(str, str)
    scripts_run_state = Signal(ExternalScriptsRunState)
    scripts_run_finish_state = Signal(ExternalScriptsRunState)
    script_run_state = Signal(ExternalScriptRunState, int)
    scripts_run_start = Signal()

    def __init__(self, uds_client, db_manager, config_name):
        super().__init__()
        self.config_name = config_name
        self.db_manager = db_manager
        self.uds_client = uds_client
        self.external_scripts: List[ExternalScriptConfig] = []

        # 初始化 API
        self.script_api = ScriptAPI(uds_client=self.uds_client, write_signal=self.write_signal)
        self.uds_test_plugin = UDSTestPlugin(self.script_api)

        self.stop_flag = False
        self.run_script_index = 0
        self.current_script_path = ""

    def _prepare_environment(self, file_path) -> bool:
        """
        检查文件是否存在，并设置 sys.path 以便脚本能 import 同目录下的其他文件
        """
        if not os.path.exists(file_path):
            logger.error(f"错误: 文件不存在 {file_path}")
            return False

        script_dir = os.path.dirname(file_path)
        if script_dir not in sys.path:
            sys.path.append(script_dir)

        self.script_api.script_name = os.path.basename(file_path)
        self.current_script_path = file_path
        return True

    @Slot()
    def run_external_script(self) -> Optional[int]:
        """
        运行单个脚本。返回 True 表示通过，False 表示失败/停止。
        """
        if not self.current_script_path:
            return None

        # 1. 准备报告路径
        # 建议放在 ./reports/config_name/script_name/time.html
        base_report_dir = os.path.join(os.getcwd(), "reports", self.config_name)
        os.makedirs(base_report_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_basename = os.path.splitext(os.path.basename(self.current_script_path))[0]
        report_path = os.path.join(base_report_dir, f"{script_basename}_{timestamp}.html")

        self.script_api.write(f"--- 开始执行: {script_basename} ---")
        self.script_api.write(f"报告路径: {report_path}")

        # 3. 构造 Pytest 参数
        pytest_args = [
            self.current_script_path,  # 目标脚本
            "-v",  # 详细模式
            f"--html={report_path}",  # 生成 HTML
            "--self-contained-html",  # 单文件 HTML
            "--capture=sys",  # 捕获 stdout (print的内容)
            "-p", "no:cacheprovider",  # 不生成 .pytest_cache 文件夹
            # 新增：加上 -q (quiet) 参数，减少 pytest 内部的处理开销
            "-q"
        ]

        try:
            # ret_code = pytest.main(pytest_args, plugins=[self.uds_test_plugin])

            # self.script_run_state.emit(ret_code.name, self.run_script_index)
            # return ret_code
            # 4. 执行 Pytest
            # ret_code: 0=Pass, 1=Fail, 2=Interrupted, 5=No Tests found
            with open(os.devnull, 'w') as fnull:
                # 将标准输出(stdout)和错误输出(stderr)都重定向到 null
                with redirect_stdout(fnull), redirect_stderr(fnull):
                    ret_code = pytest.main(pytest_args, plugins=[self.uds_test_plugin])

                    self.script_run_state.emit(ret_code.name, self.run_script_index)
                    return ret_code

        except Exception as e:
            logger.exception(f"Pytest 运行异常: {e}")
            self.script_api.write(f"运行异常: {str(e)}")
            return None

    @Slot()
    def stop_external_script(self):
        """
        停止请求。
        注意：Pytest.main 是阻塞的，无法从外部直接强制中断正在运行的测试用例。
        这里的 stop_flag 主要用于阻止下一个脚本的运行。
        """
        self.stop_flag = True
        self.script_api.write("正在尝试停止测试队列...")
        # 如果需要强制中断当前 API 操作，可以在 script_api 中增加 stop 标志检查

    def run_external_scripts(self):
        """
        主循环：遍历列表并执行
        """
        self.stop_flag = False
        self.scripts_run_start.emit()

        # 获取脚本列表
        self.external_scripts = self.db_manager.get_external_script_list_by_config(self.config_name)

        is_all_success = True

        for index, script in enumerate(self.external_scripts):
            # 1. 检查停止标志
            if self.stop_flag:
                self.scripts_run_finish_state.emit(ExternalScriptsRunState.stopped)
                return

            if not script.enable:
                continue

            script_path = script.path
            self.run_script_index = index

            # 2. 准备环境 (设置路径, 检查文件)
            if self._prepare_environment(script_path):

                # 发送状态：正在运行
                self.script_run_state.emit(ExternalScriptRunState.Running, index)

                # 3. 执行 Pytest
                rec_code = self.run_external_script()

                # 4. 发送结果状态
                if rec_code == ExitCode.OK:
                    pass
                else:
                    is_all_success = False

                    # 策略选择：遇到错误是否终止后续脚本？
                    # 如果需要终止，取消下面的注释:
                    # break
            else:
                # 文件加载失败
                self.script_run_state.emit(ExternalScriptRunState.ScriptLoadingFailed, index)
                is_all_success = False

        # 循环结束
        finish_type = ExternalScriptsRunState.passed if is_all_success else ExternalScriptsRunState.failed
        self.scripts_run_finish_state.emit(finish_type)

    def stop_run_external_scripts(self):
        """
        外部调用的停止方法
        """
        self.stop_flag = True
        self.scripts_run_state.emit(ExternalScriptsRunState.stopping)
