function uploadAvatar(elementId, event) {
    const reader = new FileReader();
    reader.onload = function(e) {
        // show the image
        document.getElementById(elementId).src = e.target.result;
        // add the image to the local storage
        localStorage.setItem('avatar', e.target.result);
    };
    reader.readAsDataURL(event.target.files[0]);
}