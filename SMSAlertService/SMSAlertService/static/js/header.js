document.addEventListener("DOMContentLoaded", function() {

    var overlay = document.createElement("div");
    overlay.classList.add("overlay");
    overlay.addEventListener("click", closeMobileMenu);

    const header = document.querySelector('header');
    const openMobileMenuIcon = document.getElementById('openMobileMenuIcon');
    const closeMobileMenuIcon = document.getElementById('closeMobileMenuIcon');
    const mobileMenu = document.getElementById('mobileMenu');

    openMobileMenuIcon.addEventListener('click', openMobileMenu);
    closeMobileMenuIcon.addEventListener('click', closeMobileMenu);

    function openMobileMenu() {
        console.log('open menu');
        mobileMenu.classList.add('open');
        addOverlay();
    }

    function closeMobileMenu() {
        console.log('close menu');
        mobileMenu.classList.remove('open');
        removeOverlay();
    }

    function addOverlay() {
        document.body.appendChild(overlay);
        // Fake header overlay because z-index doesn't work with the css position
        header.style.backgroundColor = '#666666';
    }

    function removeOverlay() {
        document.body.removeChild(overlay);
        header.style.backgroundColor = 'white';
    }
});