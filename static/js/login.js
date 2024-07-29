document.addEventListener("DOMContentLoaded", function() {

    var loginButton = document.getElementById("loginButton");
    loginButton.addEventListener('click', function() {
        username = document.getElementById("usernameInputField").value;
        password = document.getElementById("passwordInputField").value;
        login(username, password);
    })

    function login(username, password) {
        fetch("/account/login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                Username: username,
                Password: password
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.Status == "SUCCESS"){
                window.location.href = "/account";
            } else {
                var loginStatusMessage = document.getElementById("loginStatusMessage");
                loginStatusMessage.innerHTML = data.Message;
                loginStatusMessage.classList.add("red");
            }
        })
        .catch(error => console.error(error));
    }
});