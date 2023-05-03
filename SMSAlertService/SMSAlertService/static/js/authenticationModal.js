document.addEventListener("DOMContentLoaded", async function() {

    var authenticationEvent = new CustomEvent("authenticationEvent");

    var modalHtmlResponse = await fetch("/modal/authenticate");
    var modalHtml = await modalHtmlResponse.text();

    var modalContainer = document.createElement("div");
    document.body.appendChild(modalContainer);
    modalContainer.innerHTML = modalHtml;

    var challengeModal = document.getElementById("challengeModal");
    var validateModal = document.getElementById("validateModal");

    var closeChallengeModalBtn = document.getElementById("closeChallengeButton");
    closeChallengeModalBtn.addEventListener("click", closeModal);

    var closeValidateModalBtn = document.getElementById("closeValidateButton");
    closeValidateModalBtn.addEventListener("click", closeModal);

    var overlay = document.createElement("div");
    overlay.addEventListener("click", closeModal);
    overlay.classList.add("overlay");


    // After Sign-Up Form is submitted + validated
    document.addEventListener("verifiedCredentialsEvent", function() {
        openChallengeModal('create')
    });

    // Reset Password Button Click (only exists on Login page)
    var resetPasswordButton = document.getElementById("resetPasswordButton");
    if (resetPasswordButton) {
        resetPasswordButton.addEventListener("click", function() {
            openChallengeModal('recover')
        });
    }

    function openChallengeModal(flowType) {
        // If signing up, prefill ph number in modal
        var phoneNumberInput = document.getElementById("phoneNumberInputField");
        if (phoneNumberInput) {
            var modalPhoneNumberInputField = document.getElementById("modalPhoneNumberInputField");
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

    function openValidateModal(flowType) {
        var validateButton = document.getElementById("validateButton");
        validateButton.setAttribute('flowType', flowType);
        challengeModal.style.display = "none";
        validateModal.style.display = "block";
    }

    function closeModal() {
        challengeModal.style.display = "none";
        validateModal.style.display = "none";
        document.body.removeChild(overlay);
    }

    // Send Code Button
    var sendCodeButton = document.getElementById("sendCodeButton");
    sendCodeButton.addEventListener("click", function() {
        var flowType = sendCodeButton.getAttribute('flowType');
        var ph = document.getElementById("modalPhoneNumberInputField").value;
        const regex = /^\d{10}$/;
        if (regex.test(ph)) {
            sendCode(flowType);
        } else {
            challengeStatusMessage = document.getElementById("challengeStatusMessage");
            challengeStatusMessage.innerHTML = "Please enter a valid 10 digit phone number.";
            challengeStatusMessage.classList.add("alert");
        }
    });

    function sendCode(flowType) {
        var ph = document.getElementById("modalPhoneNumberInputField").value;
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
        var ph = document.getElementById("modalPhoneNumberInputField").value;
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
        var verificationCodeField = document.getElementById("verificationCode");
        var verificationCode = verificationCodeField.value;
        var ph = document.getElementById("modalPhoneNumberInputField").value
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
                if (data.FlowType == 'recover') {
                    window.location.href = "/account/recover";
                } else if (data.FlowType == 'create') {
                    document.dispatchEvent(authenticationEvent);
                }
            } else {
                verificationCodeField.value = "";
                validateStatusMessage = document.getElementById("validateStatusMessage");
                validateStatusMessage.innerHTML = data.Message;
                validateStatusMessage.classList.remove("info").add("alert");
            }
        })
    }
});
