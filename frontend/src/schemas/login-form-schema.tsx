import { z } from "zod"

export const loginFormSchema = z.object({
  username: z.string().min(1, {
    message: "Username required.",
  }),
  password: z.string().min(1, {
    message: "Password required.",
  }),
})
