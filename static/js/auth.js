// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js";
import {
    getAuth,
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    signOut,
    onAuthStateChanged
} from "https://www.gstatic.com/firebasejs/9.6.1/firebase-auth.js";

// ✅ Firebase Configuration
const firebaseConfig = {
    apiKey: "AIzaSyDu1vfZOceK6RSBzJqmJZqeFuuqL9Z4A60",
    authDomain: "cropguardauth.firebaseapp.com",
    projectId: "cropguardauth",
    storageBucket: "cropguardauth.firebasestorage.app",
    messagingSenderId: "591988252857",
    appId: "1:591988252857:web:cfdb69638542203774bb68"
};

// ✅ Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

document.addEventListener("DOMContentLoaded", function () {

    // ✅ Helper for messages
    const styleMessage = (element, message, type = "error") => {
        element.textContent = message;
        element.style.color = type === "success" ? "green" : "red";
        element.style.fontWeight = "bold";
    };

    // ✅ Register Handler
    const registerButton = document.getElementById("registerButton");
    if (registerButton) {
        registerButton.addEventListener("click", async () => {
            const email = document.getElementById("register-email").value;
            const password = document.getElementById("register-password").value;
            const message = document.getElementById("registerMessage");

            if (!email || !password) {
                styleMessage(message, "❌ Please enter both email and password!");
                return;
            }

            try {
                await createUserWithEmailAndPassword(auth, email, password);
                styleMessage(message, "✅ Registered successfully! Redirecting to login...", "success");

                setTimeout(() => {
                    window.location.href = "/login";
                }, 2000);
            } catch (error) {
                styleMessage(message, `❌ Error: ${error.message}`);
                console.error("Registration Error:", error);
            }
        });
    }

    // ✅ Login Handler
    const loginButton = document.getElementById("loginButton");
    if (loginButton) {
        loginButton.addEventListener("click", async () => {
            const email = document.getElementById("login-email").value;
            const password = document.getElementById("login-password").value;
            const message = document.getElementById("loginMessage");

            if (!email || !password) {
                styleMessage(message, "❌ Please enter both email and password!");
                return;
            }

            try {
                const userCredential = await signInWithEmailAndPassword(auth, email, password);
                const user = userCredential.user;

                styleMessage(message, "✅ Logged in successfully! Redirecting...", "success");
                sessionStorage.setItem("user", JSON.stringify(user));

                setTimeout(() => {
                    window.location.href = "/dashboard";  // Redirect to dashboard now
                }, 2000);
            } catch (error) {
                styleMessage(message, `❌ Error: ${error.message}`);
                console.error("Login Error:", error);
            }
        });
    }

    // ✅ Session Control and Logout
    onAuthStateChanged(auth, (user) => {
        const logoutButton = document.getElementById("logoutButton");
        const userEmailDisplay = document.getElementById("userEmail");
        const userWrapper = document.getElementById("userWrapper");

        const protectedPages = ["/", "/index.html", "/dashboard"];

        if (!user && protectedPages.includes(window.location.pathname)) {
            console.log("🔒 No user found, redirecting to login...");
            window.location.href = "/login";
        }

        if (user) {
            console.log("✅ User logged in:", user.email);

            if (userEmailDisplay) userEmailDisplay.innerText = `Logged in as: ${user.email}`;
            if (userWrapper) userWrapper.style.display = "flex";

            if (logoutButton) {
                logoutButton.addEventListener("click", async () => {
                    try {
                        await signOut(auth);
                        sessionStorage.removeItem("user");
                        alert("✅ Logged out successfully!");
                        window.location.href = "/login";
                    } catch (error) {
                        console.error("Logout Error:", error);
                        alert("❌ Logout failed: " + error.message);
                    }
                });
            }
        }
    });
});
