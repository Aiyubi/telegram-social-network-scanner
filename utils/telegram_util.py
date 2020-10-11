from config import config
import logging
import asyncio
import telethon
from telethon import TelegramClient, sync
from telethon.tl.functions.channels import GetFullChannelRequest
from utils.database import insert_new_chat, Chat
import json
import asyncio
from async_lru import alru_cache

MEMORY_LOCATION = 'telegram_chats_memory.json'


class TelegramUtil:

    def __init__(self, main_memory):

        self.tg_memory = {
            'cached_chats_by_id': {},
            'cached_chats_by_username': {},
            'cached_unknown_searches': []
        }

        self.client = TelegramClient(config['telegram']['app_name'],
                                config['telegram']['api_id'],
                                config['telegram']['api_hash'])

        self.queue_chats = main_memory['queues']['queue_chats']

    async def start(self):
        await self.client.start(config['telegram']['phone_id'])
        await self.client.get_dialogs()

    async def get_chat_info(self, search_term):
        entity = await self.client.get_entity(search_term)
        return entity

    def check_cache(self, search):
        if search in self.tg_memory['cached_chats_by_id']:
            return search
        elif search in self.tg_memory['cached_chats_by_username']:
            return self.tg_memory['cached_chats_by_username'][search]
        else:
            return None

    def add_cache(self, id, username):
        self.tg_memory['cached_chats_by_id'][id] = '@' + username
        self.tg_memory['cached_chats_by_username']['@' + username] = id

    def add_cache_invalid(self, search):
        self.tg_memory['cached_unknown_searches'].append(search)

    def is_invalid_search(self, search):
        if search in self.tg_memory['cached_unknown_searches']:
            return None

    @alru_cache(maxsize=None)
    async def get_chat_id(self, search):
        if isinstance(search, str):
            search = search.lower()

        cached = self.check_cache(search)
        if cached:
            return cached

        if self.is_invalid_search(search):
            return None

        logging.info("searching for: " + str(search))

        try:

            while True:
                try:
                    chat_info = await self.get_chat_info(search)
                    break
                except telethon.errors.FloodWaitError as e:
                    sleep_time = int(str(e).split(" ")[3])+30
                    logging.warning(f'Encountered a flood waiting error. Worker will sleep for {sleep_time} seconds')
                    await asyncio.sleep(sleep_time)

            # if a forwarded message gets scanned, it might belong to a chat without username
            if not chat_info.username:
                self.add_cache_invalid(chat_info.id)
                return None

            if type(chat_info) is telethon.types.Channel:
                # case: new chat
                participant_count = await self.client.get_participants(search, limit=0)
                participant_count = participant_count.total

                self.add_cache(chat_info.id, chat_info.username.lower())

                logging.info('new chat found: @' + chat_info.username)

                await insert_new_chat(Chat(
                    id=chat_info.id,
                    name=chat_info.title,
                    username=chat_info.username,
                    chat_member_count=participant_count,
                    is_scanned=False
                ))
                await self.queue_chats.put('@' + chat_info.username)
                return chat_info.id
            else:
                self.add_cache_invalid(chat_info.id)
                self.add_cache_invalid(chat_info.username.lower())
                self.add_cache_invalid(search)
                return None
        except (ValueError, telethon.errors.rpcerrorlist.ChannelPrivateError) as e:
            self.add_cache_invalid(search)
            return None

    async def get_messages_of_chat(self, chat):
        async for msg in self.client.iter_messages(chat):
            yield msg
