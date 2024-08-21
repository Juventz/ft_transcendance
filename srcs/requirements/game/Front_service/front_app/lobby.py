import asyncio
import json
from .gameState import GameState
from .localGame import LocalGame
import logging

logger = logging.getLogger(__name__)

class Lobby:
    def __init__(self, id, admin, is_local):
        self.id = id
        self.admin = admin
        self.players = [admin]
        self.local_players = [admin.pseudo]
        self.is_local = is_local
        self.matches = []
        self.winner = []

    def add_player(self, player):
        self.players.append(player)

    async def send_to_all(self, message, admin_message):
        for player in self.players:
            if player == self.admin:
                await player.send(admin_message)
            else:
                await player.send(message)

    async def send_lobby_menu(self):
        logging.info(f"Sending lobby menu to lobby {self.id}")

        # Début du contenu HTML
        html_content = f"""
                    <div>
                        <h2>Lobby: {"Local" if self.is_local else self.id}</h2>
                        <h3>Players list:</h3>
                        <ul>
                    """

        # Ajouter chaque joueur à la liste
        if (self.is_local):
            for player in self.local_players:
                html_content += f"<li>{player}</li>"
        else:
            for player in self.players:
                html_content += f"<li>{player.pseudo}</li>"

        # Continuer le contenu HTML
        html_content += """
                        </ul>
                    """

        # Ajouter un bouton pour ajouter des joueurs si le jeu est local
        if self.is_local:
            html_content += """
                        <button id="add_player" onClick="handleGameButtonClick('add_player')">Ajouter Joueur</button>
                    """

        # admin message
        html_admin_content = f"""
                    <div>
                        <h2>Lobby: {"Local" if self.is_local else self.id}</h2>
                        <h3>Players list:</h3>
                        <ul>
                    """

        # Ajouter chaque joueur à la liste
        if (self.is_local):
            for player in self.local_players:
                html_admin_content += f"<li>{player}</li>"
                if player != self.admin.pseudo:
                    html_admin_content += f""" <button onClick="handleGameButtonClick('remove_player', '{player}')">Remove player</button>"""
        else:
            for player in self.players:
                html_admin_content += f"<li>{player.pseudo}</li>"
                if player != self.admin:
                    html_admin_content += f""" <button onClick="handleGameButtonClick('remove_player', {player.pseudo})">Remove player</button>"""

        # Continuer le contenu HTML
        html_admin_content += """
                        </ul>
                    """

        # Ajouter un bouton pour ajouter des joueurs si le jeu est local
        if self.is_local:
            html_admin_content += """
                        <button id="add_player" onClick="handleGameButtonClick('add_player')">Ajouter Joueur</button>
                    """

        # Ajouter un bouton pour lancer la partie
        html_admin_content += """
                        <button id="start_game" onClick="handleGameButtonClick('start_game')">Launch game</button>
                    </div>
                """

        await self.send_to_all(
            json.dumps({
            "type": "html",
            "content": html_content,
            }),
            json.dumps({
                "type": "html",
                "content": html_admin_content
            })
        )

    async def start_game(self):
        if self.is_local:
            for i in range(0, len(self.local_players), 2):
                player1 = self.local_players[i]
                player2 = self.local_players[i + 1] if i + 1 < len(self.local_players) else None
                self.matches.append(LocalGame(self, player1, player2))
            await self.matches[0].start_match()
        else:
            # Create a match for each pair of players
            for i in range(0, len(self.players), 2):
                player1 = self.players[i]
                player2 = self.players[i + 1]
                self.matches.append(GameState(player1, player2, False))

            # Start the matches in parallel and wait for them to finish
            await asyncio.gather(*(match.start_match() for match in self.matches))

    def update_paddle_position(self, player_channel_name, key, action):
        if self.is_local:
            logger.info(f"Updating paddle position for player {player_channel_name}")
            self.matches[0].update_paddle_position(key, action)


    async def send_match_end_menu(self, winner):
        html_content = f"""
            <div>
                <h2>Match Score</h2>
                <p>Left Player: {self.matches[0].leftPlayer} - score: {self.matches[0].players['left']['score']}</p>
                <p>Right Player: {self.matches[0].rightPlayer} - score: {self.matches[0].players['right']['score']}</p>
                <p>Winner: {winner}</p>
        """

        if not (len(self.matches) == 1 and len(self.winner) == 0):
            html_content += """
                <button onClick="handleGameButtonClick('start_next_game')">suivant</button>
            """
        else:
            html_content += """<button onClick="handleGameButtonClick('back_to_menu')">Go back to menu</button>"""

        html_content += """</div>"""

        self.winner.append(winner)

        await self.admin.send(
            json.dumps({
                "type": "end_game",
                "content": html_content,
            })
        )

    async def end_game(self):
        if self.is_local:
            self.matches.pop(0)
            if len(self.matches) > 0:
                await self.matches[0].start_match()
            else:
                if len(self.winner) > 1:
                    for i in range(0, len(self.winner), 2):
                        player1 = self.winner[i]
                        player2 = self.winner[i + 1] if i + 1 < len(self.winner) else None
                        self.matches.append(LocalGame(self, player1, player2))
                    self.winner = []
                    await self.matches[0].start_match()
                else:
                    await self.send_end_lobby_menu()


