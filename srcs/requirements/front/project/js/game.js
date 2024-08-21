let closeGame;

function startGame() {
  /***************************************************************************
  *                           Create the game elements                       *
  ***************************************************************************/

  // Get the game screen element
  const gameScreen = document.getElementById('gameScreen');

  // Get the canvas element
  const canvas = document.getElementById('pong');

  // Get the 2D rendering context
  const context = canvas.getContext('2d');

  // Create the game structure
  let config = {};
  let gameState = null;

  /***************************************************************************
  *                           Create the WebSocket connection                *
  ***************************************************************************/


  let socket = new WebSocket(`wss://${window.location.hostname}:4243/ws/pong/`);

  socket.onopen = async function(e) {
      console.log("[open] Connection established");

      // Send jwt token to the server
        let accessToken = localStorage.getItem('accessToken');
        socket.send(JSON.stringify({ type: 'auth', token: accessToken}));
  };

  socket.onclose = function(event) {
      console.log(`[close] Connection closed`);
      // Navigate to the home page
      navigate("homePage", false);
  };

  socket.onerror = function(error) {
      console.log(`[error] ${error.message}`);
  };

  socket.onmessage = function(event) {
      let data = JSON.parse(event.data);
      switch (data.type) {
          case 'html':
              gameScreen.innerHTML = data.content;
              break;
          case 'init_game':
              gameScreen.innerHTML = data.content;
              gameState = data.gameState;
              config = data.config;
              canvas.width = data.config.canvas.width;
              canvas.height = data.config.canvas.height;
              drawGame();
              break;
          case 'game_state':
              gameScreen.innerHTML = data.content;
              gameState = data.gameState;
              drawGame();
              break;
          case 'end_game':
            context.clearRect(0, 0, canvas.width, canvas.height);
            gameScreen.innerHTML = data.content;
      }
  }

  /***************************************************************************
  *                         Game state and functions                         *
  ***************************************************************************/

  function drawRoundedRect(context, x, y, width, height, radius, color) {
    context.fillStyle = color;
    context.beginPath();
    context.moveTo(x + radius, y);
    context.lineTo(x + width - radius, y);
    context.quadraticCurveTo(x + width, y, x + width, y + radius);
    context.lineTo(x + width, y + height - radius);
    context.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    context.lineTo(x + radius, y + height);
    context.quadraticCurveTo(x, y + height, x, y + height - radius);
    context.lineTo(x, y + radius);
    context.quadraticCurveTo(x, y, x + radius, y);
    context.closePath();
    context.fill();
}

function drawPaddle(x, y, width, height, color) {
    const radius = 5; // Adjust the radius as needed
    drawRoundedRect(context, x, y, width, height, radius, color);
}

  //Ligne en pointille pout separer les 2 camps
  function drawDashedLine() {
    context.setLineDash([5, 15]);
    context.strokeStyle = 'white';
    context.beginPath();
    context.moveTo(canvas.width / 2, 0);
    context.lineTo(canvas.width / 2, canvas.height);
    context.stroke();
    context.setLineDash([]);
}

//Affiche les scores des joueurs
function drawScores() {
    context.fillStyle = 'white';
    context.font = '30px Arial';
    context.textAlign = 'center';
    context.fillText(gameState.players.left.score, canvas.width / 4, 50);
    context.fillText(gameState.players.right.score, 3 * canvas.width / 4, 50);
}

  // Draw the ball
  function drawBall(x, y, radius, color) {
      context.fillStyle = color;
      context.beginPath();
      context.arc(x, y, radius, 0, Math.PI * 2, false);
      context.closePath();
      context.fill();
  }

  //Ligne en pointille pout separer les 2 camps
  function drawDashedLine() {
    context.setLineDash([5, 15]);
    context.strokeStyle = 'white';
    context.beginPath();
    context.moveTo(canvas.width / 2, 0);
    context.lineTo(canvas.width / 2, canvas.height);
    context.stroke();
    context.setLineDash([]);
}

//Affiche les scores des joueurs
function drawScores() {
    context.fillStyle = 'white';
    context.font = '30px Arial';
    context.textAlign = 'center';
    context.fillText(gameState.players.left.score, canvas.width / 4, 50);
    context.fillText(gameState.players.right.score, 3 * canvas.width / 4, 50);
}

  // Dessiner les éléments du jeu sur le canvas
  function drawGame() {
        // Dessiner le fond du canvas
        context.fillStyle = config.canvas.color;
        context.fillRect(0, 0, canvas.width, canvas.height);
  
    // Dessiner les paddles
    drawPaddle(gameState.players.left.x, gameState.players.left.y, gameState.players.left.width, gameState.players.left.height, gameState.players.left.color);
    drawPaddle(gameState.players.right.x, gameState.players.right.y, gameState.players.right.width, gameState.players.right.height, gameState.players.right.color);

    // Dessiner la balle
    drawBall(gameState.ball.x, gameState.ball.y, gameState.ball.radius, gameState.ball.color);
    // Dessiner la ligne en pointillé
    drawDashedLine();
    // Dessiner les scores
    drawScores();
  }

  /***************************************************************************
  *                         Event handlers                                   *
  ***************************************************************************/

  function sendPaddlePosition(key, isDown = true) {
    socket.send(JSON.stringify({ type: 'paddle_position', key: key, isDown: isDown }));
  }

  window.handleGameButtonClick = function(buttonName, body) {
      console.log(`Button ${buttonName} clicked`);
      socket.send(JSON.stringify({ type: 'button_click', button: buttonName, body: body }));
  };

    closeGame = function () {
        // Fermer la WebSocket
        socket.close();
        console.log("WebSocket closed");

        // Retirer les event handlers
        // Assurez-vous que les fonctions passées à addEventListener sont nommées ou référencées pour pouvoir les retirer
        window.removeEventListener('keydown', keyDownHandler);
        window.removeEventListener('keyup', keyUpHandler);
        // window.removeEventListener('beforeunload', beforeUnloadHandler);
    }

    // Assurez-vous de définir keyDownHandler, keyUpHandler, et beforeUnloadHandler lors de l'ajout des event listeners
    // Exemple de définition de keyDownHandler (faites de même pour keyUpHandler et beforeUnloadHandler)
    function keyDownHandler(event) {
        if (gameState === null) {
            return;
        }
        switch (event.key) {
            case 'ArrowUp':
                sendPaddlePosition('ArrowUp');
                break;
            case 'ArrowDown':
                sendPaddlePosition('ArrowDown');
                break;
            case 'w':
                sendPaddlePosition('w');
                break;
            case 's':
                sendPaddlePosition('s');
                break;
        }
    }

    function keyUpHandler(event) {
        if (gameState === null) {
            return;
        }
        switch (event.key) {
            case 'ArrowUp':
                sendPaddlePosition('ArrowUp', false);
                break;
            case 'ArrowDown':
                sendPaddlePosition('ArrowDown', false);
                break;
            case 'w':
                sendPaddlePosition('w', false);
                break;
            case 's':
                sendPaddlePosition('s', false);
                break;
        }
    }

    // Ajouter les event listeners quelque part dans startGame ou une fonction initiale
    window.addEventListener('keydown', keyDownHandler);
    window.addEventListener('keyup', keyUpHandler);
    // window.addEventListener('beforeunload', beforeUnloadHandler);

    window.addEventListener("beforeunload", function (e) {
        socket.close();
    });

    return closeGame;
}