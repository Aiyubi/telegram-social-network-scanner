import logging
import asyncio

STATUS_DELAY = 10


async def worker_log_status(memory):
    while True:
        logging.info(f"Chats     \t| processed: {memory['stats']['parsed_chats']} \t| queue: {memory['queues']['queue_chats'].qsize()}")
        logging.info(f"Messages  \t| processed: {memory['stats']['parsed_messages']} \t| queue: {memory['queues']['queue_messages'].qsize()}")
        logging.info(f"Forwards  \t| processed: {memory['stats']['parsed_links_forward']} \t| queue: {memory['queues']['queue_links_forward'].qsize()}")
        logging.info(f"Text links\t| processed: {memory['stats']['parsed_links_text']} \t| queue: {memory['queues']['queue_links_text'].qsize()}")

        await asyncio.sleep(STATUS_DELAY)
