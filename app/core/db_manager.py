import logging
import sqlite3
from typing import Optional, List, Union, Any

from app.user_data import DEFAULT_SERVICES, DiagCase, DiagnosisStepData, UdsConfig, CanIgMessages, ExternalScriptConfig, \
    UdsService
from app.windows.FlashConfigPanel import FlashConfig

logger = logging.getLogger('UDSTool.' + __name__)

UDS_CONFIG_TABLE_NAME = "UDS_Config"
CURRENT_CONFIG_TABLE_NAME = 'current_active_config'
SERVICES_TABLE_NAME = 'services_table'
CASE_TABLE_NAME = 'uds_cases'
CASE_STEP_TABLE_NAME = 'uds_case_step'
FLASH_CONFIG_TABLE_NAME = 'flash_config'
CAN_IG_TABLE_NAME = 'can_ig_table'
EXTERNAL_SCRIPT_TABLE_NAME = 'external_script'


class DBBase:
    """数据库操作通用基类：封装通用逻辑，所有表操作子类继承"""
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_conn(self) -> sqlite3.Connection:
        """获取数据库连接：统一配置，便于后续全局修改（如开启连接池）"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")  # 全局开启外键，所有子类继承
        conn.row_factory = sqlite3.Row  # 让查询结果支持「列名取值」，更友好
        return conn

    def _safe_table_name(self, table_name: str) -> str:
        """安全拼接表名：双引号包裹，避免关键字/空格问题（延续之前的规范）"""
        return f'"{table_name}"'

    def execute_ddl(self, sql: str) -> bool:
        """执行DDL语句（建表/删表等），统一异常处理"""
        try:
            with self._get_conn() as conn:
                conn.execute(sql)
            logger.info(f"DDL语句执行成功：{sql[:50]}...")
            return True
        except sqlite3.Error as e:
            logger.exception(f"DDL语句执行失败：{str(e)}")
            return False

    def execute_upsert_auto_increment(self, table_name: str,
                                      auto_increment_col: str,
                                      auto_increment_val: int,
                                      insert_cols: tuple,
                                      insert_datas: tuple) -> Optional[int]:
        """
        通用自增主键增改方
        核心：自增值为0则新增，>0则更新，完全自定义列名和数据
        :param table_name: 操作的数据表名
        :param auto_increment_col: 自增列的列名（如sql_id、id、pk_id）
        :param auto_increment_val: 自增列当前值（0/None=新增，>0=更新，<0抛异常）
        :param insert_cols: 要插入/更新的列名列表（不含自增列，如[config_name, json_data]）
        :param insert_datas: 要插入/更新的一维数据列表（与insert_cols长度严格一致）
        :return: 新增返回自增ID，更新返回原有自增值，失败返回None
        """
        if auto_increment_val == 0:  # 新增
            cols_str = ", ".join(insert_cols)
            placeholders_str = ", ".join(["?"] * len(insert_cols))
            insert_sql = f"""
                                INSERT INTO {table_name} ({cols_str})
                                VALUES ({placeholders_str})
                            """
            results = self.execute_dml(
                sql=insert_sql,
                params=insert_datas,
                is_get_increment_id=True
            )
            if not results:
                logger.error(f"Upsert {table_name}失败：results={results}")
                return None
            rowcount = results[0]
            final_sql_id = results[1]
            if rowcount is None or rowcount != 1:
                logger.error(f"INSERT {table_name}失败：受影响行数={rowcount}")
                return None
        else:  # 更新
            check_sql = f"""
                                SELECT 1 FROM {table_name} WHERE {auto_increment_col} = ?
                            """
            check_result = self.execute_dql(check_sql, (auto_increment_val,))
            # 无记录直接抛异常，贴合业务需求
            if not check_result:
                logger.error(
                    f"{table_name}更新失败：无对应记录，auto_increment_col={auto_increment_val}"
                )
                return None

            # 纯UPDATE：仅更新json_data，保留原有sql_id/主键，无数据变动
            update_set_str = ", ".join([f"{col} = ?" for col in insert_cols])
            update_sql = f"""
                            UPDATE {table_name} SET {update_set_str}
                            WHERE {auto_increment_col} = ?
                        """
            update_params = insert_datas + (auto_increment_val,)
            # 3.3 执行UPDATE
            update_rowcount = self.execute_dml(sql=update_sql, params=update_params)

            if update_rowcount != 1:
                logger.error(
                    f"更新失败：无数据受影响，表{table_name}，自增列{auto_increment_col}={auto_increment_val}"
                )
                return None
            logger.info(
                f"更新成功：表{table_name}，自增列{auto_increment_col}={auto_increment_val}，更新数据={insert_datas}"
            )
            final_sql_id = auto_increment_val
        return final_sql_id


    def execute_dml(self, sql: str, params: tuple = (), is_get_increment_id: bool = False) -> \
            Optional[Union[tuple[int, int], int]]:
        """
        执行DML语句（增/删/改），统一异常处理
        :return: 受影响行数或者tuple[受影响行数, 自增id]，失败返回None
        """
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                if is_get_increment_id:
                    return cursor.rowcount, cursor.lastrowid
                else:
                    return cursor.rowcount
        except sqlite3.Error as e:
            logger.exception(f"DML语句执行失败：sql={sql[:100]}..., params={params}, error={str(e)}")
            return None

    def execute_dql(self, sql: str, params: tuple = ()) -> list[dict]:
        """
        通用DQL执行方法：执行SELECT查询，返回字典列表（列名→值）
        :param sql: SELECT查询语句（带?占位符）
        :param params: 查询参数元组
        :return: 结果字典列表，无数据/异常返回空列表
        """
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                # 将查询结果转换为字典列表（列名作为key，适配所有表）
                columns = [col[0] for col in cursor.description]  # 获取查询列名
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return result
        except sqlite3.Error as e:
            logger.exception(f"DQL查询失败：sql={sql[:100]}..., params={params}, error={str(e)}")
            return []


class CaseStepDB(DBBase):
    """诊断步骤表（case_step）专属操作类：封装该表所有逻辑"""
    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.table_name = CASE_STEP_TABLE_NAME
        self.safe_table = self._safe_table_name(self.table_name)
        self.init_table()

    def init_table(self) -> bool:
        """
        初始化诊断步骤表
        :return: 初始化成功返回True，失败返回False
        """

        create_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.safe_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增主键，步骤唯一标识
                case_id INTEGER NOT NULL DEFAULT 0,     -- 关联案例表id，外键
                step_sequence INTEGER NOT NULL DEFAULT 0, -- 案例内的步骤序号，从0/1开始
                json_data TEXT NOT NULL,                -- 步骤详情JSON数据（如步骤名称、执行结果、耗时等）
                -- 外键约束：关联案例表主键，案例删除时可选择CASCADE（级联删除）/RESTRICT（禁止删除）
                FOREIGN KEY (case_id) REFERENCES {CASE_TABLE_NAME} (id) ON DELETE RESTRICT,
                -- 联合唯一约束：同一个案例的步骤序号不能重复（核心业务约束）
                UNIQUE (case_id, step_sequence)
            )
        """
        return self.execute_ddl(create_sql)

    def delete_steps_by_case_ids(self, cases: list[DiagCase]) -> int:
        """
        批量删除：根据DiagCase列表，删除对应案例的所有诊断步骤
        自动过滤无效案例ID（None/<=0），安全构造IN查询，杜绝SQL注入
        :param cases: DiagCase对象列表（需包含有效id字段）
        :return: 批量操作成功返回删除数量
        """
        # 校验列表有效性
        if not isinstance(cases, list) or len(cases) == 0:
            logger.warning("批量删除步骤失败：传入的cases非有效列表或为空")
            return 0

        # 提取有效案例ID（过滤None/<=0）
        valid_case_ids = [
            case.id for case in cases
            if case.id is not None and case.id > 0
        ]
        if not valid_case_ids:
            logger.warning("批量删除步骤失败：cases列表中无有效案例ID（ID需为正整数）")
            return 0
        # 动态构造IN查询占位符（适配任意长度，防注入）
        placeholders = ", ".join(["?"] * len(valid_case_ids))
        sql = f"DELETE FROM {self.safe_table} WHERE case_id IN ({placeholders})"

        rowcount = self.execute_dml(sql, tuple(valid_case_ids))
        return rowcount

    def delete_case_step(self, step_id: int) -> bool:
        """
        根据步骤ID删除单个诊断步骤
        :param step_id: 步骤自增主键ID（必须为正整数）
        :return: 删除成功返回True，失败/无效参数返回False
        """
        if step_id <= 0:
            logger.warning(f"删除单个步骤失败：无效的step_id={step_id}，必须为正整数")
            return False
        sql = f"DELETE FROM {self.safe_table} WHERE id = ?"
        rowcount = self.execute_dml(sql, (step_id,))
        return rowcount == 1

    def upsert_case_step(self, case_step: DiagnosisStepData) -> Optional[int]:
        """
        步骤增改一体（Upsert）：存在则更新，不存在则新增
        基于case_step表「case_id+step_sequence」联合唯一约束实现原子操作，
        使用模型自带to_json()序列化，保证枚举/bytes等类型正确存储
        :param case_step: DiagnosisStepData模型对象（case_id/step_sequence为核心有效字段）
        :return: 成功返回步骤ID（新增为自增ID，修改为原有ID），失败返回None
        """
        if case_step.case_id < 0:
            logger.warning(f"Upsert步骤失败：无效的case_id={case_step.case_id}，必须为正整数")
            return None
        if case_step.step_sequence < 0:
            logger.warning(f"Upsert步骤失败：无效的step_sequence={case_step.step_sequence}，不能为负数")
            return None

        json_str = case_step.to_json()

        return self.execute_upsert_auto_increment(table_name=self.safe_table,
                                                  auto_increment_col='id',
                                                  auto_increment_val=case_step.id,
                                                  insert_cols=("case_id", "step_sequence", "json_data"),
                                                  insert_datas=(case_step.case_id, case_step.step_sequence, json_str))

    def get_case_steps_by_case_id(self, case_id: int) -> List[DiagnosisStepData]:
        """
        根据案例ID查询其所有诊断步骤，按step_sequence升序排列
        使用模型自带from_json()反序列化，自动还原枚举/bytes等类型为模型对象
        :param case_id: 案例ID（必须为正整数）
        :return: DiagnosisStepData模型列表，无数据/异常均返回空列表
        """
        if case_id <= 0:
            logger.warning(f"查询步骤失败：无效的case_id={case_id}，必须为正整数")
            return []
        sql = f"""
                    SELECT id, json_data
                    FROM {self.safe_table}
                    WHERE case_id = ?
                    ORDER BY step_sequence ASC
                """
        result_dicts = self.execute_dql(sql, (case_id,))
        if not result_dicts:
            logger.info(f"查询步骤完成：case_id={case_id}，无相关步骤记录")
            return []
        step_list = []
        for item in result_dicts:
            step_model = DiagnosisStepData.from_json(item["json_data"])
            step_model.id = item["id"]
            step_list.append(step_model)

        logger.info(f"查询步骤完成：case_id={case_id}，共查询到{len(step_list)}条步骤记录")
        return step_list


