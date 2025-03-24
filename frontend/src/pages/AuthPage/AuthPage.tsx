import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import SignUp from "../../components/SignUp/SignUp";
import SignIn from "../../components/SignIn/SignIn";
import "./AuthPage.css";

export default function AuthPage() {
    const [isSignUp, setIsSignUp] = useState<boolean>(true);
    const navigate = useNavigate();

    useEffect(() => {
        const isAuthenticated = localStorage.getItem("isAuthenticated");
        if (isAuthenticated === "true") {
            navigate("/home"); // Redirect if already logged in
        }
    }, [navigate]);

    const handleSignInSuccess = () => {
        navigate("/home");
    };

    return isSignUp ? (
        <SignUp toggleForm={() => setIsSignUp(false)} onSignUpSuccess={handleSignInSuccess} />
    ) : (
        <SignIn toggleForm={() => setIsSignUp(true)} onSignInSuccess={handleSignInSuccess} />
    );
}
