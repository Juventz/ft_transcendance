import asyncio
import json
import random
import logging

logger = logging.getLogger(__name__)

class DistantGame:
    def __init__(self, lobby, leftPlayer, rightPlayer):
        self.config = {
            'canvas': {
                'width': 800,
                'height': 400,
                'color': '#0F0F0F'
            },
            'paddle': {
                'width': 10,
                'height': 100,
            },
        }
        self.players = {
            'left': {
                'x': 0,
                'y': self.config['canvas']['height'] / 2 - self.config['paddle']['height'] / 2,
                'width': self.config['paddle']['width'],
                'height': self.config['paddle']['height'],
                'color': '#007BFF',
                'dy': 0,
                'score': 0
            },
            'right': {
                'x': self.config['canvas']['width'] - self.config['paddle']['width'],
                'y': self.config['canvas']['height'] / 2 - self.config['paddle']['height'] / 2,
                'width': self.config['paddle']['width'],
                'height': self.config['paddle']['height'],
                'color': '#FF4500',
                'dy': 0,
                'score': 0
            }
        }
        self.ball = {
            'x': self.config['canvas']['width'] / 2,
            'y': self.config['canvas']['height'] / 2,
            'radius': 10,
            'speed': 1,
            'dx': 4,
            'dy': 4,
            'color': '#FFFFFF'
        }
        self.lobby = lobby
        self.leftPlayer = leftPlayer
        self.rightPlayer = rightPlayer
        self.left_accepted = False
        self.right_accepted = False
        self.winner = None
        self.loser = None


    async def send_message_to_players(self, message):
        await self.leftPlayer.send(message)
        await self.rightPlayer.send(message)

    import random

    def update(self):
        # Update positions of the paddles
        for player in self.players.values():
            player['y'] += player['dy']
            if player['y'] <= 0:
                player['y'] = 0
            elif player['y'] >= self.config['canvas']['height'] - player['height']:
                player['y'] = self.config['canvas']['height'] - player['height']

        # Existing ball update logic
        self.ball['x'] += self.ball['dx'] * self.ball['speed']
        self.ball['y'] += self.ball['dy'] * self.ball['speed']

        # Check for paddle collision
        for side, player in self.players.items():
            if (
                self.ball['x'] + self.ball['radius'] >= player['x']
                and self.ball['x'] - self.ball['radius'] <= player['x'] + player['width']
                and self.ball['y'] + self.ball['radius'] >= player['y']
                and self.ball['y'] - self.ball['radius'] <= player['y'] + player['height']
            ):
                # Reverse the horizontal direction
                self.ball['dx'] *= -1
                # Increase ball speed
                self.ball['speed'] += 0.1

                # Calculate the relative position of the ball on the paddle
                relative_intersect_y = (player['y'] + (player['height'] / 2)) - self.ball['y']
                normalized_relative_intersect_y = relative_intersect_y / (player['height'] / 2)

                # Adjust the vertical direction based on where the ball hit the paddle
                self.ball['dy'] = normalized_relative_intersect_y * 4  # You can adjust the multiplier as needed

                # Add a slight random variation to the vertical direction
                self.ball['dy'] += random.uniform(-1, 1)

                # Move the ball slightly away from the paddle to prevent sticking
                if side == 'left':
                    self.ball['x'] = player['x'] + player['width'] + self.ball['radius']
                else:
                    self.ball['x'] = player['x'] - self.ball['radius']


        # Check if the ball hit the top or bottom of the screen
        if self.ball['y'] - self.ball['radius'] <= 0:
            self.ball['dy'] = abs(self.ball['dy'])  # Ensure the ball bounces downwards
            self.ball['y'] = self.ball['radius']  # Move the ball slightly away from the top
        elif self.ball['y'] + self.ball['radius'] >= self.config['canvas']['height']:
            self.ball['dy'] = -abs(self.ball['dy'])  # Ensure the ball bounces upwards
            self.ball['y'] = self.config['canvas']['height'] - self.ball['radius']  # Move the ball slightly away from the bottom

        # Check if a player scored
        if self.ball['x'] + self.ball['radius'] <= 0:
            self.players['right']['score'] += 1
            self.ball['dx'] = abs(self.ball['dx'])  # Ensure the ball continues to move to the right
            self.ball['x'] = -self.ball['radius'] - 1  # Move the ball slightly off screen
        elif self.ball['x'] - self.ball['radius'] >= self.config['canvas']['width']:
            self.players['left']['score'] += 1
            self.ball['dx'] = -abs(self.ball['dx'])  # Ensure the ball continues to move to the left
            self.ball['x'] = self.config['canvas']['width'] + self.ball['radius'] + 1  # Move the ball slightly off screen

        # Check if the ball is completely off screen to reset
        if self.ball['x'] < -self.ball['radius'] or self.ball['x'] > self.config['canvas']['width'] + self.ball['radius']:
            self.reset_ball()

    def reset_ball(self):
        # Reset the position of the ball to the center of the screen
        self.ball['x'] = self.config['canvas']['width'] / 2
        self.ball['y'] = self.config['canvas']['height'] / 2
        self.ball['dx'] = 4 if self.ball['dx'] < 0 else -4  # Ensure the ball moves in the opposite direction
        self.ball['dy'] = random.choice([-4, 4])  # Start with a slight vertical direction
        self.ball['speed'] = 1  # Reset speed
        self.players['left']['y'] = self.config['canvas']['height'] / 2 - self.config['paddle']['height'] / 2
        self.players['right']['y'] = self.config['canvas']['height'] / 2 - self.config['paddle']['height'] / 2

    def update_paddle_position(self, key, player_side, isDown):
        player = self.players[player_side]

        if isDown:  # Key is pressed
            if key == 'ArrowUp':
                player['dy'] += -4
            elif key == 'ArrowDown':
                player['dy'] += 4
        else:  # Key is released
            player['dy'] = 0

    # Create a new task to send the game state to all players every 50ms
    async def send_game_state(self):
        while True:
            self.update()
            if self.players['left']['score'] >= 11:
                self.winner = self.leftPlayer
                self.loser = self.rightPlayer
                await self.lobby.check_matches_state(self)
                break
            elif self.players['right']['score'] >= 11:
                self.loser = self.leftPlayer
                self.winner = self.rightPlayer
                await self.lobby.check_matches_state(self)
                break
            else:
                await self.send_message_to_players(
                    json.dumps({
                        "type": "game_state",
                        "gameState": {
                            "players": self.players,
                            "ball": self.ball
                        },
                        "content": self.html_content(),
                    })
                )
                await asyncio.sleep(0.01)  # sleep for 50ms


    def html_content(self):
        # Create the match score HTML content
        return f"""
            <div>
                <h2>Match Score</h2>
                <p>Left Player: {self.leftPlayer.pseudo} - score: {self.players['left']['score']}</p>
                <p>Right Player: {self.rightPlayer.pseudo} - score: {self.players['right']['score']}</p>
            </div>
        """

    # When match is Created send match accept menu to the two players
    async def send_accept_match_menu(self):
        html_waiting_content = f"""
            <div>
                <h2>Accept Match</h2>
                <p>Left Player: {self.leftPlayer.pseudo}</p>
                <p>Right Player: {self.rightPlayer.pseudo}</p>
        """

        html_accept_content = html_waiting_content

        html_accept_content += """
                <button onClick="handleGameButtonClick('accept_match')">Accept/button>
            </div>
        """

        html_waiting_content += """
                <p>Waiting ...</p>
            </div>
        """

        if self.left_accepted:
            await self.leftPlayer.send(json.dumps({
                    "type": "html",
                    "content": html_waiting_content,
                }))
        else:
            await self.leftPlayer.send(json.dumps({
                    "type": "html",
                    "content": html_accept_content,
                }))

        if self.right_accepted:
            await self.rightPlayer.send(json.dumps({
                    "type": "html",
                    "content": html_waiting_content,
                }))
        else:
            await self.rightPlayer.send(json.dumps({
                    "type": "html",
                    "content": html_accept_content,
                }))


    # Called by players to accept the match
    async def accept_match(self, player_channel_name):
        if self.leftPlayer.channel_name == player_channel_name:
            self.left_accepted = True
        elif self.rightPlayer.channel_name == player_channel_name:
            self.right_accepted = True

        if self.right_accepted and self.left_accepted:
            await self.start_match()
        else:
            await self.send_accept_match_menu()


    # if both player accepted, start the match
    async def start_match(self):

        # Create a match for the local game
        await self.send_message_to_players(
            json.dumps({
                "type": "init_game",
                "config": self.config,
                "gameState": {
                    "players": self.players,
                    "ball": self.ball
                },
                "content": self.html_content(),
            })
        )

        asyncio.create_task(self.send_game_state())


    # When match end send waiting menu to winner and back to main menu to loser
    async def send_match_end_menu(self, is_last_match):
        base_html_content = f"""
            <div class="container mt-3">
                <h2 class="text-center">Match Score</h2>
                <p class="text-center">Left Player: {self.leftPlayer.pseudo} - score: {self.players['left']['score']}</p>
                <p class="text-center">Right Player: {self.rightPlayer.pseudo} - score: {self.players['right']['score']}</p>
                <p class="text-center">Winner: {self.winner.pseudo}</p>
        """

        if is_last_match:
            html_winner_content = base_html_content + """
                    <div class="text-center mt-3">
                        <button class="btn btn-primary" onClick="handleGameButtonClick('back_to_main_menu')">Go back to menu</button>
                    </div>
                </div>
            """
        else:
            html_winner_content = base_html_content + """
                    <p class="text-center">Waiting for next game</p>
                </div>
            """

        html_loser_content = base_html_content + """
                <div class="text-center mt-3">
                    <button class="btn btn-primary" onClick="handleGameButtonClick('back_to_main_menu')">Go back to menu</button>
                </div>
            </div>
        """
        logger.info(f"send messages to winner and loser: winner {self.winner.pseudo}, loser {self.loser.pseudo}")
        await self.winner.send(
            json.dumps({
                "type": "end_game",
                "content": html_winner_content,
            })
        )
        await self.loser.send(
            json.dumps({
                "type": "end_game",
                "content": html_loser_content,
            })
        )
