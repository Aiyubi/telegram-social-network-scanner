from utils.database import db_connect, db_disconnect, get_all_chats, get_all_links_counted
import asyncio
from graphviz import Digraph, Graph


async def main():
    dot = Digraph(comment='the conspiracy bubble')
    ädot = Graph(comment='the conspiracy bubble')
    #dot.engine = 'neato'
    dot.attr('node', shape='box', style='filled')
    await db_connect()

    rows = await get_all_chats()
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
        pass

    rows = await get_all_links_counted()
    for source, destination, count in rows:
        dot.edge(str(source), str(destination))

    dot.format = 'svg'
    dot.render('test.dot', view=True)
    await db_disconnect()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()