class ExternalScriptDB(DBBase):
    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.table_name = EXTERNAL_SCRIPT_TABLE_NAME
        self.safe_table = self._safe_table_name(self.table_name)
        self.init_table()

    def init_table(self) -> bool:
        sql = f"""
                CREATE TABLE IF NOT EXISTS {self.safe_table} (
                    sql_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_name TEXT NOT NULL DEFAULT '',
                    json_data TEXT NOT NULL,
                    FOREIGN KEY (config_name) REFERENCES {UDS_CONFIG_TABLE_NAME} (config_name) ON DELETE RESTRICT
                )
            """
        return self.execute_ddl(sql)

    def save_external_script(self, external_script: ExternalScriptConfig) -> Optional[int]:
        if not external_script.config.strip():
            logger.warning("Upsert外部脚本失败：config字段不能为空")
            return None
        config_val = external_script.config

        json_str = external_script.to_json()

        return self.execute_upsert_auto_increment(table_name=self.safe_table,
                                                  auto_increment_col='sql_id',
                                                  auto_increment_val=external_script.sql_id,
                                                  insert_cols=("config_name", "json_data"),
                                                  insert_datas=(config_val, json_str))

    def get_external_script(self, sql_id: int) -> Optional[ExternalScriptConfig]:
        if sql_id < 0:
            logger.warning(f"查询失败：无效的sql_id={sql_id}，必须为正整数")
            return None
        sql = f"""
                SELECT sql_id, config_name, json_data FROM {self.safe_table} WHERE sql_id = ?
            """
        result_dicts = self.execute_dql(sql, (sql_id,))
        if not result_dicts:
            logger.info(f"查询完成：sql_id={sql_id}，无相关记录")
            return None
        if len(result_dicts) == 1:
            for item in result_dicts:
                external_script = ExternalScriptConfig.from_json(item["json_data"])
                external_script.sql_id = item["sql_id"]
                return external_script
        else:
            logger.error(f"查询完成：sql_id:{sql_id}查询到{len(result_dicts)}个记录")

    def get_external_script_list_by_config(self, config: str) -> List[ExternalScriptConfig]:
        """
        根据config字段查询外部脚本列表
        :param config: 要查询的配置名称
        :return: 匹配的ExternalScriptConfig对象列表，无匹配/异常/入参无效均返回空列表
        """
        if not config.strip():
            logger.warning("查询外部脚本失败：config参数不能为空或仅含空格")
            return []

        # 构造查询SQL：使用安全表名，参数化占位符防注入，保留原有排序
        query_sql = f"""
            SELECT sql_id, config_name, json_data 
            FROM {self.safe_table} 
            WHERE config_name = ?
            ORDER BY sql_id ASC
        """

        # 调用基类execute_dql通用方法：统一处理连接/异常/结果集，返回字典列表
        result_dicts = self.execute_dql(query_sql, (config,))
        external_script_list = []

        for item in result_dicts:
            # 从JSON反序列化基础模型
            external_script = ExternalScriptConfig.from_json(item["json_data"])
            external_script.sql_id = item["sql_id"]
            external_script.config = item["config_name"]
            external_script_list.append(external_script)

        logger.info(f"根据config查询外部脚本完成：config={config}，匹配到{len(external_script_list)}条记录")
        return external_script_list

    def delete_external_script_by_sql_id(self, sql_id: int) -> bool:
        """
        根据sql_id删除单条外部脚本记录
        :param sql_id: 要删除的记录ID
        :return: 删除成功返回True，记录不存在/入参无效/异常返回False
        """
        # 新增入参校验：sql_id必须为正整数
        if sql_id < 0:
            logger.warning(f"删除外部脚本失败：无效的sql_id={sql_id}，必须为正整数")
            return False

        # 构造删除SQL：使用安全表名，参数化占位符
        delete_sql = f"""
            DELETE FROM {self.safe_table} 
            WHERE sql_id = ?
        """

        # 调用基类execute_dml通用方法：统一处理连接/异常，返回受影响行数
        rowcount = self.execute_dml(delete_sql, (sql_id,))

        if rowcount == 1:
            logger.info(f"删除外部脚本成功：sql_id={sql_id}")
            return True
        else:
            logger.warning(f"删除外部脚本失败：sql_id={sql_id}（记录不存在或数据库异常），受影响行数={rowcount}")
            return False

    def delete_external_script_by_config(self, config: str) -> int:
        """
        根据config批量删除外部脚本记录
        :param config: 要删除的配置名称（精确匹配）
        :return: 成功删除的记录数，入参无效/异常返回0
        """
        if not config.strip():
            logger.warning("批量删除外部脚本失败：config参数不能为空或仅含空格")
            return 0

        # 构造批量删除SQL：使用安全表名，参数化占位符
        delete_sql = f"""
            DELETE FROM {self.safe_table} 
            WHERE config_name = ?
        """

        # 调用基类execute_dml通用方法
        rowcount = self.execute_dml(delete_sql, (config,))

        # 处理返回值：execute_dml失败返回None，需转为0；成功返回实际删除行数
        delete_count = rowcount if rowcount is not None else 0
        logger.info(f"根据config批量删除外部脚本完成：config={config}，成功删除{delete_count}条记录")
        return delete_count


