document.addEventListener("DOMContentLoaded", async function() {

    var authenticationEvent = new CustomEvent("authenticationEvent");

    // Modal Container
    var overlay = document.createElement("div");
    overlay.classList.add("overlay");

    var modalHtmlResponse = await fetch("/modal/authenticate");
    var modalHtml = await modalHtmlResponse.text();

    var modalContainer = document.createElement("div");
    document.body.appendChild(modalContainer);
    modalContainer.innerHTML = modalHtml;


    // Create Account Trigger
    document.addEventListener("verifiedCredentialsEvent", function() {
      openChallengeModal('create');
    });

    // Reset Password Trigger
    var resetPasswordButton = document.getElementById("resetPasswordButton");
    if (resetPasswordButton) {
        resetPasswordButton.addEventListener("click", function() {
            openChallengeModal('recover');
        });
    }

    // Open Challenge Modal
    var challengeModal = document.getElementById("challengeModal");
    function openChallengeModal(flowType) {
        var phoneNumberInput = document.getElementById("phoneNumberInputField");
        console.log(`phoneNumberInputField value = ${phoneNumberInput}`)
        var modalPhoneNumberInputField = document.getElementById("phoneNumber");
        if (phoneNumberInput) {
            modalPhoneNumberInputField.value = phoneNumberInput.value;
        }
        var sendCodeButton = document.getElementById("sendCodeButton");
        sendCodeButton.setAttribute('flowType', flowType);
        var resendCodeButton = document.getElementById("resendCodeButton");
        resendCodeButton.setAttribute('flowType', flowType);
        challengeModal.style.display = "block";
        validateModal.style.display = "none";
        document.body.appendChild(overlay);
    }

    // Close Challenge Modal
    var closeChallengeModalBtn = document.getElementById("closeChallengeButton");
    closeChallengeModalBtn.addEventListener("click", function() {
        challengeModal.style.display = "none";
        document.body.removeChild(overlay);
    });

    // Open Validate Modal
    var validateModal = document.getElementById("validateModal");
    function openValidateModal(flowType) {
        var validateButton = document.getElementById("validateButton");
        validateButton.setAttribute('flowType', flowType);
        challengeModal.style.display = "none";
        validateModal.style.display = "block";
    }

    // Close Validate Modal
    var closeValidateModalBtn = document.getElementById("closeValidateButton");
    closeValidateModalBtn.addEventListener("click", function() {
        validateModal.style.display = "none";
        document.body.removeChild(overlay);
    });

    // Close All (click off)
    window.addEventListener("click", function(event) {
        if (event.target == overlay) {
            challengeModal.style.display = "none";
            validateModal.style.display = "none";
            document.body.removeChild(overlay);
        }
    });

    // Send Code Button
    var sendCodeButton = document.getElementById("sendCodeButton");
    sendCodeButton.addEventListener("click", function() {
        var flowType = sendCodeButton.getAttribute('flowType');
        sendCode(flowType);
    });

    function sendCode(flowType) {
        var ph = document.getElementById("phoneNumber").value;
        fetch(`account/${flowType}/send/otp`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                FlowType: flowType,
                PhoneNumber: ph
                })
        })
        .then(response => response.json())
        .then(data => {
            if (data.Status == "SUCCESS") {
                openValidateModal(data.FlowType);
            } else {
                challengeStatusMessage = document.getElementById("challengeStatusMessage");
                challengeStatusMessage.innerHTML = data.Message;
                challengeStatusMessage.classList.add("alert");
            }
        })
    };

    // Resend Code Button
    var resendCodeButton = document.getElementById("resendCodeButton");
    resendCodeButton.addEventListener("click", function() {
        var flowType = sendCodeButton.getAttribute('flowType');
        resendCode(flowType);
    });

    function resendCode(flowType) {
        var ph = document.getElementById("phoneNumber").value;
        fetch(`account/${flowType}/resend/otp`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                FlowType: flowType,
                PhoneNumber: ph
                })
        })
        .then(response => response.json())
        .then(data => {
            validateStatusMessage = document.getElementById("validateStatusMessage");
            if (data.Status == "SUCCESS") {
                validateStatusMessage.innerHTML = data.Message;
                validateStatusMessage.classList.remove("alert");
                validateStatusMessage.classList.add("info");
            } else {
                validateStatusMessage.innerHTML = data.Message;
                validateStatusMessage.classList.remove("info");
                validateStatusMessage.classList.add("alert");
            }
        })
    };

    // Validate Button
    var validateButton = document.getElementById('validateButton');
    validateButton.addEventListener('click', function() {
        var flowType = validateButton.getAttribute('flowType');
        validateCode(flowType);
    });

    function validateCode(flowType) {
        var verificationCode = document.getElementById('verificationCode').value;
        var ph = document.getElementById("phoneNumber").value
        fetch(`account/${flowType}/validate/otp`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                FlowType: flowType,
                OTP: verificationCode,
                PhoneNumber: ph
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.Status == "AUTHENTICATED") {
                console.log('authenticated user!');
                console.log(`FlowType = ${data.FlowType}`)
                if (data.FlowType == 'recover') {
                    window.location.href = "/account/recover";
                } else if (data.FlowType == 'create') {
                    console.log('dispatching auth event!');
                    document.dispatchEvent(authenticationEvent);
                }
            } else {
                console.log('user authentication failed');
                var verificationCodeField = document.getElementById("verificationCode");
                verificationCodeField.value = "";
                validateStatusMessage = document.getElementById("validateStatusMessage");
                validateStatusMessage.innerHTML = data.Message;
                validateStatusMessage.classList.remove("info");
                validateStatusMessage.classList.add("alert");
            }
        })
    }
});
