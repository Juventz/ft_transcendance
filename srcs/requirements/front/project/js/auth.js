async function handleSignup() {
    // Verify the passwords
    const password = document.getElementById('passwordSignup').value;
    const confirmPassword = document.getElementById('confirmPasswordSignup').value;
    if (password !== confirmPassword) {
        const confirmPasswordError = document.getElementById('confirmPasswordError');
        confirmPasswordError.innerText = 'Passwords do not match';
        return;
    }

    // Get the form data
    const formData = new FormData();
    formData.append('email', document.getElementById('emailSignup').value);
    formData.append('username', document.getElementById('usernameSignup').value);
    formData.append('password', document.getElementById('passwordSignup').value);
    if (localStorage.getItem('avatar')) {
        const blob = await fetch(localStorage.getItem('avatar')).then(response => response.blob());
        formData.append('avatar', blob, 'avatar.png');
        console.log(blob);
    }

    // Send the data to the API
    fetch(`${ApiUrl}/signup`, {
        method: 'POST',
        body: formData,
    }).then(response => {
        if (response.ok) {
            response.json().then(data => {
                // Store the tokens
                storeTokens(data.accessToken, data.refreshToken, data.expiresIn);

                // Clear the avatar and history
                localStorage.removeItem('avatar');
                window.history.replaceState({}, document.title, window.location.pathname);

                // Redirect to the home page
                navigate('homePage');
            });
        } else {
            console.log("signup error: ", response);
            // Handle the error
            response.json().then(data => {
                const errorElement = document.getElementById('confirmPasswordError');
                errorElement.innerText = data.errorMessage;
            });
        }
    }).catch(error => {
        const errorElement = document.getElementById('confirmPasswordError');
        errorElement.innerText = 'An error occurred';
    });
};

async function handleLogin() {
    // Get the form data
    const username = document.getElementById('usernameLogin').value;
    const password = document.getElementById('passwordLogin').value;

    // Send the data to the API
    await fetch(`${ApiUrl}/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
    }).then(response => {
        if (response.ok) {
            response.json().then(data => {
                // Store the tokens
                storeTokens(data.accessToken, data.refreshToken, data.expiresIn);

                // Clear the history
                window.history.replaceState({}, document.title, window.location.pathname);

                // Redirect to the home page
                navigate('homePage');
            });
        } else {
            // Handle the error
            response.json().then(data => {
                console.log("login error: ", data);
                const errorElement = document.getElementById('loginError');
                errorElement.innerText = data.errorMessage;
            });
        }
    }).catch(error => {
        const errorElement = document.getElementById('loginError');
        errorElement.innerText = 'An error occurred';
    });
};

// handle 42 login redirection
function handle42Login() {
    const hostname = window.location.hostname;
    const url = `https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-f5c5921ffe4bfdfa83e528698d26c32ffbb288ff911f2e66d44bc7c9e53546ed&redirect_uri=https%3A%2F%2F${hostname}%3A4243%2F&response_type=code`;

    // Redirect the user to the authorization URL
    window.location.href = url;
}

// handle 42 login return
async function handle42Return(code) {
    // Send the code to the API
    await fetch(`${ApiUrl}/login42`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            code: code,
            redirectUri: `https://${window.location.hostname}:4243/`, 
        }),
    }).then(response => {
        if (response.ok) {
            response.json().then(data => {
                // Store the tokens
                storeTokens(data.accessToken, data.refreshToken, data.expiresIn);

                // Clear the history
                window.history.replaceState({}, document.title, window.location.pathname);

                // Redirect to the home page
                navigate('homePage');
            });
        } else {
            // Handle the error
            response.json().then(data => {
                const errorElement = document.getElementById('loginError');
                errorElement.innerText = data.error;
            });
        }
    }).catch(error => {
        const errorElement = document.getElementById('loginError');
        errorElement.innerText = 'An error occurred';
    });
}

document.addEventListener('DOMContentLoaded', async () => {
    console.log('DOMContentLoaded');

    // Extract the code from the URL
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');

    // Check if the code is present
    if (code) {
        // Remove the code from the URL
        window.history.replaceState({}, document.title, window.location.pathname);

        await handle42Return(code);
    }
});

async function handleLogout() {
    // Send logout request to the API
    await makeApiRequest('logout', 'POST');

    // Remove the tokens
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('expiresAt');

    // Remove the navbar
    document.getElementById('navbar').innerHTML = '';

    // Remove user data
    clearDataOnLogout();

    // Redirect to the start page
    navigate('startPage');  
}