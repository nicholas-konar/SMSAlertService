document.addEventListener("DOMContentLoaded", async function() {

    // Modal Window
    var overlay = document.createElement("div");
    overlay.classList.add("overlay");

    var modalHtmlResponse = await fetch("/modal/authenticate");
    var modalHtml = await modalHtmlResponse.text();

    var modalContainer = document.createElement("div");
    document.body.appendChild(modalContainer);
    modalContainer.innerHTML = modalHtml;

    var challengeModal = document.getElementById("challengeModal");
    var openChallengeModalBtn = document.getElementById("resetPasswordButton");
    var closeChallengeModalBtn = document.getElementById("closeChallengeButton");

    var validateModal = document.getElementById("validateModal");
    var openValidateModalBtn = document.getElementById("sendCodeButton");
    var closeValidateModalBtn = document.getElementById("closeValidateButton");

    // Open Challenge Modal
    openChallengeModalBtn.addEventListener("click", function() {
        challengeModal.style.display = "block";
        document.body.appendChild(overlay);
    });

    // Close Challenge Modal
    closeChallengeModalBtn.addEventListener("click", function() {
        challengeModal.style.display = "none";
        document.body.removeChild(overlay);
    });

    // Click off event
    window.addEventListener("click", function(event) {
        if (event.target == overlay) {
            challengeModal.style.display = "none";
            validateModal.style.display = "none";
            document.body.removeChild(overlay);
        }
    });

    // Open Validate Modal (after OTP sent successfully)
    function openValidateModal() {
      var validateModal = document.getElementById("validateModal");
      challengeModal.style.display = "none";
      validateModal.style.display = "block";
    }

    // Close Validate Modal
    closeValidateModalBtn.addEventListener("click", function() {
        validateModal.style.display = "none";
        document.body.removeChild(overlay);
    });

    // Send Code Button
    function sendCode() {
        var phoneNumber = document.getElementById("phoneNumber").value
        console.log(`JS btn got ${phoneNumber}`)
        fetch("/send/otp", {
            method: "POST",
            body: JSON.stringify({PhoneNumber: phoneNumber}),
            headers: {"Content-Type": "application/json"}
        })
        .then(response => response.json())
        .then(data => {
            var status = data.Status;
            var message = data.Message;
            if (status == "SUCCESS") {
                openValidateModal();
            } else {
                challengeStatusMessage = document.getElementById("challengeStatusMessage");
                challengeStatusMessage.innerHTML = message;
                challengeStatusMessage.classList.add("alert");
            }
        })
    };

    var sendCodeButton = document.getElementById("sendCodeButton");
    sendCodeButton.addEventListener("click", function() {
        sendCode();
    });

});
