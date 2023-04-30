document.addEventListener("DOMContentLoaded", function() {

    function createAccount(username, pw, ph, verified) {
        fetch("/account/create", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                Username: username,
                PhoneNumber: ph,
                Password: pw,
                Verified: verified
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.Status == "SUCCESS"){
                console.log("Account created successfully.")
                window.location.href = "/account";
            } else {
                console.log("Account creation failed.")
                var loginStatusMessage = document.getElementById("signUpStatusMessage");
                loginStatusMessage.innerHTML = data.Message;
                loginStatusMessage.classList.add("alert");
            }
        })
        .catch(error => console.error(error));
    }

    var createAccountButton = document.getElementById("createAccountButton");
    createAccountButton.addEventListener('click', function(event) {
        event.preventDefault();
    })
});