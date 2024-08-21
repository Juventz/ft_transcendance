async function handleEditEmail() {
    const newEmail = document.getElementById('editProfilePageEmail').value;
    if (newEmail) {
        const response = await makeApiRequest('updateEmail', 'PUT', { email: newEmail });
        if (response.successMessage) {
            document.getElementById('editProfilePageEmailError').textContent = '';
            document.getElementById('editProfilePageEmail').value = '';
            document.getElementById('editProfilePageEmailSuccess').textContent = response.successMessage;

            // Clear the cache
            await refetchData('userInfos');

        } else if (response.errorMessage) {
            document.getElementById('editProfilePageEmailError').textContent = response.errorMessage;
            document.getElementById('editProfilePageEmailSuccess').textContent = '';
        }
    }
}

async function handleEditUsername() {
    const newUsername = document.getElementById('editProfilePageUsername').value;
    if (newUsername) {
        const response = await makeApiRequest('updateUsername', 'PUT', { username: newUsername });
        if (response.successMessage) {
            document.getElementById('editProfilePageUsernameError').textContent = '';
            document.getElementById('editProfilePageUsername').value = '';
            document.getElementById('editProfilePageUsernameSuccess').textContent = response.successMessage;

            // Clear the cache
            await refetchData('userInfos');

        } else if (response.errorMessage) {
            document.getElementById('editProfilePageUsernameError').textContent = response.errorMessage;
            document.getElementById('editProfilePageUsernameSuccess').textContent = '';
        }
    }
}

async function handleEditPassword() {
    const newPassword = document.getElementById('editProfilePagePassword').value;
    const confirmPassword = document.getElementById('editProfilePageConfirmPassword').value;

    if (newPassword !== confirmPassword) {
        document.getElementById('editProfilePagePasswordError').textContent = 'Passwords do not match';
        document.getElementById('editProfilePagePasswordSuccess').textContent = '';
        return;
    }

    if (newPassword) {
        const response = await makeApiRequest('updatePassword', 'PUT', { password: newPassword });
        if (response.successMessage) {
            document.getElementById('editProfilePagePasswordError').textContent = '';
            document.getElementById('editProfilePagePassword').value = '';
            document.getElementById('editProfilePageConfirmPassword').value = '';
            document.getElementById('editProfilePagePasswordSuccess').textContent = response.successMessage;

            // Clear the cache
            await refetchData('userInfos');

        } else if (response.errorMessage) {
            document.getElementById('editProfilePagePasswordError').textContent = response.errorMessage;
            document.getElementById('editProfilePagePasswordSuccess').textContent = '';
        }
    }
}

async function handleEditAvatar() {
    const newAvatar = localStorage.getItem('avatar');
    if (newAvatar) {
        const formData = new FormData();
        const blob = await fetch(newAvatar).then(response => response.blob());
        formData.append('avatar', blob, 'avatar.png');

        console.log('blob', blob);

        const accessToken = await getAccessToken();
        if (!accessToken) {
            navigate('startPage', false);
            return null;
        }
    
        const headers = {
            'Authorization': `Bearer ${accessToken}`,
        };

        let response = await fetch(`${ApiUrl}/updateAvatar`, {
            method: 'POST',
            headers,
            body: formData,
        });
    
        response = await response.json();

        if (response.successMessage) {
            document.getElementById('editProfilePageAvatarError').textContent = '';
            document.getElementById('editProfilePageAvatarSuccess').textContent = response.successMessage;

            // Clear the cache
            localStorage.removeItem('avatar');
            await refetchData('userInfos');

        } else if (response.errorMessage) {
            document.getElementById('editProfilePageAvatarError').textContent = response.errorMessage;
            document.getElementById('editProfilePageAvatarSuccess').textContent = '';
        }
    }
}

async function handleSendFriendRequest() {
    const friendUsername = document.getElementById('friendsPageUsername').value;
    if (friendUsername) {
        const response = await makeApiRequest('friendRequest', 'POST', { username: friendUsername });
        console.log('response', response);
        if (response.successMessage) {
            document.getElementById('friendsPageUsernameError').textContent = '';
            document.getElementById('friendsPageUsername').value = '';
            document.getElementById('friendsPageUsernameSuccess').textContent = response.successMessage;

            // Clear the cache
            await refetchData('friendList');

        } else if (response.errorMessage) {
            document.getElementById('friendsPageUsernameError').textContent = response.errorMessage;
            document.getElementById('friendsPageUsernameSuccess').textContent = '';
        }
    }
}