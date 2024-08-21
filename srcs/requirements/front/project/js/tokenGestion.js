// Fonction pour stocker les tokens et leur durée de validité
function storeTokens(accessToken, refreshToken, expiresIn) {
    const expiresAt = new Date().getTime() + expiresIn * 1000; // Convertir en timestamp
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
    localStorage.setItem('expiresAt', expiresAt);
}

// Fonction pour récupérer un nouvel access_token avec le refresh_token
async function refreshToken() {
    const refreshToken = localStorage.getItem('refreshToken');

    if (!refreshToken) {
        // Pas de refresh_token, déconnecter l'utilisateur
        console.error('No refresh token found. Please login again.');
        return null;
    }

    const response = await fetch(`${ApiUrl}/token/refresh`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refreshToken }),
    });
    const data = await response.json();
    if (response.ok) {
        storeTokens(data.accessToken, data.refreshToken, data.expiresIn);
        return data.accessToken;
    } else {
        // Gérer l'erreur, par exemple en déconnectant l'utilisateur
        console.error('Session expired. Please login again.');
        return null;
    }
}

// Fonction pour vérifier si l'access_token est valide et le rafraîchir si nécessaire
async function getAccessToken() {
    const expiresAt = localStorage.getItem('expiresAt');

    if (!expiresAt) {
        // Pas de token, déconnecter l'utilisateur
        console.error('No access token found. Please login again.');
        return null;
    }

    if (new Date().getTime() > expiresAt) {
        // Le token a expiré, obtenir un nouveau token
        return await refreshToken();
    } else {
        // Le token est toujours valide
        return localStorage.getItem('accessToken');
    }
}

async function makeApiRequest(route, type, body) {
    const accessToken = await getAccessToken();
    if (!accessToken) {
        // Remove navbar
        document.getElementById("navbar").innerHTML = '';
        clearDataOnLogout();
        navigate('startPage', false);
        return null;
    }

    const headers = {
        'Authorization': `Bearer ${accessToken}`,
    };

    if (type === 'POST' || type === 'PUT') {
        headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(`${ApiUrl}/${route}`, {
        method: type,
        headers,
        body: body ? JSON.stringify(body) : undefined,
    });

    if (response.status === 401) {
        // Token invalide ou expiré, déconnecter l'utilisateur
        console.error('Invalid or expired token. Please login again.');
        clearDataOnLogout();
        navigate('startPage', false);
        return null;
    }

    return await response.json();
}