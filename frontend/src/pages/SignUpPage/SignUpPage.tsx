import { z } from "zod"

import { SignupForm } from "@/components/signup-form"
import { signupFormSchema } from "@/schemas/signup-form-schema"
import { useNavigate } from "react-router-dom"


function SignUpPage() {
    const navigate = useNavigate()
    const handleSubmit = async (values: z.infer<typeof signupFormSchema>) => {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/signUp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: values.username,
          password: values.password,
          age: values.age,
          brokerApiKey: values.brokerApiKey,
          brokerApiSecret: values.brokerApiSecret,
        }),
      });
  
      if (response.ok) {
        localStorage.setItem("isAuthenticated", "true");
        localStorage.setItem("username", values.username);
        navigate("/")
      } else {
        alert("An error occurred. We couldn't sign you up right now. Please try again later.")
      }
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
