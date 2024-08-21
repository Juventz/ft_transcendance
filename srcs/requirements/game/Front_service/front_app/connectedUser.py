import json
import random

class ConnectedUser:
    def __init__(self, channel_name, send):
        # Générer un pseudo aléatoire
        self.pseudo = "Player" + str(random.randint(1, 1000))
        self.id = None
        self.channel_name = channel_name
        self.lobby_id = None
        self.send = send

    # async def send(self, message):
    #     await self.send(message)

    async def send_main_menu(self):
        self.lobby_id = None

        html_content = """
            <div class="container" style="margin-top: 100px;">
                <div class="row-mt-5 justify-content-center col-xs-12 col-sm-12 col-md-12 col-lg-12 text-center">
                    <div class="col sweet-title-straight mt-1 mb-5 ml-3">
                        <span>Choose game mode</span>
                    </div>
                    <button type="submit" class="btn btn-secondary btn-lg" style="background-color: black" onClick="handleGameButtonClick('Local')">Local</button>
                    <button type="submit" class="btn btn-secondary btn-lg" style="background-color: black" onClick="handleGameButtonClick('Distant')">Distant</button>
                </div>
            </div>
        """
        await self.send(text_data=json.dumps({'type': 'html', 'content': html_content}))

    async def send_lobby_config(self):
        html_content = """
            <div class="container" style="margin-top: 100px;">
                <div class="row-mt-5 justify-content-center col-xs-12 col-sm-12 col-md-12 col-lg-12 text-center">
                    <div class="col sweet-title-straight mt-1 mb-5">
                        <span>Choose a lobby</span>
                    </div>
                <div class="input-group mb-3">
                    <input type="text" class="form-control" id="lobby_id" placeholder="Lobby's ID">
                    <button id="join_lobby" class="btn btn-secondary btn-sm" style="background-color: black" onClick="handleGameButtonClick('join_lobby', document.getElementById('lobby_id').value)">Join</button>
                    <button id="create_lobby" class="btn btn-secondary btn-sm" style="background-color: black"" onClick="handleGameButtonClick('create_lobby')">Create</button>
                </div>
            </div>
        """
        await self.send(text_data=json.dumps({'type': 'html', 'content': html_content}))
