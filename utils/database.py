from pydantic import BaseModel
import sqlalchemy
from sqlalchemy import select
import databases
import logging
from config import  config
metadata = sqlalchemy.MetaData()

DATABASE_URL = config['database']
database = databases.Database(DATABASE_URL)

chats = sqlalchemy.Table(
    "chats", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("username", sqlalchemy.String),
    sqlalchemy.Column("description", sqlalchemy.String),
    sqlalchemy.Column("chat_member_count", sqlalchemy.Integer),
    sqlalchemy.Column("is_scanned", sqlalchemy.Boolean),
)

chat_links = sqlalchemy.Table(
    "links", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("origin_chat_id", sqlalchemy.Integer),
    sqlalchemy.Column("origin_message_id", sqlalchemy.Integer),
    sqlalchemy.Column("target_chat_id", sqlalchemy.Integer)
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)


class Chat(BaseModel):
    id: int
    name: str
    username:str
    chat_member_count: int
    is_scanned: bool


class LinkIn(BaseModel):
    origin_chat_id: int
    origin_message_id: int
    target_chat_id: int


class Link(BaseModel):
    id: int
    origin_chat_id: int
    origin_message_id: int
    target_chat_id: int


async def insert_new_chat(chatin: Chat):
    query = chats.insert().values(
        id = chatin.id,
        name=chatin.name,
        username=chatin.username,
        is_scanned=chatin.is_scanned,
        chat_member_count=chatin.chat_member_count
    )

    await database.execute(query)
    return chatin


async def insert_chat_link(linkin: LinkIn):
    query = chat_links.insert().values(
        origin_chat_id=linkin.origin_chat_id,
        origin_message_id=linkin.origin_message_id,
        target_chat_id=linkin.target_chat_id
    )

    attempts = 10

    while attempts > 0:
        last_record_id = await database.execute(query)
        return {**linkin.dict(), "id": last_record_id}

    logging.error(f"Couldnt insert chat link into database {linkin.origin_chat_id} | {linkin.origin_message_id} | {linkin.target_chat_id}")
    return None


async def db_connect():
    await database.connect()


async def db_disconnect():
    await database.disconnect()


async def mark_chat_scanned(id):
    query = chats.update().where(chats.c.id == id).values(is_scanned=True)
    await database.execute(query)


async def get_all_chats():
    query = chats.select()
    rows = await database.fetch_all(query=query)
    return rows


async def get_all_links_counted():
    query = select([chat_links.c.origin_chat_id,chat_links.c.target_chat_id,sqlalchemy.func.count()])\
        .group_by(chat_links.c.origin_chat_id,chat_links.c.target_chat_id)
    rows = await database.fetch_all(query=query)
    return rows