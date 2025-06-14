// Toggle edit for account form
function toggleAccountEdit() {
    const form = document.getElementById('account-form');
    const isReadonly = form.classList.contains('readonly');
    const inputs = form.querySelectorAll('input');

    inputs.forEach(input => {
        if (input.name !== 'username') {
            input.readOnly = isReadonly ? false : true;
            input.style.backgroundColor = isReadonly ? 'white' : 'transparent';
            input.style.border = isReadonly ? '1px solid #ccc' : 'none';
        }
    });

    const saveBtn = form.querySelector('.btn');
    saveBtn.style.display = isReadonly ? 'inline-block' : 'none';

    form.classList.toggle('readonly');
}

// Toggle edit for personal form
function togglePersonalEdit() {
    const form = document.getElementById('personal-form');
    const isReadonly = form.classList.contains('readonly');
    const inputs = form.querySelectorAll('input, textarea, select');
    const saveBtn = form.querySelector('.btn');

    inputs.forEach(el => {
        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
            el.readOnly = !isReadonly;
        }

        if (el.tagName === 'SELECT') {
            el.disabled = isReadonly ? false : true;
        }
    });

    saveBtn.style.display = isReadonly ? 'inline-block' : 'none';
    form.classList.toggle('readonly');
}

// Toggle edit for contact form
function toggleContactEdit() {
    const form = document.getElementById('contact-form');
    const isReadonly = form.classList.contains('readonly');
    const inputs = form.querySelectorAll('textarea');
    const saveBtn = form.querySelector('.btn');

    inputs.forEach(textarea => {
        textarea.readOnly = !isReadonly;
        textarea.style.backgroundColor = isReadonly ? 'white' : 'transparent';
        textarea.style.border = isReadonly ? '1px solid #ccc' : 'none';
    });

    saveBtn.style.display = isReadonly ? 'inline-block' : 'none';
    form.classList.toggle('readonly');
}

// Toggle edit for privacy form
function togglePrivacyEdit() {
    const form = document.getElementById('privacy-form');
    const isReadonly = form.classList.contains('readonly');
    const selects = form.querySelectorAll('select');
    const saveBtn = form.querySelector('.btn');

    selects.forEach(el => {
        (el.tagName === 'SELECT') {
            el.disabled = isReadonly ? false : true;
        }
    });

    saveBtn.style.display = isReadonly ? 'inline-block' : 'none';
    form.classList.toggle('readonly');
}

// Delete account confirmation
function confirmDelete() {
  return confirm("Are you sure you want to permanently delete your account?");
}

document.addEventListener("DOMContentLoaded", () => {
    // For account form
    const accountMessage = document.querySelector("#account-form + p");
    if (accountMessage) {
        const form = document.getElementById("account-form");
        const inputs = form.querySelectorAll("input");

        inputs.forEach(input => {
            input.readOnly = true;
            input.style.backgroundColor = 'transparent';
            input.style.border = 'none';
        });

        form.classList.add("readonly");
        const saveBtn = form.querySelector('.btn');
        saveBtn.style.display = 'none';
    }

    // For personal form
    const personalMessage = document.querySelector("#personal-form + p");
    const personalForm = document.getElementById("personal-form");
    if (personalMessage && personalForm && !personalForm.classList.contains("readonly")) {
        const inputs = personalForm.querySelectorAll("input, textarea, select");
        
        inputs.forEach(el => {
            el.style.backgroundColor = 'transparent';
            el.style.border = 'none';
        });

        const saveBtn = personalForm.querySelector('.btn');
        saveBtn.style.display = 'none';
        personalForm.classList.add("readonly");
    }

    // For contact form
    const contactMessage = document.querySelector("#contact-form + p");
    const contactForm = document.getElementById("contact-form");
    if (contactMessage && contactForm && !contactForm.classList.contains("readonly")) {
        const inputs = contactForm.querySelectorAll("textarea");
        
        inputs.forEach(textarea => {
            textarea.readOnly = true;
            textarea.style.backgroundColor = 'transparent';
            textarea.style.border = 'none';
        });

        const saveBtn = contactForm.querySelector('.btn');
        saveBtn.style.display = 'none';
        contactForm.classList.add("readonly");
    }

    // For privacy form
    const privacyMessage = document.querySelector("privacy-form");
    const privacyForm = document.getElementById("privacy-form");
    if (privacyMessage && privacyForm && !privacyForm.classList.contains("readonly")) {
        const selects = privacyForm.querySelectorAll("select");
        
        selects.forEach(el => {
            el.style.backgroundColor = 'transparent';
            el.style.border = 'none';
        });

        const saveBtn = personalForm.querySelector('.btn');
        saveBtn.style.display = 'none';
        personalForm.classList.add("readonly");
    }
});