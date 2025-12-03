import base64
import logging
import sqlite3
from enum import Enum
from os import PathLike
from typing import Union, Optional, List

from user_data import DoIPConfig

DOIP_CONFIG_TABLE_NAME = "DoIP_Config"
CURRENT_CONFIG_TABLE_NAME = 'current_active_config'
DIAG_TREE_TABLE_NAME = "Diag_Tree"
DIAG_PROCESS_TABLE_NAME = "Diag_Process"

logger = logging.getLogger('UDSOnIPClient.' + __name__)


DEFAULT_DOIP_CONFIG_INSTANCE = DoIPConfig(
    config_name='default_config',
    tester_logical_address=0x7e2,
    dut_logical_address=0x773,
    dut_ipv4_address='172.16.104.70',
)
def json_default_converter(obj):
    """
    一个自定义转换器，用于处理 JSON 无法直接序列化的对象。
    如果对象是 bytes 类型，则将其转换为 Base64 编码的字符串。
    如果对象是 bool 类型，则将其转换为 int。
    """
    if isinstance(obj, bytes):
        # 1. Base64 编码 (bytes -> bytes)
        encoded_bytes = base64.b64encode(obj)
        # 2. 转换为 UTF-8 字符串 (bytes -> str)
        return encoded_bytes.decode('utf-8')

    if isinstance(obj, bool):
        return 1 if obj else 0

    # 对于其他无法序列化的对象（如 datetime 对象），可以抛出 TypeError
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def sql_converter(obj):
    """
    一个自定义转换器，用于处理 spl 无法直接序列化的对象。
    如果对象是 bytes 类型，则将其转换为 int
    如果对象是 bool 类型，则将其转换为 int。
    """
    if isinstance(obj, bytes):
        return int.from_bytes(
            obj,
            byteorder='big',  # 假设采用大端序（网络字节序）
            signed=False  # 假设它是无符号整数
        )

    if isinstance(obj, bool):
        return 1 if obj else 0

    if isinstance(obj, Enum):
        return obj.value

    return obj


