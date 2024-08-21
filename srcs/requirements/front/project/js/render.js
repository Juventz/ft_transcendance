async function renderPages(pageKey) {
    switch (pageKey) {
        case 'loginPage':
        case 'signupPage':
        case 'signupFormPage':
        case 'homePage':
        case 'editProfilePage':
            return renderEditProfilePage();
        case 'profilePage':
            return renderProfilePage();
        case 'gamePage':
            return startGame();
        case 'friendsPage':
            return renderFriendsPage();
        case 'scoreBoardPage':
            return renderScoreBoardPage();
        default:
            console.log(`Page ${pageKey} not found`);
    }
}

async function renderNavbar() {
    const avatarElement = document.getElementById('navbarAvatar');

    // Récupérer l'avatar de l'utilisateur connecté
    const avatar = await fetchData('userInfos', 'avatar');
    if (avatar) {
        // Mettre à jour l'élément de l'avatar avec l'URL récupérée
        avatarElement.src = `${BaseUrl}${avatar}`;
    }
}

async function renderPage(pageKey, stateKey) {
    // Sélectionner tous les éléments dont l'ID commence par 'profilePage'
    const elements = document.querySelectorAll(`[id^="${pageKey}"]`);

    // Itérer sur chaque élément trouvé
    elements.forEach(async (element) => {
        // Extraire la clé du state associée à partir de l'ID de l'élément
        // Par exemple, si l'ID est 'profilePageUsername', la clé sera 'username'
        const infoKey = element.id.replace(pageKey, '').toLowerCase();

        // Récupérer la valeur correspondante du state
        // Supposons que `fetchData` est une fonction qui prend une clé et retourne la valeur associée du state
        let value = await fetchData(stateKey, infoKey);

        if (value === null) {
            // Si la valeur n'est pas trouvée, ne rien faire
            return;
        }
        // Mettre à jour le contenu de l'élément avec la valeur récupérée
        if (element.tagName === 'IMG') {
            // Décoder l'URL
            value = `${BaseUrl}${value}`;
            element.src = value;
        } else {
            element.textContent = value;
        }
    });
}

async function renderProfilePage() {
    // Récupérer les informations de l'utilisateur connecté
    const userInfos = await fetchData('userInfos');

    // Sélectionner les éléments de la page de profil et appliquer les classes Bootstrap
    const profilePageUsername = document.getElementById('profilePageUsername');
    const profilePageEmail = document.getElementById('profilePageEmail');
    const profilePageAvatar = document.getElementById('profilePageAvatar');
    const profilePageDate = document.getElementById('profilePageDate');
    const profilePageVictories = document.getElementById('profilePageVictories');
    const profilePageDefeats = document.getElementById('profilePageDefeats');
    const profilePageWinRate = document.getElementById('profilePageWinRate');
    const profilePageTournamentVictories = document.getElementById('profilePageTournamentVictories');

    // Mettre à jour le contenu des éléments avec les informations récupérées
    profilePageUsername.textContent = userInfos.username;
    profilePageEmail.textContent = userInfos.email;
    if (userInfos.avatar)
        profilePageAvatar.src = `${BaseUrl}${userInfos.avatar}`;
    profilePageVictories.textContent = userInfos.victories;
    profilePageDefeats.textContent = userInfos.defeats;
    if (userInfos.victories + userInfos.defeats === 0)
        profilePageWinRate.textContent = 'N/A';
    else
        profilePageWinRate.textContent = `${(userInfos.victories / (userInfos.victories + userInfos.defeats) * 100).toFixed(0)} %`;
    profilePageTournamentVictories.textContent = userInfos.tournament_victories;
    profilePageDate.textContent = new Date(userInfos.date).toLocaleDateString();
}

async function renderEditProfilePage() {
    // Sélectionner tous les éléments que nous voulons mettre à jour
    const elements = document.querySelectorAll(
        '#editProfilePageUsername, #editProfilePageEmail, #editProfilePageAvatar'
    );

    // Itérer sur chaque élément trouvé
    elements.forEach(async (element) => {
        // Extraire la clé du state associée à partir de l'ID de l'élément
        // Par exemple, si l'ID est 'editProfilePageUsername', la clé sera 'username'
        const infoKey = element.id.replace('editProfilePage', '').toLowerCase();

        // Récupérer la valeur correspondante du state
        // Supposons que `fetchData` est une fonction qui prend une clé et retourne la valeur associée du state
        let value = await fetchData('userInfos', infoKey);

        if (value === null) {
            // Si la valeur n'est pas trouvée, ne rien faire
            return;
        }
        // Mettre à jour le contenu de l'élément avec la valeur récupérée
        if (element.tagName === 'IMG') {
            // Décoder l'URL
            value = `${BaseUrl}${value}`;
            element.src = value;
        } else {
            element.value = value;
        }
    });
}

