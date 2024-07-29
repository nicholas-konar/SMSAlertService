document.addEventListener("DOMContentLoaded", function() {

    var updateUsernameButton = document.getElementById("updateUsernameButton");
    updateUsernameButton.addEventListener('click', function() {
        username = document.getElementById("newUsernameField").value;
        updateUsername(username);
    })

    function updateUsername(username) {
        fetch("/account/update/username", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                NewUsername: username
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.Status == "SUCCESS"){
                window.location.href = "/account";
            } else {
                var editInfoStatusMessage = document.getElementById("editInfoStatusMessage");
                editInfoStatusMessage.innerHTML = data.Message;
                editInfoStatusMessage.classList.add("red");
            }
        })
        .catch(error => console.error(error));
    }
});