class DBManager:
    def __init__(self, database: Union[str, bytes, PathLike[str], PathLike[bytes]]):
        self.database = database  # 数据库路径/名称
        # 预先获取字段名和默认值，用于动态 SQL
        self.config_fields = DEFAULT_DOIP_CONFIG_INSTANCE.to_dict()
        self.field_names = list(self.config_fields.keys())
        self.primary_key = 'config_name'
        self.init_database()      # 初始化时自动建表

    def init_database(self):
        """初始化数据库：创建 doip_config 表并确保存在默认配置"""

        # --- 动态生成 CREATE TABLE SQL ---
        field_definitions = []
        for field, value in self.config_fields.items():
            # 确定 SQL 类型和约束
            sql_type = 'TEXT' if isinstance(value, str) else 'INTEGER'
            constraints = 'PRIMARY KEY' if field == self.primary_key else 'NOT NULL'

            # 添加 DEFAULT 子句（如果不是主键）
            if field != self.primary_key:
                # 使用 sql_converter 转换默认值，确保 SQL 格式正确
                default_value = sql_converter(value)
                constraints += f" DEFAULT {repr(default_value)}"

            field_definitions.append(f"{field} {sql_type} {constraints}")

        fields_sql = ',\n'.join(field_definitions)
        create_doip_config_sql = f"""
        CREATE TABLE IF NOT EXISTS {DOIP_CONFIG_TABLE_NAME} (
            {fields_sql}
        );
        """
        # ---------------------------------

        create_current_config_sql = f"""
                CREATE TABLE IF NOT EXISTS {CURRENT_CONFIG_TABLE_NAME} (
                    key TEXT PRIMARY KEY,
                    active_config_name TEXT NOT NULL
                );
                """

        try:
            with sqlite3.connect(self.database) as conn:
                cursor = conn.cursor()
                cursor.execute(create_doip_config_sql)
                cursor.execute(create_current_config_sql)
                conn.commit()
                logger.info(f"数据库初始化完成！{DOIP_CONFIG_TABLE_NAME} ，{CURRENT_CONFIG_TABLE_NAME}表创建/验证成功")

                # 检查表中是否有数据
                cursor.execute(f"SELECT COUNT(*) FROM {DOIP_CONFIG_TABLE_NAME}")
                count = cursor.fetchone()[0]

                if count == 0:
                    # 3. 如果没有数据，插入默认配置
                    self._insert_default_config(conn)
                else:
                    logger.info(f"表 {DOIP_CONFIG_TABLE_NAME} 中已存在 {count} 条配置，跳过写入默认配置。")

                # 检查并设置当前激活的配置名称到激活配置表
                cursor.execute(f"SELECT COUNT(*) FROM {CURRENT_CONFIG_TABLE_NAME}")
                meta_count = cursor.fetchone()[0]

                if meta_count == 0:
                    # 如果激活配置表是空的，将默认配置设为激活
                    self._insert_default_config_name(conn)
                else:
                    logger.info(f"表 {CURRENT_CONFIG_TABLE_NAME} 中已存在激活配置记录，跳过设置。")

        except sqlite3.Error as e:
            logger.exception(f"初始化数据库失败：{e}")

    def _insert_default_config_name(self, conn: sqlite3.Connection):
        """内部方法：首次将默认配置名称写入 current_active_config 表"""
        insert_meta_sql = f"""
        INSERT INTO {CURRENT_CONFIG_TABLE_NAME} (key, active_config_name) 
        VALUES ('singleton_key', ?);
        """
        try:
            cursor = conn.cursor()
            # 使用默认配置实例的 config_name
            cursor.execute(insert_meta_sql, (DEFAULT_DOIP_CONFIG_INSTANCE.config_name,))
            conn.commit()
            logger.info(f"成功将 '{DEFAULT_DOIP_CONFIG_INSTANCE.config_name}' 设置为当前激活配置。")
        except sqlite3.Error as e:
            logger.exception(f"设置激活配置名称失败: {e}")

    def _insert_default_config(self, conn: sqlite3.Connection):
        """内部方法：将默认配置写入数据库"""

        # 转换为字典并使用 sql_converter 转换默认配置中的值
        converted_config = {}
        for key, value in DEFAULT_DOIP_CONFIG_INSTANCE.to_dict().items():
            converted_config[key] = sql_converter(value)

        # 构建 SQL 插入语句 (使用 self.field_names 保证顺序与 asdict 结果一致)
        keys = ', '.join(self.field_names)
        # 使用 ? 占位符防止 SQL 注入
        placeholders = ', '.join(['?'] * len(self.field_names))
        insert_sql = f"""
        INSERT INTO {DOIP_CONFIG_TABLE_NAME} ({keys}) 
        VALUES ({placeholders})
        """

        # 准备要插入的值，保持顺序与 keys (self.field_names) 一致
        values = tuple(converted_config[key] for key in self.field_names)

        try:
            cursor = conn.cursor()
            cursor.execute(insert_sql, values)
            conn.commit()
            logger.info(f"成功写入默认配置: {DEFAULT_DOIP_CONFIG_INSTANCE.config_name}")
        except sqlite3.Error as e:
            logger.exception(f"写入默认配置失败: {e}")

    def set_active_config(self, new_config_name: str) -> bool:
        """
        更新当前激活的配置名称。

        由于 current_active_config 表设计为单行（key='singleton_key'），
        我们使用 UPDATE 语句来修改这一行的值。

        :param new_config_name: 要设置为激活状态的配置名称 (必须存在于 doip_config 表中)。
        :return: 成功返回 True，失败返回 False。
        """
        try:
            with sqlite3.connect(self.database) as conn:
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
            with sqlite3.connect(self.database) as conn:
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
        keys = ', '.join(self.field_names)
        placeholders = ', '.join(['?'] * len(self.field_names))
        insert_sql = f"""
        INSERT INTO {DOIP_CONFIG_TABLE_NAME} ({keys})
        VALUES ({placeholders});
        """
        # 使用 asdict() 获取所有字段的值，并按 field_names 顺序排列
        config_dict = config.to_dict()
        values = tuple(sql_converter(config_dict[key]) for key in self.field_names)

        try:
            with sqlite3.connect(self.database) as conn:
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
        keys = ', '.join(self.field_names)
        query_sql = f"SELECT {keys} FROM {DOIP_CONFIG_TABLE_NAME} WHERE config_name = ?;"
        try:
            with sqlite3.connect(self.database) as conn:
                cursor = conn.execute(query_sql, (config_name,))
                result = cursor.fetchone()

            if result:
                logger.info(f"查询到配置：{config_name}")
                # 动态创建 DoIPConfig 实例
                config_data = dict(zip(self.field_names, result))
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
        keys = ', '.join(self.field_names)
        query_sql = f"SELECT {keys} FROM {DOIP_CONFIG_TABLE_NAME} ORDER BY config_name ASC;"
        try:
            with sqlite3.connect(self.database) as conn:
                cursor = conn.execute(query_sql)
                results = cursor.fetchall()

            config_list = []
            for row in results:
                # 动态创建 DoIPConfig 实例
                config_data = dict(zip(self.field_names, row))
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
        update_data = config.to_update_dict()  # 不包含 config_name
        set_clauses = ', '.join([f"{key} = ?" for key in update_data.keys()])

        update_sql = f"""
        UPDATE {DOIP_CONFIG_TABLE_NAME}
        SET {set_clauses}
        WHERE {self.primary_key} = ?;
        """
        # 值：更新字段的值 + 主键的值
        values = tuple(sql_converter(v) for v in update_data.values()) + (config.config_name,)

        try:
            with sqlite3.connect(self.database) as conn:
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
            with sqlite3.connect(self.database) as conn:
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
            with sqlite3.connect(self.database) as conn:
                cursor = conn.execute(query_sql)
                # 提取所有配置名称，转换为列表（fetchall() 返回 [(name1,), (name2,), ...] 格式）
                results = cursor.fetchall()
                config_names = [row[0] for row in results]

            logger.info(f"查询到 {len(config_names)} 个配置名称")
            return config_names
        except sqlite3.Error as e:
            logger.exception(f"查询所有配置名称异常：{e}")
            return []




