document.addEventListener("DOMContentLoaded", async function() {

    const overlay = document.createElement('div');
    overlay.classList.add('overlay');

    const modalHtmlResponse = await fetch('/modal/challenge');
    const modalHtml = await modalHtmlResponse.text();

    const modalContainer = document.createElement('div');
    document.body.appendChild(modalContainer);
    modalContainer.innerHTML = modalHtml;

    const modal = document.querySelector('.modal');
    const openModalBtn = document.getElementById('resetPasswordButton');
    const closeBtn = document.querySelector('.close');

    openModalBtn.addEventListener('click', function() {
        console.log('button clicked')
        modal.style.display = "block";
        document.body.appendChild(overlay);
    });

    closeBtn.addEventListener('click', function() {
        modal.style.display = "none";
        document.body.removeChild(overlay);
    });

    window.addEventListener('click', function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
            document.body.removeChild(overlay);
        }
    });

});
