from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User


class Users(object):
    """"""

    def __init__(self, id: int, username: str, firstname: str,
                 lastname: str, is_loading: bool, loads: int):
        self.id = id
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.is_loading = is_loading
        self.loads = loads


    async def get_id(self, session: AsyncSession):
        sql = select(User.id).where(
            User.id == self.id
        )
        result = await session.execute(sql)
        return result.scalars().first()


    async def create_user(self, session: AsyncSession):
        user = User(
            id = self.id,
            username = self.username,
            firstname = self.firstname,
            lastname = self.lastname,
            is_loading = self.is_loading,
            loads = self.loads
        )
        session.add(user)


    async def update_user(self, session: AsyncSession):
        sql = update(User).where(
            User.id == self.id
        ).values(
            username = self.username,
            firstname = self.firstname,
            lastname = self.lastname
        )
        await session.execute(sql)


    async def upsert_user(self, session: AsyncSession):
        if await self.get_id(session):
            await self.update_user(session)
        else:
            await self.create_user(session)


    async def increase_loads(self, session: AsyncSession):
        '''
        sql = select(User.loads).where(
            User.id == self.id
        )
        loads = await session.execute(sql)
        loads = loads.scalars().first()
        '''
        sql = update(User).where(
            User.id == self.id
        ).values(
            loads = User.loads + 1
        )
        await session.execute(sql)


    async def change_load_status(self, is_loading: bool, session: AsyncSession):
        sql = update(User).where(
            User.id == self.id
        ).values(
            is_loading = is_loading
        )
        await session.execute(sql)


    async def check_loading(self, session: AsyncSession):
        sql = select(User.is_loading).where(
            User.id == self.id
        )
        result = await session.execute(sql)
        return result.scalars().first()
