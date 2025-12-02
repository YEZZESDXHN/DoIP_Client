import base64
from dataclasses import dataclass, asdict
import logging
import sqlite3
from os import PathLike
from typing import Union, Optional, List

DOIP_CONFIG_TABLE_NAME = "DoIP_Config"
CURRENT_CONFIG_TABLE_NAME = 'current_active_config'
DIAG_TREE_TABLE_NAME = "Diag_Tree"
DIAG_PROCESS_TABLE_NAME = "Diag_Process"

DEFAULT_DOIP_CONFIG = {
    'config_name': 'default_config',
    'tester_logical_address': 0x7e2,
    'dut_logical_address': 0x773,
    'dut_ipv4_address': '172.16.104.70',
    'is_routing_activation_use': True,
    'is_oem_specific_use': False,
    'oem_specific': b'\x00\x00\x00\x00',

}

logger = logging.getLogger('UDSOnIPClient.' + __name__)

@dataclass
class DoIPConfig:
    # 主键字段（必填，无默认值）
    config_name: str
    # 必填字段（无默认值，必须传入）
    tester_logical_address: int
    dut_logical_address: int
    dut_ipv4_address: str
    # 可选字段（有默认值，可省略）
    is_routing_activation_use: int = 1
    is_oem_specific_use: int = 0
    oem_specific: int = 0

    def to_db_tuple(self) -> tuple:
        """
        转换为数据库插入/更新所需的元组（顺序与 SQL 字段对应）
        用途：配合 INSERT/UPDATE 语句的 ? 占位符使用
        """
        return (
            self.config_name,
            self.tester_logical_address,
            self.dut_logical_address,
            self.dut_ipv4_address,
            self.is_routing_activation_use,
            self.is_oem_specific_use,
            self.oem_specific
        )

    def to_update_tuple(self) -> tuple:
        """转换为数据库更新所需的元组（不含主键，主键放最后用于 WHERE 条件）"""
        return (
            self.tester_logical_address,
            self.dut_logical_address,
            self.dut_ipv4_address,
            self.is_routing_activation_use,
            self.is_oem_specific_use,
            self.oem_specific,
            self.config_name  # 主键作为查询条件
        )

    def to_dict(self) -> dict:
        """转换为字典（用于 JSON 序列化或日志打印）"""
        return asdict(self)

    def __str__(self) -> str:
        """自定义字符串输出，方便打印查看"""
        return (
            f"DoipConfig(config_name='{self.config_name}', "
            f"tester_logical_address={self.tester_logical_address}, "
            f"dut_logical_address={self.dut_logical_address}, "
            f"dut_ipv4_address='{self.dut_ipv4_address}', "
            f"is_routing_activation_use={'启用' if self.is_routing_activation_use == 1 else '禁用'}, "
            f"is_oem_specific_use={'启用' if self.is_oem_specific_use == 1 else '禁用'}, "
            f"oem_specific={self.oem_specific})"
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

    return obj


class DBManager:
    def __init__(self, database: Union[str, bytes, PathLike[str], PathLike[bytes]]):
        self.database = database  # 数据库路径/名称
        self.init_database()      # 初始化时自动建表

    def init_database(self):
        """初始化数据库：创建 doip_config 表并确保存在默认配置"""
        create_doip_config_sql = f"""
        CREATE TABLE IF NOT EXISTS {DOIP_CONFIG_TABLE_NAME} (
            config_name TEXT PRIMARY KEY,
            tester_logical_address INTEGER NOT NULL,
            dut_logical_address INTEGER NOT NULL,
            dut_ipv4_address TEXT NOT NULL,
            is_routing_activation_use INTEGER DEFAULT 1,
            is_oem_specific_use INTEGER DEFAULT 0,
            oem_specific INTEGER DEFAULT 0
        );
        """

        create_current_config_sql = f"""
                CREATE TABLE IF NOT EXISTS {CURRENT_CONFIG_TABLE_NAME} (
                    key TEXT PRIMARY KEY,
                    active_config_name TEXT NOT NULL
                );
                """

        try:
            # 1. 连接数据库，创建表（如果不存在）
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
            cursor.execute(insert_meta_sql, (DEFAULT_DOIP_CONFIG['config_name'],))
            conn.commit()
            logger.info(f"成功将 '{DEFAULT_DOIP_CONFIG['config_name']}' 设置为当前激活配置。")
        except sqlite3.Error as e:
            logger.exception(f"设置激活配置名称失败: {e}")

    def _insert_default_config(self, conn: sqlite3.Connection):
        """内部方法：将默认配置写入数据库"""

        # 使用 sql_converter 转换默认配置中的值
        converted_config = {}
        for key, value in DEFAULT_DOIP_CONFIG.items():
            converted_config[key] = sql_converter(value)

        # 构建 SQL 插入语句
        keys = ', '.join(converted_config.keys())
        # 使用 ? 占位符防止 SQL 注入
        placeholders = ', '.join(['?'] * len(converted_config))
        insert_sql = f"""
        INSERT INTO {DOIP_CONFIG_TABLE_NAME} ({keys}) 
        VALUES ({placeholders})
        """

        # 准备要插入的值，保持顺序与 keys 一致
        values = tuple(converted_config.values())

        try:
            cursor = conn.cursor()
            cursor.execute(insert_sql, values)
            conn.commit()
            logger.info(f"成功写入默认配置: {DEFAULT_DOIP_CONFIG['config_name']}")
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
        新增 DOIP 配置
        :param config: DoIPConfig 数据类对象
        :return: 新增成功返回 True，失败返回 False
        """
        insert_sql = f"""
        INSERT INTO {DOIP_CONFIG_TABLE_NAME} 
        (config_name, tester_logical_address, dut_logical_address, dut_ipv4_address, 
         is_routing_activation_use, is_oem_specific_use, oem_specific)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        try:
            with sqlite3.connect(self.database) as conn:
                conn.execute(insert_sql, config.to_db_tuple())
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
        查询指定名称的 DOIP 配置
        :param config_name: 配置名称（主键）
        :return: 成功返回 DoIPConfig 对象，失败返回 None
        """
        query_sql = f"SELECT * FROM {DOIP_CONFIG_TABLE_NAME} WHERE config_name = ?;"
        try:
            with sqlite3.connect(self.database) as conn:
                # 设置 row_factory 为 None（默认返回元组），也可改为自定义字典格式
                cursor = conn.execute(query_sql, (config_name,))
                result = cursor.fetchone()  # 获取单条结果

            if result:
                logger.info(f"查询到配置：{config_name}")
                return DoIPConfig(
                    config_name=result[0],
                    tester_logical_address=result[1],
                    dut_logical_address=result[2],
                    dut_ipv4_address=result[3],
                    is_routing_activation_use=result[4],
                    is_oem_specific_use=result[5],
                    oem_specific=result[6]
                )
            else:
                logger.warning(f"未找到配置：{config_name}")
                return None
        except sqlite3.Error as e:
            logger.exception(f"查询配置异常：{config_name} - {e}")
            return None

    def query_all_doip_configs(self) -> List[DoIPConfig]:
        """
        查询所有 DOIP 配置
        :return: 配置列表（为空则返回空列表）
        """
        query_sql = f"SELECT * FROM {DOIP_CONFIG_TABLE_NAME} ORDER BY config_name ASC;"
        try:
            with sqlite3.connect(self.database) as conn:
                cursor = conn.execute(query_sql)
                results = cursor.fetchall()  # 获取所有结果

            config_list = [
                DoIPConfig(
                    config_name=row[0],
                    tester_logical_address=row[1],
                    dut_logical_address=row[2],
                    dut_ipv4_address=row[3],
                    is_routing_activation_use=row[4],
                    is_oem_specific_use=row[5],
                    oem_specific=row[6]
                ) for row in results
            ]
            logger.info(f"查询到 {len(config_list)} 条配置")
            return config_list
        except sqlite3.Error as e:
            logger.exception(f"查询所有配置异常：{e}")
            return []

    def update_doip_config(self, config: DoIPConfig) -> bool:
        """
        更新 DOIP 配置（根据 config_name 主键更新所有字段）
        :param config: 包含最新数据的 DoIPConfig 对象
        :return: 更新成功返回 True，失败返回 False
        """
        update_sql = f"""
        UPDATE {DOIP_CONFIG_TABLE_NAME}
        SET tester_logical_address = ?,
            dut_logical_address = ?,
            dut_ipv4_address = ?,
            is_routing_activation_use = ?,
            is_oem_specific_use = ?,
            oem_specific = ?
        WHERE config_name = ?;  -- 主键作为更新条件，确保精准更新
        """
        try:
            with sqlite3.connect(self.database) as conn:
                cursor = conn.execute(update_sql, config.to_update_tuple())
                # rowcount：受影响的行数（0 表示未找到配置，1 表示更新成功）
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




