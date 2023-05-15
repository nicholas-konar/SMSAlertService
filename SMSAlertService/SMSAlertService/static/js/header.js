document.addEventListener("DOMContentLoaded", function() {

    const openMobileMenuIcon = document.getElementById('openMobileMenuIcon');
    const closeMobileMenuIcon = document.getElementById('closeMobileMenuIcon');
    const mobileMenu = document.getElementById('mobileMenu');

    openMobileMenuIcon.addEventListener('click', openMobileMenu);
    closeMobileMenuIcon.addEventListener('click', closeMobileMenu);

    function openMobileMenu() {
        console.log('open menu');
        mobileMenu.classList.add('open');
    }

    function closeMobileMenu() {
        console.log('close menu');
        mobileMenu.classList.remove('open');
    }
});