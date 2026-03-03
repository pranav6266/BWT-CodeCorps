import { Clerk } from '@clerk/clerk-js';
import { initThreeJS } from './three-scene.js';

// 1. Initialize 3D Background
initThreeJS();

// 2. Initialize Clerk Authentication
const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;
const clerk = new Clerk(clerkPubKey);

async function initClerk() {
    await clerk.load();

    const authContainer = document.getElementById('auth-container');
    const getStartedBtn = document.getElementById('get-started-btn');

    if (clerk.user) {
        // User is logged in
        clerk.mountUserButton(authContainer);
        getStartedBtn.style.display = 'block';

        getStartedBtn.addEventListener('click', () => {
            // Logic to switch to your dashboard view
            alert("Redirecting to the financial dashboard...");
            // window.location.href = '/dashboard.html';
        });
    } else {
        // User is not logged in
        const signInButton = document.createElement('button');
        signInButton.textContent = 'Sign In';
        signInButton.className = 'cta-button';
        signInButton.style.padding = '0.5rem 1.5rem';
        signInButton.style.fontSize = '0.9rem';

        signInButton.addEventListener('click', () => {
            clerk.openSignIn();
        });

        authContainer.appendChild(signInButton);
    }
}

initClerk().catch(console.error);