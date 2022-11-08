from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config


class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME,
        )

    async def execute(
            self,
            command,
            *args,
            fetch: bool = False,
            fetchval: bool = False,
            fetchrow: bool = False,
            execute: bool = False,
    ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        username varchar(255) NULL,
        telegram_id BIGINT NOT NULL UNIQUE
        );
        """
        await self.execute(sql, execute=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join(
            [f"{item} = ${num}" for num, item in enumerate(parameters.keys(), start=1)]
        )
        return sql, tuple(parameters.values())

    async def add_user(self, full_name, username, telegram_id):
        sql = "INSERT INTO main_user (name, username, id) VALUES($1, $2, $3) returning *"
        return await self.execute(sql, full_name, username, telegram_id, fetchrow=True)

    async def select_all_users(self):
        sql = "SELECT * FROM main_user"
        return await self.execute(sql, fetch=True)

    async def view_category(self):
        sql = 'SELECT * FROM main_category'
        return await self.execute(sql, fetch=True)

    async def where_category(self, **kwargs):
        sql = "SELECT * FROM main_category WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def where_product_for_category(self, **kwargs):
        sql = "SELECT * FROM main_product WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def where_product(self, **kwargs):
        sql = "SELECT * FROM main_product WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def add_cart(self, tg_id, name, price, size, count):
        sql = "INSERT INTO main_cart (tg_id,name,price,size,count) VALUES($1, $2, $3, $4, $5) returning *"
        return await self.execute(sql, tg_id, name, price, size, count, fetchrow=True)

    async def delete_cart(self, tg_id):
        sql = "DELETE FROM main_cart WHERE tg_id=$1"
        return await self.execute(sql, tg_id, execute=True)

    async def check_product(self, **kwargs):
        sql = "SELECT * FROM main_cart WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def update_product(self, count, tg_id, name, size):
        sql = "UPDATE main_cart SET count=$1 WHERE tg_id=$2 AND name=$3 AND size=$4"
        return await self.execute(sql, count, tg_id, name, size, execute=True)

    async def delete_product(self, tg_id, id):
        sql = "DELETE FROM main_cart WHERE tg_id=$1 AND id=$2"
        return await self.execute(sql, tg_id, id, execute=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM main_user WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM main_user"
        return await self.execute(sql, fetchval=True)

    async def update_user_username(self, username, telegram_id):
        sql = "UPDATE main_user SET username=$1 WHERE id=$2"
        return await self.execute(sql, username, telegram_id, execute=True)

    async def delete_users(self):
        await self.execute("DELETE FROM main_user WHERE TRUE", execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE main_user", execute=True)
