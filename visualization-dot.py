from utils.database import db_connect, db_disconnect, get_all_chats, get_all_links_counted
import asyncio
from graphviz import Digraph, Graph

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(name)s | %(levelname)s | %(message)s')

async def main():
    dot = Digraph(comment='the conspiracy bubble')
    #dot = Graph(comment='the conspiracy bubble')
    dot.layout = 'sfdp'
    #dot.engine = 'neato'
    dot.attr('node', shape='box', style='filled')
    await db_connect()

    rows = await get_all_chats()
    rows = [x for x in rows if x[4] > 10000]
    chats = [x[0] for x in rows]
    logging.info(f"adding {len(chats)} chats as nodes")

    for id, c_name, c_username, description, members, scanned in rows:

        if members < 100:
            color = 'grey'
        elif members < 1000:
            color = 'gray76'
        elif members < 10000:
            color = 'yellow'
        else:
            color = 'red'
        dot.node(str(id), f"{c_name}\n@{c_username}\n{members}", color =color)

    rows = await get_all_links_counted()
    logging.info(f"adding {len(rows)} links as edges")
    for source, destination, count in rows:
        if source in chats and destination in chats and source != destination:
            if count > 20:
                dot.edge(str(source), str(destination))

    dot.format = 'svg'
    logging.info('rendering now')
    dot.render('output/test.dot', view=True)
    await db_disconnect()
    logging.info("done")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()