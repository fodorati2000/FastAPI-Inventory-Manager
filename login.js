async function login() {
    const usern = document.getElementById("log_username");
    const pwd = document.getElementById("log_password");

    const formData = new FormData();
    formData.append("username", usern.value);
    formData.append("password", pwd.value);  
    
    try {
        const response = await fetch('http://127.0.0.1:8000/login', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok && result.status === "Success") { 
            sessionStorage.setItem("isLoggedIn", "true");
            sessionStorage.setItem("currentUser", result.user);

            await Swal.fire("Siker!", "Sikeres bejelentkezés", "success"); 
            window.location.href = "index.html"; 
            
        } else {
            Swal.fire("Hiba!", result.message || "Hibás adatok", "error");
        }
    } catch (error) {
        Swal.fire("Hiba!", "Nem sikerült elérni a szervert", "error");
    }
}

async function register() {
    const usern = document.getElementById("reg_username");
    const pwd = document.getElementById("reg_password");
    const pwd2 = document.getElementById("reg_password2");
    if(pwd.value != pwd2.value){Swal.fire("Hiba!", result.message || "jelszavak nem egyeznek", "error");}else{
        const formData = new FormData();
        formData.append("username", usern.value);
        formData.append("password", pwd.value); 
        
        try {
            const response = await fetch('http://127.0.0.1:8000/register', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok && result.status === "Success") {    
                await Swal.fire("Siker!", "Sikeres regisztáltá r", "success"); 
                view("login-panel");
            } else {
                Swal.fire("Hiba!", result.message || "Hibás adatok", "error");
            }
        } catch (error) {
            Swal.fire("Hiba!", "Nem sikerült elérni a szervert", "error");
        }
    }
}

function view(containerId){
    const containers = ["reg-panel", "login-panel"];
    containers.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = (id === containerId) ? "flex" : "none";
    });
}