class CanIgDB(DBBase):
    """CAN IG表专属操作类：继承DBBase基类，复用通用数据库逻辑"""
    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.table_name = CAN_IG_TABLE_NAME
        self.safe_table = self._safe_table_name(self.table_name)  # 安全表名，规避关键字/空格问题
        self.init_can_ig_table()
    def init_can_ig_table(self):
        """
        初始化CAN IG表
        :return: 初始化成功返回True，失败返回False
        """
        create_sql = f"""
                    CREATE TABLE IF NOT EXISTS {self.safe_table} (
                        sql_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        config_name TEXT NOT NULL DEFAULT '',
                        json_data TEXT NOT NULL,
                        FOREIGN KEY (config_name) REFERENCES {UDS_CONFIG_TABLE_NAME} (config_name) ON DELETE RESTRICT
                    )
                """

        return self.execute_ddl(create_sql)

    def save_can_ig(self, can_ig: CanIgMessages) -> Optional[int]:
        """
        保存/更新CAN IG配置（保留原有核心逻辑：新增回填ID同步JSON，更新直接同步）
        - 新增：先插临时数据→获取自增ID→回填对象→重新序列化→更新JSON（保证db主键与json内sql_id一致）
        - 更新：直接序列化（已有ID）→执行更新，无记录则抛ValueError
        :param can_ig: CAN IG模型对象
        :return: 最终的sql_id（新增=自增ID，更新=原有ID）
        """
        # 入参校验：sql_id不能为负数
        if can_ig.sql_id < 0:
            raise ValueError(f"保存失败：无效的sql_id={can_ig.sql_id}，不能为负数")
        if not can_ig.config.strip():
            logger.warning("Upsert外部脚本失败：config字段不能为空")
            return None
        config_val = can_ig.config

        json_str = can_ig.to_json()

        return self.execute_upsert_auto_increment(table_name=self.safe_table,
                                                  auto_increment_col='sql_id',
                                                  auto_increment_val=can_ig.sql_id,
                                                  insert_cols=("config_name", "json_data"),
                                                  insert_datas=(config_val, json_str))

    def get_can_ig(self, sql_id: int) -> Optional[CanIgMessages]:
        if sql_id < 0:
            logger.warning(f"查询失败：无效的sql_id={sql_id}，必须为正整数")
            return None
        sql = f"""
                SELECT sql_id, config_name, json_data FROM {self.safe_table} WHERE sql_id = ?
            """
        result_dicts = self.execute_dql(sql, (sql_id,))
        if not result_dicts:
            logger.info(f"查询完成：sql_id={sql_id}，无相关记录")
            return None
        if len(result_dicts) == 1:
            for item in result_dicts:
                can_ig = CanIgMessages.from_json(item["json_data"])
                can_ig.sql_id = item["sql_id"]
                return can_ig
        else:
            logger.error(f"查询完成：sql_id:{sql_id}查询到{len(result_dicts)}个记录")

    def get_can_ig_list_by_config(self, config: str) -> List[CanIgMessages]:
        """
        根据config字段查询外部脚本列表
        :param config: 要查询的配置名称
        :return: 匹配的CanIgMessages对象列表，无匹配/异常/入参无效均返回空列表
        """
        if not config.strip():
            logger.warning("查询外部脚本失败：config参数不能为空或仅含空格")
            return []

        # 构造查询SQL：使用安全表名，参数化占位符防注入，保留原有排序
        query_sql = f"""
               SELECT sql_id, config_name, json_data 
               FROM {self.safe_table} 
               WHERE config_name = ?
               ORDER BY sql_id ASC
           """

        # 调用基类execute_dql通用方法：统一处理连接/异常/结果集，返回字典列表
        result_dicts = self.execute_dql(query_sql, (config,))
        external_script_list = []

        for item in result_dicts:
            # 从JSON反序列化基础模型
            external_script = CanIgMessages.from_json(item["json_data"])
            external_script.sql_id = item["sql_id"]
            external_script.config = item["config_name"]
            external_script_list.append(external_script)

        logger.info(f"根据config查询can ig完成：config={config}，匹配到{len(external_script_list)}条记录")
        return external_script_list

    def delete_can_ig_by_sql_id(self, sql_id: int) -> bool:
        """
        根据sql_id删除单条外部脚本记录
        :param sql_id: 要删除的记录ID
        :return: 删除成功返回True，记录不存在/入参无效/异常返回False
        """
        # 新增入参校验：sql_id必须为正整数
        if sql_id < 0:
            logger.warning(f"删除外部脚本失败：无效的sql_id={sql_id}，必须为正整数")
            return False

        # 构造删除SQL：使用安全表名，参数化占位符
        delete_sql = f"""
               DELETE FROM {self.safe_table} 
               WHERE sql_id = ?
           """

        # 调用基类execute_dml通用方法：统一处理连接/异常，返回受影响行数
        rowcount = self.execute_dml(delete_sql, (sql_id,))

        if rowcount == 1:
            logger.info(f"删除can ig成功：sql_id={sql_id}")
            return True
        else:
            logger.warning(f"删除can ig失败：sql_id={sql_id}（记录不存在或数据库异常），受影响行数={rowcount}")
            return False

    def delete_external_script_by_config(self, config: str) -> int:
        """
        根据config批量删除外部脚本记录
        :param config: 要删除的配置名称（精确匹配）
        :return: 成功删除的记录数，入参无效/异常返回0
        """
        if not config.strip():
            logger.warning("批量删除外部脚本失败：config参数不能为空或仅含空格")
            return 0

        # 构造批量删除SQL：使用安全表名，参数化占位符
        delete_sql = f"""
               DELETE FROM {self.safe_table} 
               WHERE config_name = ?
           """

        # 调用基类execute_dml通用方法
        rowcount = self.execute_dml(delete_sql, (config,))

        # 处理返回值：execute_dml失败返回None，需转为0；成功返回实际删除行数
        delete_count = rowcount if rowcount is not None else 0
        logger.info(f"根据config批量删除can ig完成：config={config}，成功删除{delete_count}条记录")
        return delete_count




