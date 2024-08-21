import asyncio
import json
from .gameState import GameState
from .localGame import LocalGame
import logging

logger = logging.getLogger(__name__)

class LocalLobby:
    def __init__(self, id, admin):
        self.id = id
        self.admin = admin
        self.players = [admin.pseudo]
        self.matches = []
        self.winner = []

    # Called every time we are not in a game
    async def send_lobby_menu(self, error_message):
        # Start of HTML content with Bootstrap container
        html_content = """
            <div class="container" style="margin-top: 100px;">
                <div class="row-mt-5 justify-content-center col-xs-12 col-sm-12 col-md-12 col-lg-12 text-center">
                    <div class="col sweet-title-straight mt-1 mb-5">
                        <span>Lobby ===> local</span>
                    </div>
                    <div class="col sweet-title-straight mt-1 mb-5">
                        <span>Players list</span>
                    </div>
                <ul class="list-group">
        """

        # Add each player to the list with Bootstrap styling
        for player in self.players:
            html_content += f'<li class="list-group-item d-flex justify-content-between align-items-center">{player}'
            if player != self.admin.pseudo:
                html_content += f""" <button class="btn btn-danger btn-sm" onClick="handleGameButtonClick('remove_player', '{player}')">Remove player</button>"""
            html_content += "</li>"

        # Continue HTML content with Bootstrap buttons
        html_content += f"""
                </ul>
                <div class="mt-3">
                    <button id="add_player" class="btn btn-secondary btn-lg" style="background-color: black"  onClick="handleGameButtonClick('add_player')">Add player</button>
                    <button id="start_game" class="btn btn-secondary btn-lg" style="background-color: black"  onClick="handleGameButtonClick('start_game')">Launch game</button>
                </div>
                <p class="mt-3">{error_message}</p>
            </div>
        """

        await self.admin.send(
            json.dumps({
            "type": "html",
            "content": html_content,
            }),
        )


    # Called by admin with the add_player button
    async def add_player(self):
        if len(self.players) >= 4:
            await self.send_lobby_menu("4 players is the max allowed")
        else:
            self.players.append(f"Joueur {len(self.players)+ 1}")
            await self.send_lobby_menu("")


    # Called by admin with the remove_player button
    async def remove_player(self, player):
        self.players.remove(player)
        await self.send_lobby_menu("")


    # Called by admin with the start_game button
    async def start_game(self):
        if len(self.players) % 2 == 1:
            await self.send_lobby_menu("The number of players must be even!")
        else:
            #Créer les différents matchs
            for i in range(0, len(self.players), 2):
                player1 = self.players[i]
                player2 = self.players[i + 1] if i + 1 < len(self.players) else None
                self.matches.append(LocalGame(self, player1, player2))
            await self.matches[0].start_match()


    # Called by players by pressing keys
    def update_paddle_position(self, admin_channel_name, key, isDown):
        if self.matches:
            self.matches[0].update_paddle_position(key, isDown)


    # Called by the played match when is over
    async def send_match_end_menu(self, winner):
        html_content = f"""
            <div class="container mt-3">
                <h2 class="text-center">Match Score</h2>
                <p class="text-center">Left Player: {self.matches[0].leftPlayer} - score: {self.matches[0].players['left']['score']}</p>
                <p class="text-center">Right Player: {self.matches[0].rightPlayer} - score: {self.matches[0].players['right']['score']}</p>
                <p class="text-center font-weight-bold">Winner: {winner}</p>
        """

        # Remove match from list and add winner to
        self.matches.pop(0)
        self.winner.append(winner)

        # if there is no more matches add a back to menu button
        if len(self.matches) == 0 and len(self.winner) == 1:
            html_content += """<div class="text-center mt-3"><button class="btn btn-primary" onClick="handleGameButtonClick('back_to_main_menu')">Go back to menu</button></div>"""
        else:
            # if there is no more matches in the round start a new one
            if len(self.matches) == 0:
                for i in range(0, len(self.winner), 2):
                    player1 = self.winner[i]
                    player2 = self.winner[i + 1] if i + 1 < len(self.winner) else None
                    self.matches.append(LocalGame(self, player1, player2))
                self.winner = []
            html_content += f"""
                <h2 class="text-center mt-4">Next game</h2>
                <p class="text-center">Left Player: {self.matches[0].leftPlayer}</p>
                <p class="text-center">Right Player: {self.matches[0].rightPlayer}</p>
                <div class="text-center mt-3"><button class="btn btn-success" onClick="handleGameButtonClick('start_next_match')">Launch game</button></div>
            """

        html_content += """</div>"""

        await self.admin.send(
            json.dumps({
                "type": "end_game",
                "content": html_content,
            })
        )


    # Called by the admin with the start_next_match button
    async def start_next_match(self):
        await self.matches[0].start_match()
