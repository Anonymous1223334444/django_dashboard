const usernameField = document.querySelector("#usernameField");
const emailField = document.querySelector("#emailField");
const passwordField = document.querySelector("#passwordField");
const UsernameFeedback = document.querySelector(".username-feedback");
const UsernameSuccess = document.querySelector(".usernameSuccessOutput");
const EmailFeedback = document.querySelector(".email-feedback");
const EmailSuccess = document.querySelector(".emailSuccessOutput");
const showPassToggle = document.querySelector(".showPass");
const submitBTN = document.querySelector(".submit-btn");    

const handleToggleInput = (e) => {
    if (showPassToggle.textContent === 'SHOW') {
        showPassToggle.textContent = 'HIDE';
        passwordField.setAttribute("type", "text");
    } else {
        showPassToggle.textContent = 'SHOW';
        passwordField.setAttribute("type", "password");
    }
}

showPassToggle.addEventListener('click', handleToggleInput)

emailField.addEventListener('keyup', (e) => {
    const emailValue = e.target.value;
    EmailSuccess.textContent = `Checking ${emailValue}`

    EmailFeedback.classList.remove("is-invalid");
    EmailFeedback.style.display = "none";

    if (emailValue.length > 0) {
        fetch("/authentication/validate-email", {
            method: "POST",
            body: JSON.stringify({
                email: emailValue 
            }),
        })
        .then((res) => res.json())
        .then((data) => {
            console.log(data);
            EmailSuccess.style.display = "block";
            if(data.Email_error) {
                // submitBTN.disabled = true;  
                emailField.classList.add("is-invalid");
                EmailFeedback.style.display = "block";
                EmailFeedback.innerHTML = `<p>${data.Email_error}</p>`;
            } else {
                // submitBTN.removeAttribute('disabled');
            }
        });
    }
});

usernameField.addEventListener('keyup', (e) => {
    const usernameValue = e.target.value;
    UsernameSuccess.textContent = `Checking ${usernameValue}`

    submitBTN.removeAttribute('disabled');
    usernameField.classList.remove("is-invalid");
    UsernameFeedback.style.display = "none";

    if (usernameValue.length > 0) {
        fetch("/authentication/validate-username", {
            method: "POST",
            body: JSON.stringify({
                username: usernameValue 
            }),
        })
        .then((res) => res.json())
        .then((data) => {
            console.log(data);
            UsernameSuccess.style.display = "block";
            if(data.Username_error) {
                submitBTN.disabled = true;
                usernameField.classList.add("is-invalid");
                UsernameFeedback.style.display = "block";
                UsernameFeedback.innerHTML = `<p>${data.Username_error}</p>`;
            } else {
                submitBTN.removeAttribute('disabled');
            }
        });
    }
}); 