document.addEventListener('DOMContentLoaded', function() {

    const createAccountButton = document.getElementById('createAccountButton');
    createAccountButton.addEventListener('click', function() {
        window.location.href = '/signup';
    });
});