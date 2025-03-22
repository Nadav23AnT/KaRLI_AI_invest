import { useState } from "react";
import "./SignIn.css";
import { API_BASE_URL } from '../../enums';

export default function SignIn({ toggleForm, onSignInSuccess }: { toggleForm: () => void; onSignInSuccess: () => void }) {
    const [username, setUsername] = useState<string>("");
    const [password, setPassword] = useState<string>("");
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setError(null);

        const response = await fetch(`${API_BASE_URL}/signIn`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password }),
        });

        if (response.ok) {
            localStorage.setItem("isAuthenticated", "true");
            localStorage.setItem("username", username);
            onSignInSuccess();
        } else {
            setError("Username or password is incorrect");
        }
    };

    return (
        <div className="sign-in-container">
            <h2 className="title">Sign In</h2>
            {error && <p className="error-message">{error}</p>}
            <form onSubmit={handleSubmit} className="form">
                <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} className="input" required />
                <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} className="input" required />
                <button type="submit" className="button">Sign In</button>
            </form>
            <p className="toggle-link" onClick={toggleForm}>Don't have an account? Sign Up</p>
        </div>
    );
}