function toggleEdit() {
    const form = document.getElementById('personal-form');
    const isReadonly = form.classList.contains('readonly');
    const inputs = form.querySelectorAll('input, textarea, select');
    const saveBtn = form.querySelector('.btn');

    inputs.forEach(el => {
        if (el.id !== 'profile-pic') {
            el.readOnly = isReadonly ? false : true;
        }

        if (el.tagName === 'SELECT' || el.id === 'profile-pic') {
            el.disabled = !el.disabled;
        }

        el.style.backgroundColor = isReadonly ? 'white' : 'transparent';
        el.style.border = isReadonly ? '1px solid #ccc' : 'none';
    });

    saveBtn.style.display = isReadonly ? 'inline-block' : 'none';
    form.classList.toggle('readonly');
}
document.addEventListener("DOMContentLoaded", () => {
    const message = document.querySelector("p");
    const form = document.getElementById("personal-form");
    const inputs = form.querySelectorAll("input, textarea, select");
    const saveBtn = form.querySelector('.btn');

    if (message && !form.classList.contains("readonly")) {
        inputs.forEach(el => {
            if (el.id !== 'profile-pic') {
                el.readOnly = true;
            }

            if (el.tagName === 'SELECT' || el.id === 'profile-pic') {
                el.disabled = true;
            }

            el.style.backgroundColor = 'transparent';
            el.style.border = 'none';
        });

        saveBtn.style.display = 'none';
        form.classList.add("readonly");
    }
});