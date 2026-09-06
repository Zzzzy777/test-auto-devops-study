# -*- coding:utf-8 -*-
"""
数据库操作工具类
用途：UI页面操作完成后，查询mysql，做数据库层数据一致性校验
"""
import pymysql
# 导入配置文件的数据库参数
from common.config import MYSQL_CFG


class DbHelper:
    def __init__(self):
        """初始化：建立mysql数据库连接"""
        # 使用配置里面的参数创建数据库连接
        self.conn = pymysql.connect(
            host=MYSQL_CFG["host"],
            port=MYSQL_CFG["port"],
            user=MYSQL_CFG["user"],
            password=MYSQL_CFG["password"],
            database=MYSQL_CFG["database"],
            charset=MYSQL_CFG["charset"]
        )
        # 创建游标，DictCursor：查询结果以字典返回，方便取值
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)

    def query_user_by_username(self, username):
        """
        根据用户名查询sys_user用户表
        :param username: 待查询的用户名
        :return: dict 查到的用户数据；查不到返回None
        """
        # sql语句，%s是占位符，防止sql注入
        sql = "select * from sys_user where username=%s"
        # 执行sql，传入参数元组
        self.cursor.execute(sql, (username,))
        # fetchone 获取单条查询结果
        return self.cursor.fetchone()

    def close(self):
        """关闭游标、关闭数据库连接，释放资源"""
        self.cursor.close()
        self.conn.close()
