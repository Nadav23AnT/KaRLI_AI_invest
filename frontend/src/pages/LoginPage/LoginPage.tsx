import { z } from "zod"

import { LoginForm } from "@/components/login-form"
import { loginFormSchema } from "@/schemas/login-form-schema"

function LoginPage() {
    const handleSubmit = (values: z.infer<typeof loginFormSchema>) => {
        console.log(values)
    }

    return (
        <div className="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
            <div className="w-full max-w-md">
                <LoginForm onSumbit={handleSubmit} />
            </div>
        </div>
    )
}

export default LoginPage