class UdsCaseDB(DBBase):
    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.table_name = CASE_TABLE_NAME
        self.safe_table = self._safe_table_name(self.table_name)  # 安全表名，规避关键字/空格问题
        self.init_case_database()
    def init_case_database(self):
        """
        初始化CAN IG表
        :return: 初始化成功返回True，失败返回False
        """
        create_sql = f"""
                    CREATE TABLE IF NOT EXISTS {self.safe_table} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        config_name TEXT NOT NULL DEFAULT '',
                        json_data TEXT NOT NULL,
                        FOREIGN KEY (config_name) REFERENCES {UDS_CONFIG_TABLE_NAME} (config_name) ON DELETE RESTRICT
                    )
                """

        return self.execute_ddl(create_sql)

    def delete_case_by_id(self, case_id: int) -> bool:
        """
        根据case_id删除单条外部脚本记录
        :param case_id: 要删除的记录ID
        :return: 删除成功返回True，记录不存在/入参无效/异常返回False
        """
        # 新增入参校验：sql_id必须为正整数
        if case_id <= 0:
            logger.warning(f"删除case失败：无效的sql_id={case_id}，必须为正整数")
            return False

        # 构造删除SQL：使用安全表名，参数化占位符
        delete_sql = f"""
               DELETE FROM {self.safe_table} 
               WHERE id = ?
           """

        # 调用基类execute_dml通用方法：统一处理连接/异常，返回受影响行数
        rowcount = self.execute_dml(delete_sql, (case_id,))

        if rowcount == 1:
            logger.info(f"删除case成功：sql_id={case_id}")
            return True
        else:
            logger.warning(f"删除case失败：sql_id={case_id}（记录不存在或数据库异常），受影响行数={rowcount}")
            return False

    def upsert_case(self, case: DiagCase) -> Optional[int]:
        """
        保存/更新CASE配置
        :param case: case模型对象
        :return: 最终的id（新增=自增ID，更新=原有ID）
        """
        # 1. 入参校验：sql_id不能为负数
        if case.id < 0:
            raise ValueError(f"保存失败：无效的sql_id={case.id}，不能为负数")
        if not case.config_name.strip():
            logger.warning("Upsert外部脚本失败：config字段不能为空")
            return None
        config_val = case.config_name

        json_str = case.to_json()

        return self.execute_upsert_auto_increment(table_name=self.safe_table,
                                                  auto_increment_col='id',
                                                  auto_increment_val=case.id,
                                                  insert_cols=("config_name", "json_data"),
                                                  insert_datas=(config_val, json_str))

    def batch_upsert_cases(self, cases: list[DiagCase]) -> tuple[int, list[int]]:
        """
        批量插入/更新诊断案例
        :param cases: DiagCase 对象列表
        :return: (成功数量, 成功ID列表)
        """
        pass

    def get_case(self, case_id: int) -> Optional[DiagCase]:
        if case_id < 0:
            logger.warning(f"查询失败：无效的case_id={case_id}，必须为正整数")
            return None
        sql = f"""
                SELECT id, config_name, json_data FROM {self.safe_table} WHERE id = ?
            """
        result_dicts = self.execute_dql(sql, (case_id,))
        if not result_dicts:
            logger.info(f"查询完成：case_id={case_id}，无相关记录")
            return None
        if len(result_dicts) == 1:
            for item in result_dicts:
                case = DiagCase.from_json(item["json_data"])
                case.id = item["id"]
                case.case_name = item["config_name"]
                return case
        else:
            logger.error(f"查询完成：case_id:{case_id}查询到{len(result_dicts)}个记录")

    def get_case_list_by_config(self, config_name: str) -> List[DiagCase]:
        """
        根据config_name字段查询外部脚本列表
        :param config_name: 要查询的配置名称
        :return: 匹配的DiagCase对象列表，无匹配/异常/入参无效均返回空列表
        """
        if not config_name.strip():
            logger.warning("查询case失败：config_name参数不能为空或仅含空格")
            return []

        # 构造查询SQL：使用安全表名，参数化占位符防注入，保留原有排序
        query_sql = f"""
               SELECT id, config_name, json_data 
               FROM {self.safe_table} 
               WHERE config_name = ?
               ORDER BY id ASC
           """

        # 调用基类execute_dql通用方法：统一处理连接/异常/结果集，返回字典列表
        result_dicts = self.execute_dql(query_sql, (config_name,))
        case_list = []

        for item in result_dicts:
            # 从JSON反序列化基础模型
            case = DiagCase.from_json(item["json_data"])
            case.id = item["id"]
            # case.config_name = item["config_name"]
            case_list.append(case)

        logger.info(f"根据config查询case完成：config={config_name}，匹配到{len(case_list)}条记录")
        return case_list

    def delete_cases_by_config(self, config_name: str) -> int:
        """
        根据config_name批量删除外部脚本记录
        :param config_name: 要删除的配置名称（精确匹配）
        :return: 成功删除的记录数，入参无效/异常返回0
        """
        if not config_name.strip():
            logger.warning("批量删除case失败：config_name参数不能为空或仅含空格")
            return 0

        # 构造批量删除SQL：使用安全表名，参数化占位符
        delete_sql = f"""
               DELETE FROM {self.safe_table} 
               WHERE config_name = ?
           """

        # 调用基类execute_dml通用方法
        rowcount = self.execute_dml(delete_sql, (config_name,))

        # 处理返回值：execute_dml失败返回None，需转为0；成功返回实际删除行数
        delete_count = rowcount if rowcount is not None else 0
        logger.info(f"根据config批量删除can ig完成：config={config_name}，成功删除{delete_count}条记录")
        return delete_count