async function renderFriendsPage() {
    // Récupérer la liste des amis de l'utilisateur connecté
    const friends = await fetchData('friendList', 'friends');
    const friendRequestsReceived = await fetchData('friendList', 'friendRequestsReceived');

    console.log("Friends: ", friends, "Friend Requests: ", friendRequestsReceived);

    // Sélectionner l'élément de la liste d'amis et appliquer les classes Bootstrap
    const friendsList = document.getElementById('friendsList');
    friendsList.className = 'list-group';

    // Réinitialiser la liste d'amis
    friendsList.innerHTML = '';

    // Itérer sur chaque ami et ajouter un élément à la liste avec Bootstrap classes
    friends.forEach((friend) => {
        const friendElement = document.createElement('li');
        friendElement.className = 'list-group-item d-flex justify-content-between align-items-center';
        
        const avatar = document.createElement('img');
        avatar.src = "../static/duck.png";
        if (friend.avatar) 
            avatar.src = `${BaseUrl}${friend.avatar}`;
        avatar.alt = 'Avatar';
        avatar.className = 'img-thumbnail mr-2 rounded-circle'; // Bootstrap class for images
        avatar.style.width = '50px';
        avatar.style.height = '50px';
        friendElement.appendChild(avatar);
        
        const username = document.createElement('span');
        username.textContent = friend.username;
        friendElement.appendChild(username);
        
        const statusButton = document.createElement('button');
        statusButton.textContent = 'Status';
        statusButton.className = `btn ${friend.is_active ? 'btn-success' : 'btn-danger'}`; // Bootstrap buttons
        friendElement.appendChild(statusButton);
        
        friendsList.appendChild(friendElement);
    });

    // Sélectionner l'élément de la liste des demandes d'amis reçues et appliquer les classes Bootstrap
    const friendRequestsList = document.getElementById('friendRequestsList');
    friendRequestsList.className = 'list-group';

    // Réinitialiser la liste des demandes d'amis reçues
    friendRequestsList.innerHTML = '';

    // Itérer sur chaque demande d'ami reçue et ajouter un élément à la liste avec Bootstrap classes
    friendRequestsReceived.forEach((request) => {
        const requestElement = document.createElement('li');
        requestElement.className = 'list-group-item d-flex justify-content-between align-items-center';
        
        const avatar = document.createElement('img');
        avatar.src = "../static/duck.png";
        if (request.avatar) 
            avatar.src = `${BaseUrl}${request.avatar}`;
        avatar.alt = 'Avatar';
        avatar.className = 'img-thumbnail mr-2 rounded-circle'; // Bootstrap class for images
        avatar.style.width = '50px';
        avatar.style.height = '50px';
        requestElement.appendChild(avatar);
        
        const username = document.createElement('span');
        username.textContent = request.username;
        requestElement.appendChild(username);
        
        const acceptButton = document.createElement('button');
        acceptButton.textContent = 'Accept';
        acceptButton.className = 'btn btn-primary'; // Bootstrap primary button
        acceptButton.addEventListener('click', async () => {
            makeApiRequest('acceptFriendRequest', 'POST', { username: request.username });

            // Mettre à jour la liste des amis
            await refetchData('friendList');
            await renderFriendsPage();
        });
        requestElement.appendChild(acceptButton);
        
        const rejectButton = document.createElement('button');
        rejectButton.textContent = 'Reject';
        rejectButton.className = 'btn btn-secondary'; // Bootstrap secondary button
        rejectButton.addEventListener('click', async () => {
            makeApiRequest('declineFriendRequest', 'POST', { username: request.username });

            // Mettre à jour la liste des amis
            await refetchData('friendList');
            await renderFriendsPage();
        });
        requestElement.appendChild(rejectButton);
        
        friendRequestsList.appendChild(requestElement);
    });
}

