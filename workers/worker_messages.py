import logging
from utils.text_utils import clean_entity_url, clean_entity_text
import telethon


async def worker_messages(memory):
    input_queue = memory['queues']['queue_messages']
    text_links_queue = memory['queues']['queue_links_text']
    forwards_queue = memory['queues']['queue_links_forward']
    while True:
        msg = await input_queue.get()
        await process_message(msg, text_links_queue, forwards_queue)
        input_queue.task_done()
        memory['stats']['parsed_messages'] += 1


async def process_message(msg, text_links_queue, forwards_queue):
    origin_id = msg.to_id.channel_id
    message_id = msg.id

    if msg and msg.entities:
        entities = msg.get_entities_text()
        for entity_type,entity_text in entities:
            search_term = None

            if type(entity_type) is telethon.types.MessageEntityMention:
                search_term = clean_entity_text(entity_text)
            elif type(entity_type) is telethon.types.MessageEntityUrl:
                search_term = clean_entity_url(entity_text)
            elif type(entity_type) is telethon.types.MessageEntityTextUrl:
                search_term = clean_entity_url(entity_text)

            if search_term:
                search_term = search_term.lower()
                await text_links_queue.put((origin_id, message_id, search_term))
    if msg and msg.forward and msg.forward.chat:
        await forwards_queue.put((origin_id, message_id, msg.forward.chat.id))
