from dataclasses import dataclass, asdict
import logging
import sqlite3
from os import PathLike
from typing import Union, Optional, List

DOIP_CONFIG_TABLE_NAME = "DoIP_Config"

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


class DBManager:
    def __init__(self, database: Union[str, bytes, PathLike[str], PathLike[bytes]]):
        self.database = database  # 数据库路径/名称
        self.init_database()      # 初始化时自动建表

    def init_database(self):
        """初始化数据库：创建 doip_config 表（不存在则创建）"""
        # 修复建表 SQL 末尾多余的逗号（避免语法错误）
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {DOIP_CONFIG_TABLE_NAME} (
            config_name TEXT PRIMARY KEY,
            tester_logical_address INTEGER NOT NULL,
            dut_logical_address INTEGER NOT NULL,
            dut_ipv4_address TEXT NOT NULL,
            is_routing_activation_use INTEGER DEFAULT 1,
            is_oem_specific_use INTEGER DEFAULT 0,
            oem_specific INTEGER DEFAULT 0  -- 移除末尾多余的逗号
        );
        """
        try:
            # 使用上下文管理器（with）自动关闭连接，无需手动 close()
            with sqlite3.connect(self.database) as conn:
                cursor = conn.cursor()
                cursor.execute(create_table_sql)
                conn.commit()
            logger.info(f"数据库初始化完成！{DOIP_CONFIG_TABLE_NAME} 表创建/验证成功")
        except sqlite3.Error as e:
            logger.exception(f"初始化数据库失败：{e}")

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

