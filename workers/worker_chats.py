from utils.database import mark_chat_scanned
import logging


async def worker_chats(memory):
    input_queue = memory['queues']['queue_chats']
    output_queue = memory['queues']['queue_messages']
    tg_util = memory['tg_util']

    while True:
        next_job = await input_queue.get()
        await scan_chat(next_job, output_queue, tg_util)
        input_queue.task_done()
        memory['stats']['parsed_chats'] += 1


async def scan_chat(channel_username, output_queue, tg_util):
    logging.info(f'beginning to scan chat: {channel_username}')
    chat_id = await tg_util.get_chat_id(channel_username)
    async for msg in tg_util.get_messages_of_chat(channel_username):
        await output_queue.put(msg)
    await mark_chat_scanned(chat_id)
