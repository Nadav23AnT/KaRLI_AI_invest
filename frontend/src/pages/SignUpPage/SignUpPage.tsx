import { z } from "zod"

import { SignupForm } from "@/components/signup-form"
import { signupFormSchema } from "@/schemas/signup-form-schema"


function SignUpPage() {
    const handleSubmit = (values: z.infer<typeof signupFormSchema>) => {
        console.log(values)
    }

    return (
        <div className="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
            <div className="w-full max-w-sm">
                <SignupForm onSumbit={handleSubmit} />
            </div>
        </div>
    )
}

export default SignUpPage
