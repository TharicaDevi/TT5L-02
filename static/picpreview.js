document.getElementById('profile-picture-input').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const preview = document.getElementById('profile-picture-preview');
        preview.src = URL.createObjectURL(file);
    }
});