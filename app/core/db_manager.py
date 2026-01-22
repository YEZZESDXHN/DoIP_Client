import logging
import sqlite3
from typing import Optional, List

from app.user_data import DEFAULT_SERVICES, DiagCase, DiagnosisStepData, UdsConfig, CanIgMessages
from app.windows.FlashConfigPanel import FlashConfig

logger = logging.getLogger('UDSTool.' + __name__)

UDS_CONFIG_TABLE_NAME = "UDS_Config"
CURRENT_CONFIG_TABLE_NAME = 'current_active_config'
SERVICES_TABLE_NAME = 'services_table'
CASE_TABLE_NAME = 'uds_cases'
CASE_STEP_TABLE_NAME = 'uds_case_step'
FLASH_CONFIG_TABLE_NAME = 'flash_config'
CAN_IG_TABLE_NAME = 'can_ig_table'


class DBManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.default_config = UdsConfig()
        self.init_config_database()
        self.init_services_database()
        self.init_case_database()
        self.init_case_step_database()
        self.init_flash_config_table()
        self.init_can_ig_table()

    def init_can_ig_table(self):
        with sqlite3.connect(self.db_path) as conn:
            # 只有两列：sql_id (主键), json_data
            conn.execute(f"""
                            CREATE TABLE IF NOT EXISTS {CAN_IG_TABLE_NAME} (
                                sql_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                config TEXT NOT NULL DEFAULT '',  -- 新增config字段，默认空字符串
                                json_data TEXT NOT NULL
                            )
                        """)
            conn.commit()

    def save_can_ig(self, can_ig: CanIgMessages) -> int:
        """
        保存/更新配置：
        - 新增：先插数据生成自增ID → 回填ID → 重新序列化 → 更新JSON（确保sql_id同步）
        - 更新：直接序列化（已有ID）→ 同步更新
        最终数据库主键 + json_data里的sql_id 完全一致
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            config_val = can_ig.config

            if can_ig.sql_id > 0:
                # 场景1：更新 → sql_id已存在，直接序列化（JSON里有正确ID）
                json_str = can_ig.to_json()
                cursor.execute(f"""
                    UPDATE {CAN_IG_TABLE_NAME} 
                    SET config = ?, json_data = ? 
                    WHERE sql_id = ?
                """, (config_val, json_str, can_ig.sql_id))

                if cursor.rowcount == 0:
                    raise ValueError(f"更新失败：无sql_id={can_ig.sql_id}的记录")
                final_sql_id = can_ig.sql_id

            else:
                # 场景2：新增 → 核心修复：先插空数据，再回填ID更新JSON
                # 步骤1：插入临时数据（config + 初始JSON，此时sql_id=0）
                temp_json = can_ig.to_json()
                cursor.execute(f"""
                    INSERT INTO {CAN_IG_TABLE_NAME} (config, json_data) 
                    VALUES (?, ?)
                """, (config_val, temp_json))

                # 步骤2：获取数据库自增的sql_id，回填到对象
                final_sql_id = cursor.lastrowid
                can_ig.sql_id = final_sql_id  # 此时对象的sql_id变为自增ID

                # 步骤3：重新序列化（此时JSON里的sql_id是自增ID）
                final_json = can_ig.to_json()

                # 步骤4：更新数据库的json_data，确保JSON里的sql_id同步
                cursor.execute(f"""
                    UPDATE {CAN_IG_TABLE_NAME} 
                    SET json_data = ? 
                    WHERE sql_id = ?
                """, (final_json, final_sql_id))

        return final_sql_id

    def get_can_ig(self, sql_id: int) -> CanIgMessages:
        """根据sql_id读取单条记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT config, json_data FROM {CAN_IG_TABLE_NAME} WHERE sql_id = ?
            """, (sql_id,))
            result = cursor.fetchone()

            if not result:
                raise ValueError(f"无sql_id={sql_id}的记录")

            config_val, json_str = result
            can_ig = CanIgMessages.from_json(json_str)
            return can_ig

    def get_can_ig_list_by_config(self, config: str) -> List[CanIgMessages]:
        """
        根据config字段查询CanIgMessages列表
        :param config: 要查询的配置名称（精确匹配）
        :return: 匹配的CanIgMessages对象列表，无匹配则返回空列表
        """
        can_ig_list = []

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # 精确匹配config字段
            cursor.execute(f"""
                SELECT sql_id, config, json_data FROM {CAN_IG_TABLE_NAME} 
                WHERE config = ?
                ORDER BY sql_id ASC
            """, (config,))

            # 遍历所有查询结果
            results = cursor.fetchall()
            for row in results:
                sql_id, config_val, json_str = row
                # 还原对象并补全sql_id和config属性
                can_ig = CanIgMessages.from_json(json_str)
                can_ig_list.append(can_ig)

        return can_ig_list

    def delete_can_ig_by_sql_id(self, sql_id: int) -> bool:
        """
        根据sql_id删除单条记录
        :param sql_id: 要删除的记录ID
        :return: 删除成功返回True，记录不存在返回False
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                DELETE FROM {CAN_IG_TABLE_NAME} 
                WHERE sql_id = ?
            """, (sql_id,))

            # rowcount：受影响的行数，0表示无记录，1表示删除成功
            return cursor.rowcount > 0

    def delete_can_ig_by_config(self, config: str) -> int:
        """
        根据config批量删除记录
        :param config: 要删除的配置名称（精确匹配）
        :return: 成功删除的记录数
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                DELETE FROM {CAN_IG_TABLE_NAME} 
                WHERE config = ?
            """, (config,))

            # 返回删除的行数
            return cursor.rowcount


    def init_flash_config_table(self):
        with sqlite3.connect(self.db_path) as conn:
            # 只有两列：name (主键), json_data
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {FLASH_CONFIG_TABLE_NAME} (
                    name TEXT PRIMARY KEY,
                    json_data TEXT NOT NULL
                )
            """)
            conn.commit()

    def save_flash_config(self, config_name: str, config_obj: FlashConfig):
        """保存配置 (如果存在则覆盖)"""
        json_str = config_obj.to_json()
        with sqlite3.connect(self.db_path) as conn:
            # 使用 REPLACE 语法实现 Upsert (Update or Insert)
            conn.execute(
                f"INSERT OR REPLACE INTO {FLASH_CONFIG_TABLE_NAME} (name, json_data) VALUES (?, ?)",
                (config_name, json_str)
            )
            conn.commit()
            logger.info(f"Saved: {config_name}")

    def load_flash_config(self, config_name: str) -> Optional[FlashConfig]:
        """读取配置，返回 FlashConfig 对象"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(f"SELECT json_data FROM {FLASH_CONFIG_TABLE_NAME} WHERE name = ?", (config_name,))
            row = cursor.fetchone()
            if row:
                try:
                    return FlashConfig.from_json(row[0])
                except Exception as e:
                    logger.exception(f'读取flash配置错误：{e}')
                    return None
            return None

    def init_config_database(self):
        # ---生成当前配置的CREATE TABLE SQL---
        create_current_config_sql = f"""
                        CREATE TABLE IF NOT EXISTS {CURRENT_CONFIG_TABLE_NAME} (
                            key TEXT PRIMARY KEY,
                            active_config_name TEXT NOT NULL
                        );
                        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                                CREATE TABLE IF NOT EXISTS {UDS_CONFIG_TABLE_NAME} (
                                    config_name TEXT PRIMARY KEY,
                                    json_data TEXT NOT NULL
                                )
                            """)
                cursor.execute(create_current_config_sql)
                conn.commit()
                logger.info(f"数据库初始化完成！{UDS_CONFIG_TABLE_NAME} ，{CURRENT_CONFIG_TABLE_NAME}表创建/验证成功")

                # 检查表中是否有数据
                cursor.execute(f"SELECT COUNT(*) FROM {UDS_CONFIG_TABLE_NAME}")
                count = cursor.fetchone()[0]

                if count == 0:
                    # 如果没有数据，插入默认配置
                    default_config = UdsConfig()
                    config_name = getattr(default_config, 'config_name', 'default')
                    json_data = default_config.to_json()
                    sql = f"""
                                    INSERT OR REPLACE INTO {UDS_CONFIG_TABLE_NAME} 
                                    (config_name, json_data) VALUES (?, ?)
                                """
                    conn.execute(sql, (config_name, json_data))
                    conn.commit()
                else:
                    logger.info(f"表 {UDS_CONFIG_TABLE_NAME} 中已存在 {count} 条配置，跳过写入默认配置。")

                # 检查并设置当前激活的配置名称到激活配置表
                cursor.execute(f"SELECT COUNT(*) FROM {CURRENT_CONFIG_TABLE_NAME}")
                meta_count = cursor.fetchone()[0]

                if meta_count == 0:
                    # 如果激活配置表是空的，将默认配置设为激活
                    self._insert_default_doip_config_name(conn)
                else:
                    logger.info(f"表 {CURRENT_CONFIG_TABLE_NAME} 中已存在激活配置记录，跳过设置。")

        except sqlite3.Error as e:
            logger.exception(f"初始化数据库失败：{str(e)}")

    def init_services_database(self):
        create_services_table_sql = f"""
                                CREATE TABLE IF NOT EXISTS {SERVICES_TABLE_NAME} (
                                    config_name TEXT PRIMARY KEY,
                                    services_json TEXT NOT NULL
                                )
                            """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(create_services_table_sql)
                conn.commit()
                active_config_name = self.get_active_config_name()
                if self._check_services_is_exists(conn, active_config_name):
                    pass
                else:
                    self.add_services_config(active_config_name, DEFAULT_SERVICES.to_json())
                    logger.debug(f'{SERVICES_TABLE_NAME}表创建成功')
                logger.info(f"services数据库初始化完成！{SERVICES_TABLE_NAME}表创建/验证成功")
        except sqlite3.Error as e:
            logger.exception(f"services初始化数据库失败：{str(e)}")

    def init_case_database(self):
        primary_key = DiagCase().get_attr_names()[0]
        field_definitions = []
        for field, value in DiagCase().to_dict().items():
            # 确定 SQL 类型和约束
            sql_type = 'TEXT' if isinstance(value, str) else 'INTEGER'
            constraints = 'PRIMARY KEY AUTOINCREMENT' if field == primary_key else 'NOT NULL'

            # 添加 DEFAULT 子句（如果不是主键）
            if field != primary_key:
                constraints += f" DEFAULT {repr(value)}"

            field_definitions.append(f"{field} {sql_type} {constraints}")

        fields_sql = ',\n'.join(field_definitions)
        create_case_table_sql = f"""
                        CREATE TABLE IF NOT EXISTS {CASE_TABLE_NAME} (
                            {fields_sql}
                        );
                        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(create_case_table_sql)
                conn.commit()

                logger.info(f"case数据库初始化完成！{CASE_TABLE_NAME}表创建/验证成功")
        except sqlite3.Error as e:
            logger.exception(f"case初始化数据库失败：{str(e)}")

    def init_case_step_database(self):
        """初始化诊断步骤表"""
        # 实例化数据类获取字段信息
        step_data = DiagnosisStepData()
        # 获取主键（取第一个字段作为主键，可根据实际需求调整）
        primary_key = step_data.get_attr_names()[0]
        field_definitions = []

        for field, value in step_data.to_dict().items():
            # 确定 SQL 类型和约束
            sql_type = 'TEXT' if isinstance(value, str) else 'INTEGER'
            constraints = 'PRIMARY KEY AUTOINCREMENT' if field == primary_key else 'NOT NULL'

            # 添加 DEFAULT 子句（如果不是主键）
            if field != primary_key:
                constraints += f" DEFAULT {repr(value)}"

            field_definitions.append(f"{field} {sql_type} {constraints}")

        fields_sql = ',\n'.join(field_definitions)
        # 构建创建表SQL
        create_step_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {CASE_STEP_TABLE_NAME} (
                {fields_sql}
            );
        """

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(create_step_table_sql)
                conn.commit()
                logger.info(f"诊断步骤数据库初始化完成！{CASE_STEP_TABLE_NAME}表创建/验证成功")
        except sqlite3.Error as e:
            logger.exception(f"诊断步骤初始化数据库失败：{str(e)}")

    def delete_steps_by_case_ids(self, cases: list[DiagCase]) -> bool:
        """
        根据 case 列表批量删除对应的步骤 (DiagnosisStep)
        :param cases: 要删除步骤的 case 列表
        :return: 是否执行成功
        """
        case_ids = []
        for case in cases:
            case_ids.append(case.id)
        if not case_ids:
            logger.warning("传入的 case_id 列表为空，未执行删除步骤操作")
            return False

        success = False
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 1. 动态构建占位符字符串，例如: "?, ?, ?"
                # 这样可以处理列表长度不固定的情况
                placeholders = ', '.join(['?'] * len(case_ids))

                # 2. 构建批量删除 SQL
                # 注意：CASE_STEP_TABLE_NAME 必须是你类中定义的表名常量
                sql = f"DELETE FROM {CASE_STEP_TABLE_NAME} WHERE case_id IN ({placeholders})"

                # 3. 执行 SQL
                # execute 的第二个参数必须是元组或列表，这里直接传入 case_ids 即可
                cursor.execute(sql, case_ids)

                # 4. 获取受影响行数
                deleted_count = cursor.rowcount

                # 5. 提交事务
                conn.commit()

                logger.info(f"批量删除步骤成功：涉及 case_id {case_ids}，共清理 {deleted_count} 条步骤数据")
                success = True

        except sqlite3.Error as e:
            logger.exception(f"数据库批量删除步骤失败：{str(e)}")
        except Exception as e:
            logger.exception(f"删除步骤时发生未知错误: {str(e)}")

        return success

    def delete_case_step(self, step_id: int):
        if step_id <= 0:
            logger.warning(f"删除step失败：无效的ID（{step_id}），ID必须为正整数")
            return False

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 2. 先检查该ID是否存在（避免误判删除成功）
                cursor.execute(
                    f"SELECT 1 FROM {CASE_STEP_TABLE_NAME} WHERE id = ?",
                    (step_id,)
                )
                if not cursor.fetchone():
                    logger.warning(f"删除Case失败：ID={step_id} 的记录不存在")
                    return False

                # 3. 执行单个删除操作
                cursor.execute(
                    f"DELETE FROM {CASE_TABLE_NAME} WHERE id = ?",
                    (step_id,)
                )
                conn.commit()

                # 4. 验证删除结果（rowcount 为受影响的行数）
                if cursor.rowcount == 1:
                    logger.info(f"成功删除单个step：ID={step_id}")
                    return True
                else:
                    logger.error(f"删除step异常：ID={step_id} 匹配但未删除（rowcount={cursor.rowcount}）")
                    return False

        except sqlite3.Error as e:
            logger.exception(f"删除单个step失败（ID={step_id}）：{str(e)}")
            return False

    def upsert_case_step(self, case_step: DiagnosisStepData) -> Optional[int]:
        """
        插入或更新诊断案例数据（UPSERT）
        :param case_step: DiagnosisStepData 对象
        :return: 成功返回记录ID，失败返回None
        """
        if not isinstance(case_step, DiagnosisStepData):
            logger.error("传入的不是有效的DiagnosisStepData对象")
            return None

        try:
            # 转换为字典
            case_dict = case_step.to_dict()
            primary_key = case_step.get_attr_names()[0]

            # 提取字段和值
            fields = list(case_dict.keys())
            values = list(case_dict.values())

            # 构建插入SQL（使用SQLite的UPSERT语法 ON CONFLICT）
            placeholders = ', '.join(['?'] * len(fields))
            update_clause = ', '.join([f"{field}=excluded.{field}" for field in fields if field != primary_key])

            insert_sql = f"""
                INSERT INTO {CASE_STEP_TABLE_NAME} ({', '.join(fields)})
                VALUES ({placeholders})
                ON CONFLICT({primary_key}) DO UPDATE SET
                {update_clause}
            """
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # 执行插入/更新
                cursor.execute(insert_sql, values)

                # 获取插入/更新后的ID
                if case_dict[primary_key] is None:  # 新增记录
                    case_id = cursor.lastrowid
                else:  # 更新记录
                    case_id = case_dict[primary_key]

                conn.commit()

                logger.info(f"案例数据{'新增' if case_dict[primary_key] == 0 else '更新'}成功，ID: {case_id}")
                return case_id

        except sqlite3.Error as e:
            logger.exception(f"案例数据插入/更新失败：{str(e)}")
            return None

    def get_case_steps_by_case_id(self, case_id: int) -> List[DiagnosisStepData]:
        """
        根据case_id读取步骤，并按step_sequence排序

        Args:
            case_id: 用例ID

        Returns:
            排序后的步骤列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # 查询指定case_id的所有步骤，按step_sequence升序排列
                cursor.execute(f"""
                    SELECT * FROM {CASE_STEP_TABLE_NAME} 
                    WHERE case_id = ? 
                    ORDER BY step_sequence ASC
                """, (case_id,))

                # 获取列名
                columns = [desc[0] for desc in cursor.description]
                # 转换为DiagnosisStepData对象列表
                steps = []
                for row in cursor.fetchall():
                    row_dict = dict(zip(columns, row))
                    step = DiagnosisStepData()
                    step.update_from_dict(row_dict)
                    steps.append(step)

                logger.info(f"成功读取case_id={case_id}的步骤，共{len(steps)}条")
                return steps

        except sqlite3.Error as e:
            logger.exception(f"读取case_id={case_id}的步骤失败：{str(e)}")
            return []

    def fix_case_step_sequence(self, case_id: int) -> bool:
        """
        修复指定case_id的步骤序列，确保step_sequence从1开始连续递增

        Args:
            case_id: 用例ID

        Returns:
            是否成功修复
        """
        try:
            # 1. 读取当前步骤
            steps = self.get_case_steps_by_case_id(case_id)
            if not steps:
                logger.info(f"case_id={case_id}没有步骤需要修复")
                return True

            # 2. 检查是否需要修复
            need_fix = False
            for idx, step in enumerate(steps):
                expected_sequence = idx + 1
                if step.step_sequence != expected_sequence:
                    need_fix = True
                    break

            if not need_fix:
                logger.info(f"case_id={case_id}的步骤序列已经是连续的，无需修复")
                return True

            # 3. 执行修复
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 按当前顺序更新step_sequence
                for idx, step in enumerate(steps):
                    new_sequence = idx + 1
                    if step.step_sequence != new_sequence:
                        logger.info(
                            f"更新case_id={case_id}步骤ID={step.id}的sequence: {step.step_sequence} -> {new_sequence}")
                        cursor.execute(f"""
                            UPDATE {CASE_STEP_TABLE_NAME} 
                            SET step_sequence = ? 
                            WHERE id = ?
                        """, (new_sequence, step.id))

                conn.commit()
                logger.info(f"成功修复case_id={case_id}的步骤序列，共更新{len(steps)}条记录")
                return True

        except sqlite3.Error as e:
            logger.exception(f"修复case_id={case_id}的步骤序列失败：{str(e)}")
            return False

    def get_and_fix_steps_by_case_id(self, case_id: int) -> List[DiagnosisStepData]:
        """
        读取指定case_id的步骤，自动修复序列问题后返回

        Args:
            case_id: 用例ID

        Returns:
            修复后的步骤列表
        """
        # 先修复序列
        self.fix_case_step_sequence(case_id)
        # 重新读取修复后的步骤
        return self.get_case_steps_by_case_id(case_id)

    def delete_case(self, case_id: int):
        if case_id <= 0:
            logger.warning(f"删除Case失败：无效的ID（{case_id}），ID必须为正整数")
            return False

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 2. 先检查该ID是否存在（避免误判删除成功）
                cursor.execute(
                    f"SELECT 1 FROM {CASE_TABLE_NAME} WHERE id = ?",
                    (case_id,)
                )
                if not cursor.fetchone():
                    logger.warning(f"删除Case失败：ID={case_id} 的记录不存在")
                    return False

                # 3. 执行单个删除操作
                cursor.execute(
                    f"DELETE FROM {CASE_TABLE_NAME} WHERE id = ?",
                    (case_id,)
                )
                conn.commit()

                # 4. 验证删除结果（rowcount 为受影响的行数）
                if cursor.rowcount == 1:
                    logger.info(f"成功删除单个Case：ID={case_id}")
                    return True
                else:
                    logger.error(f"删除Case异常：ID={case_id} 匹配但未删除（rowcount={cursor.rowcount}）")
                    return False

        except sqlite3.Error as e:
            logger.exception(f"删除单个Case失败（ID={case_id}）：{str(e)}")
            return False

    def upsert_case(self, case: DiagCase) -> Optional[int]:
        """
        插入或更新诊断案例数据（UPSERT）
        :param case: DiagCase 对象
        :return: 成功返回记录ID，失败返回None
        """
        if not isinstance(case, DiagCase):
            logger.error("传入的不是有效的DiagCase对象")
            return None

        try:
            # 转换为字典
            case_dict = case.to_dict()
            primary_key = DiagCase().get_attr_names()[0]

            # 提取字段和值
            fields = list(case_dict.keys())
            values = list(case_dict.values())

            # 构建插入SQL（使用SQLite的UPSERT语法 ON CONFLICT）
            placeholders = ', '.join(['?'] * len(fields))
            update_clause = ', '.join([f"{field}=excluded.{field}" for field in fields if field != primary_key])

            insert_sql = f"""
                INSERT INTO {CASE_TABLE_NAME} ({', '.join(fields)})
                VALUES ({placeholders})
                ON CONFLICT({primary_key}) DO UPDATE SET
                {update_clause}
            """
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # 执行插入/更新
                cursor.execute(insert_sql, values)

                # 获取插入/更新后的ID
                if case_dict[primary_key] is None:  # 新增记录
                    case_id = cursor.lastrowid
                else:  # 更新记录
                    case_id = case_dict[primary_key]

                conn.commit()

                logger.info(f"案例数据{'新增' if case_dict[primary_key] == 0 else '更新'}成功，ID: {case_id}")
                return case_id

        except sqlite3.Error as e:
            logger.exception(f"案例数据插入/更新失败：{str(e)}")
            return None

    def batch_upsert_cases(self, cases: list[DiagCase]) -> tuple[int, list[int]]:
        """
        批量插入/更新诊断案例
        :param cases: DiagCase 对象列表
        :return: (成功数量, 成功ID列表)
        """
        if not cases or not isinstance(cases, list):
            logger.error("传入的案例列表无效")
            return 0, []

        success_count = 0
        success_ids = []

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                primary_key = DiagCase().get_attr_names()[0]

                for case in cases:
                    if not isinstance(case, DiagCase):
                        logger.warning("跳过无效的案例对象")
                        continue

                    case_dict = case.to_dict()
                    fields = list(case_dict.keys())
                    values = list(case_dict.values())

                    placeholders = ', '.join(['?'] * len(fields))
                    update_clause = ', '.join([f"{field}=excluded.{field}" for field in fields if field != primary_key])

                    insert_sql = f"""
                        INSERT INTO {CASE_TABLE_NAME} ({', '.join(fields)})
                        VALUES ({placeholders})
                        ON CONFLICT({primary_key}) DO UPDATE SET
                        {update_clause}
                    """

                    try:
                        cursor.execute(insert_sql, values)
                        # 获取ID
                        if case_dict[primary_key] == 0:
                            case_id = cursor.lastrowid
                        else:
                            case_id = case_dict[primary_key]

                        success_count += 1
                        success_ids.append(case_id)
                    except sqlite3.Error as e:
                        logger.warning(f"单个案例处理失败：{str(e)}，案例数据：{case_dict}")

                conn.commit()
                logger.info(f"批量处理完成，成功{success_count}/{len(cases)}条记录")
                return success_count, success_ids

        except sqlite3.Error as e:
            logger.exception(f"批量插入/更新失败：{str(e)}")
            return success_count, success_ids

    def get_current_config_uds_cases(self) -> list[DiagCase]:
        """获取当前配置下所有的case"""
        active_config_name = self.get_active_config_name()

        return self.get_config_uds_cases(active_config_name)

    def get_config_uds_cases(self, config_name: str) -> list[DiagCase]:
        """获取指定配置下所有的case"""
        cases = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 设置行工厂，使查询结果可以通过列名访问
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # 构建查询SQL：查询当前配置下的所有case（排除group类型，如需包含可去掉type条件）
                query_sql = f"""
                                    SELECT * FROM {CASE_TABLE_NAME} 
                                    WHERE config_name = ? 
                                """

                # 执行查询（使用参数化查询防止SQL注入）
                cursor.execute(query_sql, (config_name,))

                # 获取所有结果并转换为DiagCase对象
                rows = cursor.fetchall()
                for row in rows:
                    # 将sqlite3.Row转换为字典
                    row_dict = dict(row)
                    # 从字典创建DiagCase实例
                    case = DiagCase.from_dict(row_dict)
                    cases.append(case)

                logger.info(f"成功获取当前配置[{config_name}]下的case，共{len(cases)}条")

        except sqlite3.OperationalError as e:
            if "no such table" in str(e).lower():
                logger.error(f"表{CASE_TABLE_NAME}不存在，请先初始化数据库：{str(e)}")
            else:
                logger.exception(f"数据库操作错误（获取case）：{str(e)}")
        except sqlite3.Error as e:
            logger.exception(f"数据库查询失败（获取case）：{str(e)}")
        except Exception as e:
            # 捕获其他所有异常
            logger.exception(f"获取当前配置下的case失败: {str(e)}")

        return cases

    def delete_config_uds_cases(self, config_name: str) -> int:
        """删除指定配置下的所有case"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                if not config_name:
                    logger.warning("尝试删除case失败：未获取到有效的当前配置名")
                    return False

                delete_sql = f"DELETE FROM {CASE_TABLE_NAME} WHERE config_name = ?"

                cursor.execute(delete_sql, (config_name,))

                deleted_count = cursor.rowcount

                conn.commit()

                logger.info(f"成功删除配置[{config_name}]下的所有case，共清理{deleted_count}条数据")

        except sqlite3.OperationalError as e:
            if "no such table" in str(e).lower():
                logger.error(f"删除失败，表{CASE_TABLE_NAME}不存在：{str(e)}")
            else:
                logger.exception(f"数据库操作错误（删除case）：{str(e)}")
        except sqlite3.Error as e:
            # 回滚事务（虽然 with 上下文通常会自动处理回滚，但显式捕获异常更稳健）
            # conn.rollback() # with 语句块在异常时会自动 rollback
            logger.exception(f"数据库执行删除失败：{str(e)}")
        except Exception as e:
            logger.exception(f"删除当前配置下的case时发生未知错误: {str(e)}")

        return deleted_count

    def get_services_json(self, config_name: str):
        """
        从服务配置表中获取指定config_name对应的services_json

        参数:
            config_name: 要查询的配置名称（主键）

        返回:
            若存在对应记录，返回services_json字符串；否则返回None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                query_sql = f"""
                                SELECT services_json 
                                FROM {SERVICES_TABLE_NAME} 
                                WHERE config_name = ?
                            """
                # 执行查询
                cursor.execute(query_sql, (config_name,))

                # 获取结果（fetchone返回单条记录，格式为元组，取第一个元素）
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            # 捕获异常（如表不存在、连接错误等）
            logger.exception(f"获取services_json失败: {str(e)}")
            return None

    def _check_services_is_exists(self, conn: sqlite3.Connection, config_name: str) -> bool:
        """
        检查ServicesTable中是否存在指定配置名
        :param conn: 数据库conn
        :param config_name: 要检查的配置名
        :return: 存在返回True，否则False
        """
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT 1 FROM {SERVICES_TABLE_NAME} 
                WHERE config_name = ?
                LIMIT 1
            """, (config_name,))  # 使用参数化查询，避免SQL注入
            return cursor.fetchone() is not None
        except sqlite3.Error as e:
            logger.exception(f"检查配置存在性失败：{str(e)}")
            return False

    def save_uds_config(self, config_obj: UdsConfig):
        """
        将 Pydantic 配置对象保存到数据库。
        如果 config_name 已存在，则覆盖旧数据 (Upsert)。
        """
        config_name = getattr(config_obj, 'config_name', 'default')
        json_data = config_obj.to_json()
        sql = f"""
                INSERT OR REPLACE INTO {UDS_CONFIG_TABLE_NAME} 
                (config_name, json_data) VALUES (?, ?)
            """
        with sqlite3.connect(self.db_path) as conn:
            # 使用 REPLACE 语法实现 Upsert (Update or Insert)
            conn.execute(sql, (config_name, json_data))
            conn.commit()
            logger.info(f"Saved: {config_name}")


    def delete_services_config(self, config_name: str) -> bool:
        delete_sql = f"DELETE FROM {SERVICES_TABLE_NAME} WHERE config_name = ?;"
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(delete_sql, (config_name,))
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"删除配置成功：{config_name}")
                    return True
                else:
                    logger.warning(f"删除失败：未找到配置 {config_name}")
                    return False
        except sqlite3.Error as e:
            logger.exception(f"删除配置异常：{config_name} - {str(e)}")
            return False

    def add_services_config(self, config_name: str, services_json: str) -> bool:
        """
        向ServicesTable添加配置（若已存在则更新）
        :param config_name: 配置名
        :param services_json: 配置数据,JSON字符串
        :return: 操作成功返回True，否则False
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                                INSERT OR REPLACE INTO {SERVICES_TABLE_NAME} 
                                (config_name, services_json) VALUES (?, ?)
                            """, (config_name, services_json))
                conn.commit()
                logger.debug(f'添加/更新Service配置成功')
                return True
        except Exception as e:
            logger.exception(f"添加/更新配置失败：{str(e)}")
            return False

    def _insert_default_doip_config_name(self, conn: sqlite3.Connection):
        """内部方法：首次将默认配置名称写入 current_active_config 表"""
        insert_meta_sql = f"""
        INSERT INTO {CURRENT_CONFIG_TABLE_NAME} (key, active_config_name) 
        VALUES ('singleton_key', ?);
        """
        try:
            cursor = conn.cursor()
            # 使用默认配置实例的 config_name
            cursor.execute(insert_meta_sql, (UdsConfig().config_name,))
            conn.commit()
            logger.info(f"成功将 '{UdsConfig().config_name}' 设置为当前激活配置。")
        except sqlite3.Error as e:
            logger.exception(f"设置激活配置名称失败: {str(e)}")

    def set_active_config(self, new_config_name: str) -> bool:
        """
        更新当前激活的配置名称。

        由于 current_active_config 表设计为单行（key='singleton_key'），
        我们使用 UPDATE 语句来修改这一行的值。

        :param new_config_name: 要设置为激活状态的配置名称 (必须存在于 doip_config 表中)。
        :return: 成功返回 True，失败返回 False。
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 1. 验证新的配置名称是否在 doip_config 表中存在
                cursor.execute(f"SELECT COUNT(*) FROM {UDS_CONFIG_TABLE_NAME} WHERE config_name = ?",
                               (new_config_name,))
                if cursor.fetchone()[0] == 0:
                    logger.warning(f"更新失败：配置名称 '{new_config_name}' 在 {UDS_CONFIG_TABLE_NAME} 表中不存在。")
                    return False

                # 2. 更新 current_active_config 表中的唯一一行数据
                update_sql = f"""
                UPDATE {CURRENT_CONFIG_TABLE_NAME}
                SET active_config_name = ?
                WHERE key = 'singleton_key';
                """
                cursor.execute(update_sql, (new_config_name,))
                conn.commit()

                if cursor.rowcount > 0:
                    logger.info(f"成功将当前激活配置更新为: {new_config_name}")
                    return True
                else:
                    # 理论上 init_database 已经保证了这一行存在，但这作为失败备用
                    logger.error(
                        f"更新失败：无法找到 key='singleton_key' 的记录。请检查 {CURRENT_CONFIG_TABLE_NAME} 表是否为空。")
                    return False

        except sqlite3.Error as e:
            logger.exception(f"更新当前激活配置名称失败：{str(e)}")
            return False

    def get_active_config_name(self) -> Optional[str]:
        """获取当前激活的配置名称。"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                select_sql = f"SELECT active_config_name FROM {CURRENT_CONFIG_TABLE_NAME} WHERE key = 'singleton_key';"
                cursor.execute(select_sql)
                result = cursor.fetchone()
                if result:
                    return result[0]
                return None
        except sqlite3.Error as e:
            logger.exception(f"获取当前激活配置名称失败：{str(e)}")
            return None

    def load_uds_config(self, config_name: str) -> Optional[FlashConfig]:
        """读取配置，返回 FlashConfig 对象"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(f"SELECT json_data FROM {UDS_CONFIG_TABLE_NAME} WHERE name = ?", (config_name,))
            row = cursor.fetchone()
            if row:
                try:
                    return FlashConfig.from_json(row[0])
                except Exception as e:
                    logger.exception(f'读取uds配置错误：{e}')
                    return None
            return None

    def query_uds_config(self, config_name: str) -> Optional[UdsConfig]:
        """
        查询指定名称的 DOIP 配置 (动态字段)
        """
        with sqlite3.connect(self.db_path) as conn:
            try:
                cursor = conn.execute(f"SELECT json_data FROM {UDS_CONFIG_TABLE_NAME} WHERE config_name = ?", (config_name,))
            except Exception as e:
                logger.exception(str(e))
            row = cursor.fetchone()
            if row:
                try:
                    return UdsConfig.from_json(row[0])
                except Exception as e:
                    logger.exception(f'读取uds配置错误：{e}')
                    return None
            return None

    def delete_doip_config(self, config_name: str) -> bool:
        """
        根据配置名称删除 DOIP 配置
        :param config_name: 配置名称（主键）
        :return: 删除成功返回 True，失败返回 False
        """
        delete_sql = f"DELETE FROM {UDS_CONFIG_TABLE_NAME} WHERE config_name = ?;"
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(delete_sql, (config_name,))
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"删除配置成功：{config_name}")
                    return True
                else:
                    logger.warning(f"删除失败：未找到配置 {config_name}")
                    return False
        except sqlite3.Error as e:
            logger.exception(f"删除配置异常：{config_name} - {str(e)}")
            return False

    def get_all_config_names(self) -> List[str]:
        """
        获取 doip_config 表中所有的配置名称
        :return: 配置名称列表（为空则返回空列表）
        """
        query_sql = f"SELECT config_name FROM {UDS_CONFIG_TABLE_NAME} ORDER BY config_name ASC;"
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(query_sql)
                # 提取所有配置名称，转换为列表（fetchall() 返回 [(name1,), (name2,), ...] 格式）
                results = cursor.fetchall()
                config_names = [row[0] for row in results]

            logger.info(f"查询到 {len(config_names)} 个配置名称")
            return config_names
        except sqlite3.Error as e:
            logger.exception(f"查询所有配置名称异常：{str(e)}")
            return []
