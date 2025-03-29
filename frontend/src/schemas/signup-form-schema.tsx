import { z } from "zod"

export const signupFormSchema = z.object({
  username: z.string().min(2, {
    message: "Username must be at least 2 characters.",
  }),
  password: z.string().min(8, {
    message: "Password must be at least 8 characters.",
  }),
  confirm: z.string(),
  age: z.coerce.number({
    required_error: "Age is required.",
    invalid_type_error: "Age must be a number.",
  }).gte(18, {
    message: "Must be 18+ years old.",
  }),
  risk: z.string({
    required_error: "Please select risk level."
  })
}).refine((data) => data.password === data.confirm, {
  message: "Passwords don't match.",
  path: ["confirm"],
});
