
var square = document.getElementById("square");
var x = 50; // initial x position
var y = 50; // initial y position
var dx = 4; // x velocity
var dy = 2; // y velocity

function animateSquare() {
    x += dx;
    y += dy;

    // Check if the square has reached the edges
    if (x <= 0 || x >= window.innerWidth - 30) {
        dx = -dx; // reverse x velocity
    }
    if (y <= 0 || y >= window.innerHeight - 30) {
        dy = -dy; // reverse y velocity
    }

    square.style.width = "10px"; // set width to half of the original size
    square.style.height = "10px"; // set height to half of the original size

    square.style.left = x + "px";
    square.style.top = y + "px";

    requestAnimationFrame(animateSquare);
}

var leftBar = document.createElement("div");
leftBar.classList.add("bar");
leftBar.style.top = getRandomPosition() + "px"; // Set random top position
leftBar.style.left = "10px"; // Set fixed left position
document.body.appendChild(leftBar);

var rightBar = document.createElement("div");
rightBar.classList.add("bar");
rightBar.style.top = getRandomPosition() + "px"; // Set random top position
rightBar.style.right = "10px"; // Set fixed right position
document.body.appendChild(rightBar);

function getRandomPosition() {
    var min = 10; // Minimum position
    var max = window.innerHeight - 200 - 10; // Maximum position
    return Math.floor(Math.random() * (max - min + 1) + min);
}

var leftBarDirection = -1; // -1 for moving up
var rightBarDirection = 1; // 0 for not moving

function animateBars() {
    var leftBarTop = parseInt(leftBar.style.top);
    var rightBarTop = parseInt(rightBar.style.top);

    // Check if the bars have reached the edges
    if (leftBarTop <= 15 || leftBarTop >= window.innerHeight - 200 - 30) {
        leftBarDirection = -leftBarDirection; // reverse direction
    }
    if (rightBarTop <= 15 || rightBarTop >= window.innerHeight - 200 - 30) {
        rightBarDirection = -rightBarDirection; // reverse direction
    }

    leftBar.style.top = (leftBarTop + 3 * leftBarDirection) + "px";
    rightBar.style.top = (rightBarTop + 3 * rightBarDirection) + "px";

    requestAnimationFrame(animateBars);
}

animateBars();

function checkCollision() {
    var leftBarTop = parseInt(leftBar.style.top);
    var rightBarTop = parseInt(rightBar.style.top);

    // Check if the square collides with the bars
    if (x >= window.innerWidth - 20 - 10 && y >= rightBarTop && y <= rightBarTop + 200) {
        dx = -dx; // reverse x velocity
    } else if (x <= 10 && y >= leftBarTop && y <= leftBarTop + 200) {
        dx = -dx; // reverse x velocity
    }

    // Check if the square has reached the edges
    if (y <= 0 || y >= window.innerHeight - 20) {
        dy = -dy; // reverse y velocity
    }
    if (x <= 0 || x >= window.innerWidth - 20) {
        x = window.innerWidth / 2; // reset x position to the center of the screen
        y = window.innerHeight / 2; // reset y position to the center of the screen
        dx = -dx; // reverse x velocity
    }
}

function animateSquare() {
    x += dx;
    y += dy;

    checkCollision();

    square.style.width = "10px"; // set width to half of the original size
    square.style.height = "10px"; // set height to half of the original size

    square.style.left = x + "px";
    square.style.top = y + "px";

    requestAnimationFrame(animateSquare);
}

animateSquare();