class UdsConfigDB(DBBase):
    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.table_name = UDS_CONFIG_TABLE_NAME
        self.safe_table = self._safe_table_name(self.table_name)  # 安全表名，规避关键字/空格问题
        self.init_config_database()
        self.insert_default_uds_config()

    def insert_default_uds_config(self):
        config_name_list = self.get_all_config_names()

        if config_name_list:
            pass
        else:
            self.upsert_uds_config(UdsConfig())

    def init_config_database(self):
        """
        初始化uds config表
        :return: 初始化成功返回True，失败返回False
        """
        create_sql = f"""
                            CREATE TABLE IF NOT EXISTS {self.safe_table} (
                                config_name TEXT TEXT PRIMARY KEY,
                                json_data TEXT NOT NULL,
                                UNIQUE (config_name)
                            )
                        """

        return self.execute_ddl(create_sql)

    def upsert_uds_config(self, uds_config: UdsConfig) -> Optional[int]:
        """
        保存/更新Uds Config配置
        :param uds_config: uds_config模型对象
        :return: 影响的行数
        """
        if not uds_config.config_name.strip():
            logger.warning("Upsert uds config失败：config_name字段不能为空")
            return None
        config_val = uds_config.config_name

        json_str = uds_config.to_json()

        sql = f"""
                INSERT OR REPLACE INTO {self.safe_table} (
                    config_name, json_data
                ) VALUES (?, ?)
            """
        rowcount = self.execute_dml(
            sql=sql,
            params=(
                config_val,
                json_str
            ),
        )
        if rowcount is None or rowcount <= 0:
            logger.error(f"Upsert uds config失败：config_name={uds_config.config_name}，受影响行数={rowcount}")
            return None
        return rowcount

    def get_all_config_names(self) -> List[str]:
        query_sql = f"SELECT config_name FROM {self.safe_table} ORDER BY config_name ASC;"
        result_dicts = self.execute_dql(query_sql)
        config_names_list = []

        for item in result_dicts:
            config_name = item["config_name"]
            config_names_list.append(config_name)

        logger.info(f"查询config_name完成：匹配到{len(config_names_list)}条记录")
        return config_names_list

    def delete_uds_config(self, config_name: str) -> bool:
        """
        根据config_name删除记录
        :param config_name: 要删除的config_name
        :return: 删除成功返回True，记录不存在/入参无效/异常返回False
        """
        # 构造删除SQL：使用安全表名，参数化占位符
        delete_sql = f"""
               DELETE FROM {self.safe_table} 
               WHERE config_name = ?
           """

        # 调用基类execute_dml通用方法：统一处理连接/异常，返回受影响行数
        rowcount = self.execute_dml(delete_sql, (config_name,))

        if rowcount == 1:
            logger.info(f"删除config成功：config_name={config_name}")
            return True
        else:
            logger.warning(f"删除config失败：config_name={config_name}（记录不存在或数据库异常），受影响行数={rowcount}")
            return False

    def get_uds_config(self, config_name: str) -> Optional[UdsConfig]:
        sql = f"""
                SELECT config_name, json_data FROM {self.safe_table} WHERE config_name = ?
            """
        result_dicts = self.execute_dql(sql, (config_name,))
        if not result_dicts:
            logger.info(f"查询完成：config_name={config_name}，无相关记录")
            return None
        if len(result_dicts) == 1:
            for item in result_dicts:
                uds_config = UdsConfig.from_json(item["json_data"])
                uds_config.config_name = item["config_name"]
                return uds_config
        else:
            logger.error(f"查询完成：config_name:{config_name}查询到{len(result_dicts)}个记录")


