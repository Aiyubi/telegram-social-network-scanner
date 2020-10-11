import logging
from utils.database import insert_chat_link, LinkIn


async def worker_links_text(memory):
    blocking_queue = memory['queues']['queue_chats']
    input_queue = memory['queues']['queue_links_text']
    tg_util = memory['tg_util']
    while True:
        # only work if the chats queue is empty
        await blocking_queue.join()

        origin_id, message_id, search_term = await input_queue.get()
        await process_chat_link(origin_id, message_id, search_term, tg_util)
        input_queue.task_done()
        memory['stats']['parsed_links_text'] += 1


async def process_chat_link(origin_id, message_id, search_term, tg_util):
    target_id = await tg_util.get_chat_id(search_term)

    if target_id:
        await insert_chat_link(LinkIn(
            origin_chat_id=origin_id,
            origin_message_id =message_id,
            target_chat_id=target_id
        ))