// Utiliser l'URL définie dans api.js
const hostname = window.location.hostname;
const ApiUrl = `https://${hostname}:4243/auth`;
const BaseUrl = `https://${hostname}:4243`;

// Store initial
let store = {
  userInfos: null,
  friendList: null,
  gameHistory: null,
};

// Fonction pour charger ou recharger les données depuis l'API
async function fetchData(key, infoKey = null, forceRefetch = false) {
  // if (!store[key] || forceRefetch) {
  //   console.log(`${key} not loaded or refetch requested. Fetching from server...`);
  //   const data = await makeApiRequest(key, 'GET');
  //   store[key] = data;
  // }
  const data = await makeApiRequest(key, 'GET');
  store[key] = data;
  if (infoKey) {
    return store[key][infoKey] || null;
  } else {
    return store[key] || null;
  }
}

// Fonction pour nettoyer le localStorage et réinitialiser le store
function clearDataOnLogout() {
  // Réinitialiser le store
  store = {
    userInfos: null,
    friendList: null,
    gameHistory: null,
  };

  console.log('All user data has been cleared on logout');
}

async function refetchData(key) {
  return await fetchData(key, null, true);
}