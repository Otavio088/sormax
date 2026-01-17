function menu() {
    let menu = document.getElementById('header-hamburger');
    let content = document.getElementById('aside');

    menu.classList.toggle('change')
    content.classList.toggle('content-show');
}