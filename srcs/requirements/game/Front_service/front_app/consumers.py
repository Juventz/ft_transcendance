import asyncio

import requests
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .gameState import GameState
from .lobby import Lobby
from .localLobby import LocalLobby
from .distantLobby import DistantLobby
from .connectedUser import ConnectedUser
import logging
import uuid

logger = logging.getLogger(__name__)

class PongConsumer(AsyncWebsocketConsumer):
    connected_users = {}
    lobbys = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def connect(self):
        await self.accept()
        self.connected_users[self.channel_name] = ConnectedUser(self.channel_name, self.send)

    async def disconnect(self, close_code):
        logger.info(f"Disconnected {self.channel_name}")
        if self.connected_users[self.channel_name].lobby_id:
            logger.info(f"Removing player from lobby {self.connected_users[self.channel_name].lobby_id}")
            await self.lobbys[self.connected_users[self.channel_name].lobby_id].remove_player_in_game(self.connected_users[self.channel_name])
        del self.connected_users[self.channel_name]

    async def receive(self, text_data):
        if text_data:
            try:
                text_data_json = json.loads(text_data)
                type = text_data_json.get("type")

                if type == "auth":
                    # Fetch the user from the user management service
                    user = requests.get(f"http://auth:8001/auth/userInfos", 
                        headers={
                            "Authorization": f"Bearer {text_data_json.get('token')}"
                        }).json()
                    if (user):
                        self.connected_users[self.channel_name].pseudo = user.get("username")
                        self.connected_users[self.channel_name].id = user.get("id")
                        await self.connected_users[self.channel_name].send_main_menu()
                if type == "button_click":
                    await self.handle_button_click(text_data_json)
                if type == "paddle_position":
                    if text_data_json.get("key") is not None and text_data_json.get("isDown") is not None and self.connected_users[self.channel_name].lobby_id is not None and self.connected_users[self.channel_name].lobby_id in self.lobbys:
                        # Update the game state with the new paddle position
                        self.lobbys[self.connected_users[self.channel_name].lobby_id].update_paddle_position(self.channel_name, text_data_json.get("key"), text_data_json.get("isDown"))
            except json.JSONDecodeError:
                logger.info(f"Received invalid JSON: {text_data}")
        else:
            logger.info("Received empty message")


    async def handle_button_click(self, data):
        button = data.get("button")
        if button == "Local":
            # generate new id for lobby
            self.connected_users[self.channel_name].lobby_id = str(uuid.uuid4())
            # create lobby with this user as admin
            self.lobbys[self.connected_users[self.channel_name].lobby_id] = LocalLobby(
                self.connected_users[self.channel_name].lobby_id,
                self.connected_users[self.channel_name],
            )
            # send lobby menu to user
            await self.lobbys[self.connected_users[self.channel_name].lobby_id].send_lobby_menu("")
        if button == "Distant":
            await self.connected_users[self.channel_name].send_lobby_config()
        elif button == "create_lobby":
            # generate new id for lobby
            self.connected_users[self.channel_name].lobby_id = str(uuid.uuid4())
            # create lobby with this user as admin
            self.lobbys[self.connected_users[self.channel_name].lobby_id] = DistantLobby(
                self.connected_users[self.channel_name].lobby_id, 
                self.connected_users[self.channel_name],
                self.remove_lobby, 
            )
            # send lobby menu to user
            await self.lobbys[self.connected_users[self.channel_name].lobby_id].send_lobby_menu("")
        elif button == "join_lobby":
            lobby_id = data.get("body")
            if lobby_id and lobby_id in self.lobbys:
                await self.lobbys[lobby_id].join_lobby(self.connected_users[self.channel_name])
        elif button == 'add_player':
            await self.lobbys[self.connected_users[self.channel_name].lobby_id].add_player()
        elif button == 'remove_player':
            player_pseudo = data.get("body")
            await self.lobbys[self.connected_users[self.channel_name].lobby_id].remove_player(player_pseudo)
        elif button == 'start_game':
            await self.lobbys[self.connected_users[self.channel_name].lobby_id].start_game()
        elif button == 'start_next_match':
            await self.lobbys[self.connected_users[self.channel_name].lobby_id].start_next_match()
        elif button == 'back_to_main_menu':
            await self.connected_users[self.channel_name].send_main_menu()
        elif button == 'accept_match':
            await self.lobbys[self.connected_users[self.channel_name].lobby_id].accept_match(self.connected_users[self.channel_name])

    async def remove_lobby(self, lobby_id):
        if lobby_id in self.lobbys:
            del self.lobbys[lobby_id]
            logger.info(f"Removed lobby {lobby_id}")
