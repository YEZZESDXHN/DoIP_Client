import logging
import sqlite3
from typing import Optional, List

from user_data import DoIPConfig, DEFAULT_SERVICES

logger = logging.getLogger('UDSOnIPClient.' + __name__)

DOIP_CONFIG_TABLE_NAME = "DoIP_Config"
CURRENT_CONFIG_TABLE_NAME = 'current_active_config'
SERVICES_TABLE_NAME = 'services_table'


class DBManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.default_config = DoIPConfig()
        self.keys_tuple = self.default_config.get_attr_names()
        self.primary_key = DoIPConfig().get_attr_names()[0]
        self.init_config_database()
        self.init_services_database()

    def init_config_database(self):
        # --- 动态生成 CREATE TABLE SQL(doip config) ---
        field_definitions = []
        for field, value in DoIPConfig().to_dict().items():
            # 确定 SQL 类型和约束
            sql_type = 'TEXT' if isinstance(value, str) else 'INTEGER'
            constraints = 'PRIMARY KEY' if field == self.primary_key else 'NOT NULL'

            # 添加 DEFAULT 子句（如果不是主键）
            if field != self.primary_key:
                constraints += f" DEFAULT {repr(value)}"

            field_definitions.append(f"{field} {sql_type} {constraints}")

        fields_sql = ',\n'.join(field_definitions)
        create_doip_config_sql = f"""
                CREATE TABLE IF NOT EXISTS {DOIP_CONFIG_TABLE_NAME} (
                    {fields_sql}
                );
                """

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
                cursor.execute(create_doip_config_sql)
                cursor.execute(create_current_config_sql)
                conn.commit()
                logger.info(f"数据库初始化完成！{DOIP_CONFIG_TABLE_NAME} ，{CURRENT_CONFIG_TABLE_NAME}表创建/验证成功")

                # 检查表中是否有数据
                cursor.execute(f"SELECT COUNT(*) FROM {DOIP_CONFIG_TABLE_NAME}")
                count = cursor.fetchone()[0]

                if count == 0:
                    # 如果没有数据，插入默认配置
                    self._insert_default_doip_config(conn)
                else:
                    logger.info(f"表 {DOIP_CONFIG_TABLE_NAME} 中已存在 {count} 条配置，跳过写入默认配置。")

                # 检查并设置当前激活的配置名称到激活配置表
                cursor.execute(f"SELECT COUNT(*) FROM {CURRENT_CONFIG_TABLE_NAME}")
                meta_count = cursor.fetchone()[0]

                if meta_count == 0:
                    # 如果激活配置表是空的，将默认配置设为激活
                    self._insert_default_doip_config_name(conn)
                else:
                    logger.info(f"表 {CURRENT_CONFIG_TABLE_NAME} 中已存在激活配置记录，跳过设置。")

        except sqlite3.Error as e:
            logger.exception(f"初始化数据库失败：{e}")

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
            logger.exception(f"services初始化数据库失败：{e}")

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
            logger.exception(f"检查配置存在性失败：{e}")
            return False
    def _insert_default_doip_config(self, conn: sqlite3.Connection):
        """内部方法：将默认配置写入数据库"""
        # 构建 SQL 插入语句
        keys = ', '.join(self.keys_tuple)
        # 使用 ? 占位符防止 SQL 注入
        placeholders = ', '.join(['?'] * len(self.keys_tuple))
        insert_sql = f"""
        INSERT INTO {DOIP_CONFIG_TABLE_NAME} ({keys}) 
        VALUES ({placeholders})
        """

        values = self.default_config.to_tuple()

        try:
            cursor = conn.cursor()
            cursor.execute(insert_sql, values)
            conn.commit()
            logger.info(f"成功写入默认配置: {self.default_config.config_name}")
        except sqlite3.Error as e:
            logger.exception(f"写入默认配置失败: {e}")

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
            logger.exception(f"添加/更新配置失败：{e}")
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
            cursor.execute(insert_meta_sql, (DoIPConfig().config_name,))
            conn.commit()
            logger.info(f"成功将 '{DoIPConfig().config_name}' 设置为当前激活配置。")
        except sqlite3.Error as e:
            logger.exception(f"设置激活配置名称失败: {e}")

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
                cursor.execute(f"SELECT COUNT(*) FROM {DOIP_CONFIG_TABLE_NAME} WHERE config_name = ?",
                               (new_config_name,))
                if cursor.fetchone()[0] == 0:
                    logger.warning(f"更新失败：配置名称 '{new_config_name}' 在 {DOIP_CONFIG_TABLE_NAME} 表中不存在。")
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
            logger.exception(f"更新当前激活配置名称失败：{e}")
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
            logger.exception(f"获取当前激活配置名称失败：{e}")
            return None

    def add_doip_config(self, config: DoIPConfig) -> bool:
        """
        新增 DOIP 配置 (动态字段)
        """
        keys = ', '.join(self.keys_tuple)
        placeholders = ', '.join(['?'] * len(self.keys_tuple))
        insert_sql = f"""
        INSERT INTO {DOIP_CONFIG_TABLE_NAME} ({keys})
        VALUES ({placeholders});
        """
        values = config.to_tuple()

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(insert_sql, values)
            logger.info(f"新增 DOIP 配置成功：{config}")
            return True
        except sqlite3.IntegrityError as e:
            logger.error(f"新增配置失败（主键重复/约束冲突）：{config.config_name} - {e}")
            return False
        except sqlite3.Error as e:
            logger.exception(f"新增配置异常：{config.config_name} - {e}")
            return False

    def query_doip_config(self, config_name: str) -> Optional[DoIPConfig]:
        """
        查询指定名称的 DOIP 配置 (动态字段)
        """
        keys = ', '.join(self.keys_tuple)
        query_sql = f"SELECT {keys} FROM {DOIP_CONFIG_TABLE_NAME} WHERE config_name = ?;"
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(query_sql, (config_name,))
                result = cursor.fetchone()

            if result:
                logger.info(f"查询到配置：{config_name}")
                # 动态创建 DoIPConfig 实例
                config_data = dict(zip(self.keys_tuple, result))
                return DoIPConfig(**config_data)
            else:
                logger.warning(f"未找到配置：{config_name}")
                return None
        except sqlite3.Error as e:
            logger.exception(f"查询配置异常：{config_name} - {e}")
            return None

    def query_all_doip_configs(self) -> List[DoIPConfig]:
        """
        查询所有 DOIP 配置 (动态字段)
        """
        keys = ', '.join(self.keys_tuple)
        query_sql = f"SELECT {keys} FROM {DOIP_CONFIG_TABLE_NAME} ORDER BY config_name ASC;"
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(query_sql)
                results = cursor.fetchall()

            config_list = []
            for row in results:
                # 动态创建 DoIPConfig 实例
                config_data = dict(zip(self.keys_tuple, row))
                config_list.append(DoIPConfig(**config_data))

            logger.info(f"查询到 {len(config_list)} 条配置")
            return config_list
        except sqlite3.Error as e:
            logger.exception(f"查询所有配置异常：{e}")
            return []

    def update_doip_config(self, config: DoIPConfig) -> bool:
        """
        更新 DOIP 配置 (动态字段)
        """
        set_clauses = ', '.join([f"{key} = ?" for key in config.get_attr_names()[1:]])

        update_sql = f"""
        UPDATE {DOIP_CONFIG_TABLE_NAME}
        SET {set_clauses}
        WHERE {self.primary_key} = ?;
        """
        # 值：更新字段的值 + 主键的值
        values = config.to_tuple()[1:] + (config.config_name,)

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(update_sql, values)
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"更新配置成功：{config}")
                    return True
                else:
                    logger.warning(f"更新失败：未找到配置 {config.config_name}")
                    return False
        except sqlite3.Error as e:
            logger.exception(f"更新配置异常：{config.config_name} - {e}")
            return False

    def delete_doip_config(self, config_name: str) -> bool:
        """
        根据配置名称删除 DOIP 配置
        :param config_name: 配置名称（主键）
        :return: 删除成功返回 True，失败返回 False
        """
        delete_sql = f"DELETE FROM {DOIP_CONFIG_TABLE_NAME} WHERE config_name = ?;"
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
            logger.exception(f"删除配置异常：{config_name} - {e}")
            return False

    def get_all_config_names(self) -> List[str]:
        """
        获取 doip_config 表中所有的配置名称
        :return: 配置名称列表（为空则返回空列表）
        """
        query_sql = f"SELECT config_name FROM {DOIP_CONFIG_TABLE_NAME} ORDER BY config_name ASC;"
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(query_sql)
                # 提取所有配置名称，转换为列表（fetchall() 返回 [(name1,), (name2,), ...] 格式）
                results = cursor.fetchall()
                config_names = [row[0] for row in results]

            logger.info(f"查询到 {len(config_names)} 个配置名称")
            return config_names
        except sqlite3.Error as e:
            logger.exception(f"查询所有配置名称异常：{e}")
            return []
