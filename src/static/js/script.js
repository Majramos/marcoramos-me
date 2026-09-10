const navMenu = document.getElementById('nav-menu');
const toggle = navMenu.querySelector('.toggle');
const dropdown = navMenu.querySelector('.dropdown');

toggle.addEventListener('click', (e) => {
    e.stopPropagation();
    const isOpen = !dropdown.hidden;
    dropdown.hidden = isOpen;
    toggle.setAttribute('aria-expanded', String(!isOpen));
});

document.addEventListener('click', (e) => {
    if (!navMenu.contains(e.target)) {
        dropdown.hidden = true;
        toggle.setAttribute('aria-expanded', 'false');
    }
});

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        dropdown.hidden = true;
        toggle.setAttribute('aria-expanded', 'false');
    }
});
