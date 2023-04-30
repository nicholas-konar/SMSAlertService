document.addEventListener("DOMContentLoaded", function() {

    function login(username, password) {
        fetch("/login", {
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
                console.log("login success")
                window.location.href = "/account";
            } else {
                console.log("failed login")
                var loginStatusMessage = document.getElementById("loginStatusMessage");
                loginStatusMessage.innerHTML = data.Message;
                loginStatusMessage.classList.add("alert");
            }
        })
        .catch(error => console.error(error));
    }

    var loginButton = document.getElementById("loginButton");
    loginButton.addEventListener('click', function() {
        username = document.getElementById("usernameInputField").value;
        password = document.getElementById("passwordInputField").value;
        login(username, password);
    })
});