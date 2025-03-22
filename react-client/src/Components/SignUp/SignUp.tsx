import { useState, useEffect } from "react";
import "./SignUp.css";
import { API_BASE_URL } from '../../enums';

interface RiskResponse {
    risks: string[];
}

interface SignUpProps {
    toggleForm: () => void;
    onSignUpSuccess: () => void; // ✅ Add the onSignUpSuccess callback
}

export default function SignUp({ toggleForm, onSignUpSuccess }: SignUpProps) {
    const [username, setUsername] = useState<string>("");
    const [password, setPassword] = useState<string>("");
    const [age, setAge] = useState<string>("");
    const [risk, setRisk] = useState<string>("");
    const [risks, setRisks] = useState<string[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    useEffect(() => {
        fetch(`${API_BASE_URL}/risks`)
            .then((res) => res.json())
            .then((data: RiskResponse) => setRisks(data.risks))
            .catch((err) => console.error("Error fetching risks:", err));
    }, []);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);

        const response = await fetch(`${API_BASE_URL}/signUp`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password, age, risk }),
        });

        const data = await response.json();

        if (response.ok) {
            setSuccess("User registered successfully!");
            localStorage.setItem("isAuthenticated", "true");
            localStorage.setItem("username", username);
            onSignUpSuccess();
        } else {
            setError(data.error || "Registration failed");
        }
    };

    return (
        <div className="sign-up-container">
            <h2 className="title">Sign Up</h2>
            {error && <p className="error-message">{error}</p>}
            {success && <p className="success-message">{success}</p>}
            <form onSubmit={handleSubmit} className="form">
                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="input"
                    required
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="input"
                    required
                />
                <input
                    type="number"
                    placeholder="Age"
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                    className="input"
                    required
                />
                <select
                    value={risk}
                    onChange={(e) => setRisk(e.target.value)}
                    className="input"
                    required
                >
                    <option value="">Select Risk Level</option>
                    {risks.map((r, index) => (
                        <option key={index} value={r}>
                            {r}
                        </option>
                    ))}
                </select>
                <button type="submit" className="button">Sign Up</button>
            </form>
            <p className="toggle-link" onClick={toggleForm}>
                Already have an account? Sign In
            </p>
        </div>
    );
}
