let isFirstLoad = true; // Ajouter un indicateur pour le premier chargement

async function navigate(pageId, pushState = true) {
    // Liste des pages qui ne nécessitent pas de vérification de connexion
    const noAuthRequiredPages = ['loginPage', 'signupPage', 'signupFormPage'];

    // Vérifier si la page actuelle nécessite une vérification de connexion
    const isAuthRequired = !noAuthRequiredPages.includes(pageId);

    // Vérifier si l'utilisateur était sur la page de jeu afin de le faire quitter le jeu
    if (history.state && history.state.page === 'gamePage' && pageId !== 'gamePage') {
        closeGame();
    }

    // Vérifier si l'utilisateur est connecté avant de continuer, sauf pour les pages spécifiées
    if (isAuthRequired) {
        const isLoggedIn = await getAccessToken();
        if (!isLoggedIn) {
            // Si l'utilisateur n'est pas connecté, rediriger vers la page de connexion/startPage
            pageId = 'startPage';
            document.getElementById("navbar").innerHTML = "";
            clearDataOnLogout();
        } else {
            // Si l'utilisateur est connecté, affichez la navbar
            const response = await fetch('templates/navbar.html');
            const content = await response.text();
            document.getElementById("navbar").innerHTML = content;

            // Rendre la navbar
            await renderNavbar();
        }
    }

    const response = await fetch(`templates/${pageId}.html`);
    const content = await response.text();
    document.getElementById('pageContainer').innerHTML = content;

    // Rendre les éléments de la page
    await renderPages(pageId);

    // Condition pour ne pas pousser un état si c'est le premier chargement et qu'il n'y a pas de hash
    if (pushState && !(isFirstLoad && window.location.hash === "")) {
        history.pushState({page: pageId}, "", "#" + pageId);
    }
    isFirstLoad = false; // Après le premier chargement, définir comme faux
}

async function getDefaultPage() {
    // Détermine la page par défaut en fonction de l'état de connexion
    const isLoggedIn = await getAccessToken();
    return isLoggedIn ? 'homePage' : 'startPage';
}

window.addEventListener("popstate", async function(event) {
    const page = window.location.hash ? window.location.hash.substring(1) : await getDefaultPage();
    navigate(page, false);
});

window.onload = async function() {
    const page = window.location.hash ? window.location.hash.substring(1) : await getDefaultPage();
    navigate(page, false);
};

window.addEventListener("beforeunload", async function(event) {
    // Envoyer une requête de déconnexion avant de quitter la page
    await makeApiRequest('logout', 'POST');
});