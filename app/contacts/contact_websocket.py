import asyncio

import websockets

from app.contacts.handles.h_chat import Handle
from app.utility.base_world import BaseWorld


class WebSocket(BaseWorld):

    def __init__(self, services):
        self.name = 'websocket'
        self.description = 'Accept data through web sockets'
        self.log = self.create_logger('contact_websocket')
        self.handler = Handler(services)

    async def start(self):
        loop = asyncio.get_event_loop()
        web_socket = self.get_config('app.contact.websocket')
        loop.create_task(await websockets.serve(self.handler.handle, '0.0.0.0', web_socket.split(':')[1]))


class Handler:

    def __init__(self, services):
        self.services = services
        self.handles = [
            Handle(tag='chat', services=services)
        ]
        self.log = BaseWorld.create_logger('websocket_handler')
        self.users = set()

    async def handle(self, socket, path):
        self.users.add(socket)
        try:
            for handle in [h for h in self.handles if h.tag == path.split('/')[1]]:
                await handle.run(socket, path, self.users)
        except Exception as e:
            self.log.debug(e)
            self.users.remove(socket)