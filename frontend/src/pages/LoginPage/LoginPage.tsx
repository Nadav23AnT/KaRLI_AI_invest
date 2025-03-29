import { z } from "zod"

import { LoginForm } from "@/components/login-form"
import { loginFormSchema } from "@/schemas/login-form-schema"

import { useNavigate } from "react-router-dom"
import { useState } from "react"


function LoginPage() {
    const navigate = useNavigate()
    const [error, setError] = useState<{ type: string, message: string }>()

    const handleSubmit = async (values: z.infer<typeof loginFormSchema>) => {
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/signIn`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                username: values.username,
                password: values.password
            }),
        });

        if (response.ok) {
            localStorage.setItem("isAuthenticated", "true");
            localStorage.setItem("username", values.username);
            navigate("/")
        } else {
            setError({
                type: "incorrect login",
                message: "Username or password is incorrect."
            });
        }
    }

    return (
        <div className="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
            <div className="w-full max-w-md">
                <LoginForm error={error} onSumbit={handleSubmit} />
            </div>
        </div>
    )
}

export default LoginPage
