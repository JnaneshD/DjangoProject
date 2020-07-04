const usernameField = document.getElementById("usernameField");
const feedBackArea = document.querySelector('.invalid_feedback');
const emailField = document.getElementById('emailField');
const emailfeedBackArea = document.querySelector(".emailfeedBackArea");
const passwordField = document.getElementById("passwordField");
const usernameSuccessoutput = document.querySelector(".usernameSuccessoutput");
const showPasswordToggle = document.querySelector(".showPasswordToggle");
const submitBtn = document.querySelector(".submit-btn");
const handleToggleInput = (e) => {
    if (showPasswordToggle.textContent == "SHOW") {
        showPasswordToggle.textContent = "HIDE";
        passwordField.setAttribute("type", "text");
    } else {
        showPasswordToggle.textContent = "SHOW";
        passwordField.setAttribute("type", "password");
    }
};

showPasswordToggle.addEventListener("click", handleToggleInput);

emailField.addEventListener('keyup', (e) => {
    const emailVal = e.target.value;
    emailField.classList.remove("is-invalid");
    emailfeedBackArea.style.display = "none";
    if (emailVal.length > 0) {
        fetch('/authentication/validate-email', {
                body: JSON.stringify({ email: emailVal }),
                method: "POST",
            })
            .then(res => res.json())
            .then(data => {
                console.log('data', data);
                if (data.email_error) {
                    emailField.classList.add("is-invalid");
                    emailfeedBackArea.style.display = "block";
                    emailfeedBackArea.innerHTML = `<p>${data.email_error}</p>`;
                    submitBtn.setAttribute('disabled', 'disabled');

                    submitBtn.disabled = true;
                } else {
                    submitBtn.removeAttribute('disabled');
                }
            });
    }
});


usernameField.addEventListener('keyup', (e) => {
    const usernameValue = e.target.value;
    usernameSuccessoutput.style.display = 'block';

    usernameSuccessoutput.textContent = `Checking ${usernameValue}`;

    usernameField.classList.remove("is-invalid");
    feedBackArea.style.display = "none";
    if (usernameValue.length > 0) {
        fetch('/authentication/validate-username', {
                body: JSON.stringify({ username: usernameValue }),
                method: "POST",
            })
            .then(res => res.json())
            .then(data => {
                console.log('data', data);
                usernameSuccessoutput.style.display = 'none';
                if (data.username_error) {
                    usernameField.classList.add("is-invalid");
                    feedBackArea.style.display = "block";
                    feedBackArea.innerHTML = `<p>${data.username_error}</p>`;
                    submitBtn.disabled = true;
                } else {
                    submitBtn.removeAttribute("disabled");
                }
            });
    }

});