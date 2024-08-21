import asyncio
import json
import random
import logging

logger = logging.getLogger(__name__)

class LocalGame:
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
        
    def update_paddle_position(self, key, isDown):
        player_side = 'left'
        if key == 'ArrowUp' or key == 'ArrowDown':
            player_side = 'right' 
        player = self.players[player_side]

        if isDown:
            if key == 'ArrowUp':
                self.players['right']['dy'] += -4
            elif key == 'ArrowDown':
                self.players['right']['dy'] += 4
            elif key == 'w':
                self.players['left']['dy'] += -4
            elif key == 's':
                self.players['left']['dy'] += 4
            elif key == 'stop':
                player['dy'] = 0
        else:
            player['dy'] = 0

    # Create a new task to send the game state to all players every 50ms
    async def send_game_state(self):
        while True:
            self.update()
            if self.players['left']['score'] >= 11:
                await self.lobby.send_match_end_menu(self.leftPlayer)
                break
            elif self.players['right']['score'] >= 11:
                await self.lobby.send_match_end_menu(self.rightPlayer)
                break
            else:
                await self.lobby.admin.send(
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
        # Updated match score HTML content with Bootstrap styling
        return f"""
            <div class="container mt-3">
                <h2 class="text-center">Match Score</h2>
                <ul class="list-group">
                    <li class="list-group-item">Left Player: <strong>{self.leftPlayer}</strong> - score: <span class="badge bg-primary rounded-pill">{self.players['left']['score']}</span></li>
                    <li class="list-group-item">Right Player: <strong>{self.rightPlayer}</strong> - score: <span class="badge bg-primary rounded-pill">{self.players['right']['score']}</span></li>
                </ul>
            </div>
        """

    async def start_match(self):

        # Create a match for the local game
        await self.lobby.admin.send(
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
