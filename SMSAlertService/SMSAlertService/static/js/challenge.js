document.addEventListener("DOMContentLoaded", async function() {

    // Modal Window
    var overlay = document.createElement("div");
    overlay.classList.add("overlay");

    var modalHtmlResponse = await fetch("/modal/challenge");
    var modalHtml = await modalHtmlResponse.text();

    var modalContainer = document.createElement("div");
    document.body.appendChild(modalContainer);
    modalContainer.innerHTML = modalHtml;

    var modal = document.querySelector(".modal");
    var openModalBtn = document.getElementById("resetPasswordButton");
    var closeBtn = document.querySelector(".close");

    openModalBtn.addEventListener("click", function() {
        console.log("button clicked")
        modal.style.display = "block";
        document.body.appendChild(overlay);
    });

    closeBtn.addEventListener("click", function() {
        modal.style.display = "none";
        document.body.removeChild(overlay);
    });

    window.addEventListener("click", function(event) {
        if (event.target == overlay) {
            modal.style.display = "none";
            document.body.removeChild(overlay);
        }
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
            var otp = data.OTP;
            var message = data.Message;
            console.log(`Status = ${status}`);
            console.log(`OTP = ${otp}`);
            console.log(`Message = ${message}`);
            if (status == "SUCCESS") {
                console.log('status was success. Present validate screen.')
            } else {
                statusMessage = document.getElementById("statusMessage");
                statusMessage.innerHTML = message
                statusMessage.classList.add("alert")
            }
        })
    };

    var sendCodeButton = document.getElementById("sendCodeButton");
    sendCodeButton.addEventListener("click", function() {
        sendCode();
    });

});