async function renderScoreBoardPage() {
    const tournaments = await fetchData('gameHistory', 'tournaments');
    const scoreBoardList = document.getElementById('tournamentList');
    scoreBoardList.innerHTML = '';

    for (const tournament of tournaments) {
        const tournamentElement = document.createElement('div');
        tournamentElement.className = 'card mb-3';

        const cardHeader = document.createElement('div');
        cardHeader.className = 'card-header d-flex justify-content-between'; // Utilisez d-flex et justify-content-between pour aligner les éléments aux extrémités
        
        // Convertir la date du tournoi
        const tournamentDate = new Date(tournament.date).toLocaleString('fr-FR', {
            day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit'
        });
        
        // Élément pour la date
        const dateElement = document.createElement('span');
        dateElement.textContent = tournamentDate;
        
        // Élément pour le nom du gagnant
        const winnerElement = document.createElement('span');
        winnerElement.innerHTML = `<strong>${tournament.winner}</strong>`; // Utilisez innerHTML pour inclure des balises HTML comme <strong>
        
        // Ajouter les éléments à cardHeader
        cardHeader.appendChild(dateElement);
        cardHeader.appendChild(winnerElement);
        
        // Ajouter cardHeader à tournamentElement
        tournamentElement.appendChild(cardHeader);

        const cardBody = document.createElement('div');
        cardBody.className = 'card-body';
        tournamentElement.appendChild(cardBody);
        
        const playersList = document.createElement('ul');
        playersList.className = 'list-group mb-3';
        cardBody.appendChild(playersList);
        
        for (const player of tournament.players) {
            const playerElement = document.createElement('li');
            playerElement.className = 'list-group-item d-flex align-items-center'; // Ajout de classes pour aligner les éléments
        
            // Déterminer si le joueur est le gagnant
            if (player.username === tournament.winner) {
                playerElement.classList.add('bg-success-pale'); // Classe pour fond vert
            } else {
                playerElement.classList.add('bg-danger-pale'); // Classe pour fond rouge
            }
        
            // Créer et ajouter l'avatar
            const avatarImg = document.createElement('img');
            avatarImg.src = "../static/duck.png";
            if (player.avatar) 
                avatarImg.src = `${BaseUrl}${player.avatar}`;
            avatarImg.className = 'mr-2'; // Ajoute une marge à droite
            avatarImg.style.width = '30px'; // Taille de l'avatar
            avatarImg.style.height = '30px'; // Taille de l'avatar
            avatarImg.style.borderRadius = '50%'; // Rend l'avatar circulaire
            playerElement.appendChild(avatarImg);
        
            // Créer et ajouter le pseudo
            const playerName = document.createElement('span');
            playerName.textContent = player.username; // Supposons que chaque joueur a une propriété 'username'
            playerElement.appendChild(playerName);
        
            playersList.appendChild(playerElement);
        }

        // Bouton dropdown pour afficher/masquer la liste des jeux
        const gamesDropdownButton = document.createElement('button');
        gamesDropdownButton.className = 'btn btn-primary dropdown-toggle';
        gamesDropdownButton.textContent = 'Show Games';
        gamesDropdownButton.setAttribute('data-toggle', 'collapse');
        const gamesListId = `gamesList-${tournament.id}`; // Assurez-vous que tournament.id est unique
        gamesDropdownButton.setAttribute('data-target', `#${gamesListId}`);
        cardBody.appendChild(gamesDropdownButton);

        // Liste des jeux en tant que contenu collapsible
        const gamesList = document.createElement('div');
        gamesList.id = gamesListId;
        gamesList.className = 'collapse list-group'; // Utilisez 'collapse' pour cacher par défaut
        cardBody.appendChild(gamesList);

        for (const game of tournament.games) {
            const gameElement = document.createElement('div');
            gameElement.className = 'list-group-item d-flex justify-content-between align-items-center';
 
            // Création du conteneur pour le gagnant
            const winnerContainer = document.createElement('div');
            winnerContainer.className = 'd-flex align-items-center'; // Utilisez des classes Bootstrap pour le flexbox

            // Avatar du gagnant
            const winnerAvatar = document.createElement('img');
            winnerAvatar.src = game.winner_avatar ? `${BaseUrl}${game.winner_avatar}` : '../static/duck.png';
            winnerAvatar.alt = 'Avatar';
            winnerAvatar.className = 'img-thumbnail mr-2 rounded-circle'; // Ajout de 'rounded-circle' pour rendre l'image ronde
            winnerAvatar.style.width = '50px';
            winnerAvatar.style.height = '50px';
            winnerContainer.appendChild(winnerAvatar);

            // Nom du gagnant
            const winnerName = document.createElement('span');
            winnerName.textContent = game.winner;
            winnerContainer.appendChild(winnerName);

            // Ajout du conteneur du gagnant au gameElement
            gameElement.appendChild(winnerContainer);

            // Score
            const score = document.createElement('span');
            score.textContent = `${game.winner_score} - ${game.loser_score}`;
            score.className = 'mx-3'; // Marges sur les côtés pour l'espacement
            score.style.fontWeight = 'bold';
            score.style.fontSize = '1.5rem'; // Taille plus grande pour le score
            gameElement.appendChild(score);

            // Création du conteneur pour le perdant
            const loserContainer = document.createElement('div');
            loserContainer.className = 'd-flex align-items-center'; // Flexbox

            // Avatar du perdant
            const loserAvatar = document.createElement('img');
            loserAvatar.src = game.loser_avatar ? `${BaseUrl}${game.loser_avatar}` : '../static/duck.png';
            loserAvatar.alt = 'Avatar';
            loserAvatar.className = 'img-thumbnail mr-2 rounded-circle'; // 'rounded-circle' pour l'arrondi
            loserAvatar.style.width = '50px';
            loserAvatar.style.height = '50px';
            loserContainer.appendChild(loserAvatar);

            // Nom du perdant
            const loserName = document.createElement('span');
            loserName.textContent = game.loser;
            loserContainer.appendChild(loserName);

            // Ajout du conteneur du perdant au gameElement
            gameElement.appendChild(loserContainer);

            gamesList.appendChild(gameElement);
        }

        scoreBoardList.appendChild(tournamentElement);
    }
}