document.addEventListener('DOMContentLoaded', () => {

    // Password Toggle
    document.querySelectorAll('.toggle-password').forEach(btn => {
        btn.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input');
            const icon = this.querySelector('i');
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.replace('fa-eye', 'fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.replace('fa-eye-slash', 'fa-eye');
            }
        });
    });

    // Password Strength Meter
    const pwdInput = document.getElementById('password');
    if (pwdInput) {
        const bar = document.getElementById('strength-bar');
        const text = document.getElementById('strength-text');

        pwdInput.addEventListener('input', () => {
            const val = pwdInput.value;
            let strength = 0;
            if (val.length >= 8) strength++;
            if (/[A-Z]/.test(val)) strength++;
            if (/[0-9]/.test(val)) strength++;
            if (/[^A-Za-z0-9]/.test(val)) strength++;

            bar.style.width = (strength * 25) + '%';

            if (strength <= 1) {
                bar.style.background = '#ff6b6b';
                text.textContent = 'Weak';
            } else if (strength === 2) {
                bar.style.background = '#ffa726';
                text.textContent = 'Medium';
            } else {
                bar.style.background = '#4ade80';
                text.textContent = 'Strong';
            }
        });
    }
});