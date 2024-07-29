document.addEventListener("DOMContentLoaded", async function() {

    var modalHtmlResponse = await fetch("/modal/paypal");
    var modalHtml = await modalHtmlResponse.text();

    var modalContainer = document.createElement("div");
    document.body.appendChild(modalContainer);
    modalContainer.innerHTML = modalHtml;

    var paypalModal = document.getElementById("paypalModal");

    const paypalModalOpenedEvent = new CustomEvent("paypalModalOpenedEvent");

    var openPaypalModalButton = document.getElementById('openPaypalModalButton');
    openPaypalModalButton.addEventListener("click", openPaypalModal);

    var closePaypalModalButton = document.getElementById('closePaypalModalButton');
    closePaypalModalButton.addEventListener('click', closePaypalModal);

    var overlay = document.createElement("div");
    overlay.classList.add("overlay");
    overlay.addEventListener("click", closePaypalModal);

    function openPaypalModal() {
        paypalModal.style.display = 'block';
        document.body.appendChild(overlay);
        window.dispatchEvent(paypalModalOpenedEvent);
    }

    function closePaypalModal() {
        paypalModal.style.display = 'none';
        document.body.removeChild(overlay);
    }
});


