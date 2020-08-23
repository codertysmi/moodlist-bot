import asyncio
import websockets

import json

class WsServer:
    def __init__(self, app):
        self.app = app
        self.loop = app.loop

        self.endpoints = {}

        self.status = "DORMANT"
    
    def route(self, func):
        self.endpoints[func.__name__] = func
    
    async def serve(self, ws, path):
        data = await ws.recv()
        parsed = json.loads(data)

        if parsed.get("endpoint"):
            endpoint = parsed.get("endpoint")

            if endpoint not in self.endpoints.keys():
                return await ws.send(json.dumps({"error": "Endpoint doesn't exist.", "status": 404}))
            
            result = await self.endpoints[endpoint](parsed["data"])

            return await ws.send(json.dumps(result))

    def start(self):
        if not self.loop:
            self.loop = asyncio.new_event_loop()
        
        print("Running WS Server")
        self.status = "RUNNING"
        self.loop.run_until_complete(websockets.serve(self.serve, "localhost", 8765))
        self.app.run(loop=self.loop, debug=False, use_reloader=True)