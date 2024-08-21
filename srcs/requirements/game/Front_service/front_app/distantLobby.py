import asyncio
import json

import requests
from .distantGame import DistantGame
import logging

logger = logging.getLogger(__name__)

class DistantLobby:
    def __init__(self, id, admin, remove_lobby):
        self.id = id
        self.admin = admin
        self.players = [admin]
        self.matches = []
        self.ended_matches = []
        self.winner = []
        self.is_started = False
        self.remove_lobby = remove_lobby


    async def send_to_all(self, message, admin_message):
        for player in self.players:
            if player == self.admin:
                await player.send(admin_message)
            else:
                await player.send(message)


    async def send_lobby_menu(self, error_message):
        # Début du contenu HTML avec Bootstrap
        html_content = f"""
                <div class="container" style="margin-top: 100px;">
                    <div class="row-mt-5 justify-content-center col-xs-12 col-sm-12 col-md-12 col-lg-12 text-center">
                        <div class="col sweet-title-straight mt-1 mb-5">
                            <span>Lobby : {self.id}</span>
                        </div>
                        <div class="col sweet-title-straight mt-1 mb-3">
                            <span>Players list</span>
                        </div>
                        <ul class="list-group">
                    """

        html_admin_content = html_content

        # Ajouter chaque joueur à la liste avec Bootstrap
        for player in self.players:
            player_item = f"<li class='list-group-item d-flex justify-content-between align-items-center'>{player.pseudo}"
            if player != self.admin:
                player_item += f"<button class='btn btn-danger btn-sm' onClick=\"handleGameButtonClick('remove_player', '{player.pseudo}')\">Remove</button>"
            player_item += "</li>"
            html_content += player_item
            html_admin_content += player_item

        # Continuer le contenu HTML
        html_content += """
                        </ul>
                    </div>
                """
        html_admin_content += """
                        </ul>
                    </div>
                """

        # Ajouter un bouton pour lancer la partie avec Bootstrap
        html_admin_content += f"""
                    <div class="text-center mt-3">
                        <button id="start_game" class="btn btn-secondary btn-lg" style="background-color: black" onClick="handleGameButtonClick('start_game')">Launch game</button>
                        <p>{error_message}</p>
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


    async def join_lobby(self, player):
        if self.is_started:
            # send an error message to the user
            # TO DO
            return
        # if len(self.players) >= 4:
            # send an error message to the user
            # TO DO
        if len(self.players) < 4:
            player.lobby_id = self.id
            self.players.append(player)
            await self.send_lobby_menu("")


    async def remove_player(self, player_pseudo):
        if self.is_started:
            # send an error message to the user
            # TO DO
            return
        if player_pseudo == self.admin.pseudo:
            for player in self.players:
                if player != self.admin:
                    await player.send_main_menu()
                    player.lobby_id = None
            self.remove_lobby(self.id)
            return
        for player in self.players:
            if player.pseudo == player_pseudo:
                # add an error message like you have been kicked
                # TO DO
                self.players.remove(player)
                await self.send_lobby_menu("")
                await player.send_lobby_config()
                break


    async def start_game(self):
        if len(self.players) % 2 == 1:
            await self.send_lobby_menu("The number of players must be even!")
        else:
            self.is_started = True
            #Créer les différents matchs
            for i in range(0, len(self.players), 2):
                player1 = self.players[i]
                player2 = self.players[i + 1]
                logger.info(f"Match créé entre {player1.pseudo} et {player2.pseudo}")  # Ajoutez des logs pour le débogage
                self.matches.append(DistantGame(self, player1, player2))
            # Start the matches in parallel and wait for them to finish
            await asyncio.gather(*(match.send_accept_match_menu() for match in self.matches))


    async def accept_match(self, player):
        for match in self.matches:
            if match.leftPlayer == player or match.rightPlayer == player:
                await match.accept_match(player.channel_name)
                break


    # Called by players by pressing keys
    def update_paddle_position(self, player_channel_name, key, isDown):
        for match in self.matches:
            if match.leftPlayer.channel_name == player_channel_name:
                match.update_paddle_position(key, "left", isDown)
                break
            elif match.rightPlayer.channel_name == player_channel_name:
                match.update_paddle_position(key, "right", isDown)
                break



    async def check_matches_state(self, finished_match):
        self.winner.append(finished_match.winner)
        self.ended_matches.append(finished_match)
        for match in self.matches:
            if not match.winner:
                logger.info(f"Match not finished")
                # if this isn't the last match so we make the winner wait for the others
                await finished_match.send_match_end_menu(False)
                return
        # if all matches of the round are finished check results
        if len(self.matches) == 1:
            logger.info("last match")
            logger.info(f"Test: {finished_match.players['left']['score']}")
            # send the tournament result to the user management service
            jsonMessage = {
                'tournament_winner': finished_match.winner.id,
                'tournament_players': [player.id for player in self.players],
                'matches': [
                    {
                        'winner': match.winner.id,
                        'winner_score': max(match.players['left']['score'], match.players['right']['score']),
                        'loser': match.loser.id,
                        'loser_score': min(match.players['left']['score'], match.players['right']['score']),
                    } for match in self.ended_matches
                ],
            }
            response = requests.post("http://auth:8001/local/gameResult", json=jsonMessage)  
            logger.error(response)
            # if this is the last match show a back to main menu button to winner
            await finished_match.send_match_end_menu(True)

            # remove lobby from the list of lobbies of the players
            for player in self.players:
                player.lobby_id = None

            # remove the lobby from the list of lobbies
            self.remove_lobby(self.id)

        else:
            await finished_match.send_match_end_menu(False)
            logger.info("next match")
            self.matches = []
            #Créer les différents matchs
            for i in range(0, len(self.winner), 2):
                player1 = self.winner[i]
                player2 = self.winner[i + 1]
                logger.info(f"Match créé entre {player1.pseudo} et {player2.pseudo}")  # Ajoutez des logs pour le débogage
                self.matches.append(DistantGame(self, player1, player2))
            self.winner = []
            # Start the matches in parallel and wait for them to finish
            await asyncio.gather(*(match.send_accept_match_menu() for match in self.matches))


    async def remove_player_in_game(self, player):
        if not self.is_started:
            await self.remove_player(player.pseudo)
            return
        for match in self.matches:
            if match.leftPlayer.channel_name == player.channel_name:
                match.winner = match.rightPlayer
                match.loser = match.leftPlayer
                await self.check_matches_state(match)
                break
            if match.rightPlayer.channel_name == player.channel_name:
                match.winner = match.leftPlayer
                match.loser = match.rightPlayer
                await self.check_matches_state(match)
                break




