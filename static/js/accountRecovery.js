document.addEventListener("DOMContentLoaded", function() {


    function resetPassword(newPassword) {
        fetch("/account/update/password", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({NewPassword: newPassword})
        })
        .then(response => response.json())
        .then(data => {
            var resetPasswordStatusMessage = document.getElementById("resetPasswordStatusMessage");
            var resetPasswordForm = document.getElementById("resetPasswordForm");
            if (data.Status == "SUCCESS") {
                resetPasswordStatusMessage.innerHTML = data.Message;
                resetPasswordForm.style.display = "none";
                backToLoginButton.style.display = "block";
            } else {
                resetPasswordStatusMessage.innerHTML = data.Message;
                resetPasswordStatusMessage.classList.remove("info");
                resetPasswordStatusMessage.classList.add("alert");
            }
        })
        .catch(error => console.error(error));
    }

    var resetPasswordButton = document.getElementById("resetPasswordButton");
    resetPasswordButton.addEventListener('click', function() {
        var newPassword = document.getElementById("newPasswordField").value;
        resetPassword(newPassword);
    });

    var resetPasswordForm = document.getElementById("resetPasswordForm");
    resetPasswordForm.addEventListener("submit", function(event) {
        event.preventDefault();
        var newPassword = document.getElementById("newPasswordField").value;
        resetPassword(newPassword);
    })

    var backToLoginButton = document.getElementById("backToLoginButton");
    backToLoginButton.style.display = "none";
    backToLoginButton.addEventListener("click", function() {
        window.location.href = "/login";
    })
});