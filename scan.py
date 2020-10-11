from utils.database import db_connect,db_disconnect
import asyncio
from asyncio import Queue
import logging

from config import config

import utils.telegram_util

from workers.worker_chats import worker_chats
from workers.worker_messages import worker_messages
from workers.worker_link_forwards import worker_links_forwards
from workers.worker_status_updates import worker_log_status
from workers.worker_link_text import worker_links_text

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(name)s | %(levelname)s | %(message)s')


async def main(loop):

    memory = {
        'queues': {
            'queue_chats': Queue(maxsize=0),
            'queue_messages': Queue(maxsize=0),
            'queue_links_forward': Queue(maxsize=0),
            'queue_links_text': Queue(maxsize=0)
        },
        'stats': {
            'parsed_chats': 0,
            'parsed_messages': 0,
            'parsed_links_forward': 0,
            'parsed_links_text': 0
        },
    }

    # Establish the connection pool
    await db_connect()

    # start the telegram client
    memory['tg_util'] = utils.telegram_util.TelegramUtil(memory)
    await memory['tg_util'].start()

    # load the initial chats
    for c in config['start_channels']:
        await memory['tg_util'].get_chat_id(c)

    # start the workers
    status_updater = loop.create_task(worker_log_status(memory))

    chat_scanner = asyncio.ensure_future(worker_chats(memory))
    message_scanners = [asyncio.ensure_future(worker_messages(memory)) for _ in range(10)]
    chat_links_forward_scanner = asyncio.ensure_future(worker_links_forwards(memory))
    chat_links_text_scanner = asyncio.ensure_future(worker_links_text(memory))

    # detect when all workers are done
    while True:
        await memory['queues']['queue_chats'].join()
        await memory['queues']['queue_messages'].join()
        await memory['queues']['queue_links_forward'].join()
        await memory['queues']['queue_links_text'].join()
        if memory['queues']['queue_chats'].empty() and memory['queues']['queue_messages'].empty() and memory['queues']['queue_links_forward'].empty() and memory['queues']['queue_links_text'].empty():
            break
    logging.info("all tasks completed")

    # stop workers
    for worker in [status_updater, chat_scanner, *message_scanners, chat_links_forward_scanner, chat_links_text_scanner]:
        worker.cancel()

    await db_disconnect()

    print("done")


loop = asyncio.get_event_loop()
loop.create_task(main(loop))
loop.run_forever()
loop.close()