class CurrentUdsConfigDB(DBBase):
    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.table_name = CURRENT_CONFIG_TABLE_NAME
        self.safe_table = self._safe_table_name(self.table_name)  # 安全表名，规避关键字/空格问题
        self.init_current_config_database()
        self.global_active_config = 'global_active_config'

    def init_current_config_database(self) -> bool:
        """初始化current_config表：主键key，外键关联UDS配置主表，初始化成功返回True，失败返回False"""
        # 修正：删除FOREIGN KEY行末尾多余逗号 + 外键用安全表名
        create_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.safe_table} (
                key TEXT PRIMARY KEY,
                active_config_name TEXT NOT NULL,
                -- 外键约束：关联UDS主表config_name，禁止主表配置删除（ON DELETE RESTRICT）
                FOREIGN KEY (active_config_name) REFERENCES {UDS_CONFIG_TABLE_NAME} (config_name) ON DELETE RESTRICT
            )
        """
        return self.execute_ddl(create_sql)

    def set_active_config(self, new_config_name: str) -> bool:
        sql = f"""
                INSERT OR REPLACE INTO {self.safe_table} (key, active_config_name)
                VALUES ('{self.global_active_config}', ?);
                """
        rowcount = self.execute_dml(
            sql=sql,
            params=(new_config_name,),
        )
        if rowcount is None or rowcount <= 0:
            logger.error(f"set_active_config失败：new_config_name={new_config_name}，受影响行数={rowcount}")
            return False
        return True

    def get_active_config_name(self) -> Optional[str]:
        query_sql = f"""
                SELECT active_config_name FROM {self.safe_table} WHERE key = ?
            """
        result_dicts = self.execute_dql(query_sql, (self.global_active_config,))
        if not result_dicts:
            logger.info(f"查询活失败")
            return None

        active_name = result_dicts[0]["active_config_name"]
        return active_name


class FlashConfigDB(DBBase):
    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.table_name = FLASH_CONFIG_TABLE_NAME
        self.safe_table = self._safe_table_name(self.table_name)  # 安全表名，规避关键字/空格问题
        self.init_flash_config_database()

    def init_flash_config_database(self) -> bool:
        """
        初始化flash_config表
        :return: 初始化成功返回True，失败返回False
        """
        create_sql = f"""
                            CREATE TABLE IF NOT EXISTS {self.safe_table} (
                                config_name TEXT PRIMARY KEY,
                                json_data TEXT NOT NULL,
                                FOREIGN KEY (config_name) REFERENCES {UDS_CONFIG_TABLE_NAME} (config_name) ON DELETE RESTRICT,
                                UNIQUE (config_name)
                            )
                        """

        return self.execute_ddl(create_sql)

    def save_flash_config(self, config_name: str, flash_config: FlashConfig) -> bool:
        """
        保存/更新flash_config配置
        :param config_name: config_name
        :param flash_config: flash_config模型对象
        :return: 影响的行数
        """
        if not config_name.strip():
            logger.warning("Upsert uds config失败：config_name字段不能为空")
            return False

        json_str = flash_config.to_json()

        sql = f"""
                INSERT OR REPLACE INTO {self.safe_table} (
                    config_name, json_data
                ) VALUES (?, ?)
            """
        rowcount = self.execute_dml(
            sql=sql,
            params=(
                config_name,
                json_str
            ),
        )
        if rowcount is None or rowcount != 1:
            logger.error(f"Upsert uds config失败：config_name={config_name}，受影响行数={rowcount}")
            return False
        elif rowcount == 1:
            return True
        else:
            logger.error(f"Upsert uds config失败：config_name={config_name}，受影响行数={rowcount}")
            return False

    def get_flash_config(self, config_name: str) -> Optional[FlashConfig]:
        sql = f"""
                SELECT config_name, json_data FROM {self.safe_table} WHERE config_name = ?
            """
        result_dicts = self.execute_dql(sql, (config_name,))
        if not result_dicts:
            logger.info(f"查询完成：config_name={config_name}，无相关记录")
            return None
        if len(result_dicts) == 1:
            for item in result_dicts:
                external_script = FlashConfig.from_json(item["json_data"])
                return external_script
        else:
            logger.error(f"查询完成：config_name:{config_name}查询到{len(result_dicts)}个记录")

    def delete_flash_config(self, config_name: str) -> bool:
        """
        根据config_name删除记录
        :param config_name: 要删除的config_name
        :return: 删除成功返回True，记录不存在/入参无效/异常返回False
        """
        # 构造删除SQL：使用安全表名，参数化占位符
        delete_sql = f"""
               DELETE FROM {self.safe_table} 
               WHERE config_name = ?
           """

        # 调用基类execute_dml通用方法：统一处理连接/异常，返回受影响行数
        rowcount = self.execute_dml(delete_sql, (config_name,))

        if rowcount == 1:
            logger.info(f"删除config成功：config_name={config_name}")
            return True
        else:
            logger.warning(f"删除config失败：config_name={config_name}（记录不存在或数据库异常），受影响行数={rowcount}")
            return False


class ServicesConfigDB(DBBase):
    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.table_name = SERVICES_TABLE_NAME
        self.safe_table = self._safe_table_name(self.table_name)  # 安全表名，规避关键字/空格问题
        self.init_services_config_database()

    def init_services_config_database(self):
        """
        初始化flash_config表
        :return: 初始化成功返回True，失败返回False
        """
        create_sql = f"""
                        CREATE TABLE IF NOT EXISTS {self.safe_table} (
                            config_name TEXT PRIMARY KEY,
                            json_data TEXT NOT NULL,
                            FOREIGN KEY (config_name) REFERENCES {UDS_CONFIG_TABLE_NAME} (config_name) ON DELETE RESTRICT,
                            UNIQUE (config_name)
                        )
                    """

        return self.execute_ddl(create_sql)

    def get_service_config(self, config_name: str) -> Optional[UdsService]:
        sql = f"""
                SELECT config_name, json_data FROM {self.safe_table} WHERE config_name = ?
            """
        result_dicts = self.execute_dql(sql, (config_name,))
        if not result_dicts:
            logger.info(f"查询完成：config_name={config_name}，无相关记录")
            return None
        if len(result_dicts) == 1:
            for item in result_dicts:
                external_script = UdsService.from_json(item["json_data"])
                return external_script
        else:
            logger.error(f"查询完成：config_name:{config_name}查询到{len(result_dicts)}个记录")

    def save_service_config(self, config_name: str, service_config: UdsService) -> bool:
        """
        保存/更新flash_config配置
        :param config_name: config_name
        :param service_config: flash_config模型对象
        :return: 影响的行数
        """
        if not config_name.strip():
            logger.warning("Upsert uds config失败：config_name字段不能为空")
            return False

        json_str = service_config.to_json()

        sql = f"""
                INSERT OR REPLACE INTO {self.safe_table} (
                    config_name, json_data
                ) VALUES (?, ?)
            """
        rowcount = self.execute_dml(
            sql=sql,
            params=(
                config_name,
                json_str
            ),
        )
        if rowcount is None or rowcount != 1:
            logger.error(f"Upsert service_config失败：config_name={config_name}，受影响行数={rowcount}")
            return False
        elif rowcount == 1:
            return True
        else:
            logger.error(f"Upsert service_config失败：config_name={config_name}，受影响行数={rowcount}")
            return False

    def delete_service_config(self, config_name: str) -> bool:
        """
        根据config_name删除记录
        :param config_name: 要删除的config_name
        :return: 删除成功返回True，记录不存在/入参无效/异常返回False
        """
        # 构造删除SQL：使用安全表名，参数化占位符
        delete_sql = f"""
               DELETE FROM {self.safe_table} 
               WHERE config_name = ?
           """

        # 调用基类execute_dml通用方法：统一处理连接/异常，返回受影响行数
        rowcount = self.execute_dml(delete_sql, (config_name,))

        if rowcount == 1:
            logger.info(f"删除config成功：config_name={config_name}")
            return True
        else:
            logger.warning(f"删除config失败：config_name={config_name}（记录不存在或数据库异常），受影响行数={rowcount}")
            return False


class DBManager:
    def __init__(self, db_path: str):
        self.db_path = db_path

        self.uds_config_db: UdsConfigDB = UdsConfigDB(self.db_path)
        self.current_uds_config_db: CurrentUdsConfigDB = CurrentUdsConfigDB(self.db_path)

        self.case_step_db: CaseStepDB = CaseStepDB(self.db_path)
        self.external_script_db: ExternalScriptDB = ExternalScriptDB(self.db_path)
        self.can_ig_db: CanIgDB = CanIgDB(self.db_path)
        self.uds_case_db: UdsCaseDB = UdsCaseDB(self.db_path)
        self.flash_config_db: FlashConfigDB = FlashConfigDB(self.db_path)
        self.service_config_db: ServicesConfigDB = ServicesConfigDB(self.db_path)

        config_list = self.uds_config_db.get_all_config_names()
        active_config = self.current_uds_config_db.get_active_config_name()
        if not active_config and config_list:
            self.current_uds_config_db.set_active_config(config_list[0])
            active_config = config_list[0]
        elif active_config not in config_list and config_list:
            self.current_uds_config_db.set_active_config(config_list[0])
            active_config = config_list[0]

        if not self.service_config_db.get_service_config(active_config):
            self.service_config_db.save_service_config(active_config, DEFAULT_SERVICES)

    def delete_config(self, config_came: str):

        self.service_config_db.delete_service_config(config_came)
        self.external_script_db.delete_external_script_by_config(config_came)
        self.can_ig_db.delete_external_script_by_config(config_came)
        self.flash_config_db.delete_flash_config(config_came)

        case_list = self.uds_case_db.get_case_list_by_config(config_came)
        self.case_step_db.delete_steps_by_case_ids(case_list)
        self.uds_case_db.delete_cases_by_config(config_came)

        self.uds_config_db.delete_uds_config(config_came)






