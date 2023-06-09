document.addEventListener("DOMContentLoaded", function() {

    var verifiedCredentialsEvent = new CustomEvent("verifiedCredentialsEvent");

    var createAccountStatusMessage = document.getElementById("createAccountStatusMessage");

    document.addEventListener("authenticationEvent", function(event) {
        var username = document.getElementById("usernameInputField").value;
        var ph = document.getElementById("modalPhoneNumberInputField").value;
        var pw = document.getElementById("passwordInputField").value;
        createAccount(username, ph, pw, true);
    })

    function createAccount(username, ph, pw, verified) {
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
                window.location.href = "/account";
            } else {
                var loginStatusMessage = document.getElementById("signUpStatusMessage");
                loginStatusMessage.innerHTML = data.Message;
                loginStatusMessage.classList.add("red");
            }
        })
        .catch(error => console.error(error));
    }

    var createAccountButton = document.getElementById("createAccountButton");
    createAccountButton.addEventListener('click', function(event) {
        event.preventDefault();
        var username = document.getElementById("usernameInputField").value;
        var ph = document.getElementById("phoneNumberInputField").value;
        var pw = document.getElementById("passwordInputField").value;
        var consent = document.getElementById("consentCheckBox");
        if (validateForm(username, ph, pw, consent)) {
            verifyCredentials(username, ph);
        }
    })

    function validateForm(username, ph, pw, consent) {
        const regex = /^\d{10}$/;
        if (username.length <= 3 || username.length >= 24) {
            createAccountStatusMessage.innerHTML = "Please enter a valid username.";
            createAccountStatusMessage.classList.add("red");
            return false;
        } else if (!regex.test(ph)) {
            createAccountStatusMessage.innerHTML = "Please enter a valid 10 digit phone number.";
            createAccountStatusMessage.classList.add("red");
            return false;
        } else if (pw.length < 8) {
            createAccountStatusMessage.innerHTML = "Your password must be at least 8 characters long.";
            createAccountStatusMessage.classList.add("red");
            return false;
        } else if (!consent.checked) {
            createAccountStatusMessage.innerHTML = "Please check the consent box to continue.";
            createAccountStatusMessage.classList.add("red");
            return false;
        } else {
            return true;
        }
    }

    function verifyCredentials(username, ph) {
        fetch("/account/create/validate/credentials", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                Username: username,
                PhoneNumber: ph
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.CredentialAvailability.Username == false) {
                createAccountStatusMessage.innerHTML = "Sorry, this username is not available.";
                createAccountStatusMessage.classList.add("red");
            } else if (data.CredentialAvailability.PhoneNumber == false) {
                createAccountStatusMessage.innerHTML = "Sorry, this phone number is not available.";
                createAccountStatusMessage.classList.add("red");
            } else {
                document.dispatchEvent(verifiedCredentialsEvent);
            }
        })
        .catch(error => console.error(error));
    }
});