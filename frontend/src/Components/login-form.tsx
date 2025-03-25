import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { ChartNoAxesCombined } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"

import { loginFormSchema } from "@/schemas/login-form-schema"

export function LoginForm({
  error,
  onSumbit,
  ...props
}: {
  error: { type: string, message: string } | undefined,
  onSumbit: (values: z.infer<typeof loginFormSchema>) => void
}) {
  const form = useForm<z.infer<typeof loginFormSchema>>({
    resolver: zodResolver(loginFormSchema),
    defaultValues: {
      username: "",
      password: "",
    },
    errors: error
    ? {
        password: error
      }
    : {},
  })

  return (
    <div className={cn("flex flex-col gap-6")} {...props}>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSumbit)} className="space-y-8">
          <div className="flex flex-col gap-6">
            <div className="flex flex-col items-center gap-2">
              <div className="flex size-8 items-center justify-center rounded-md">
                <ChartNoAxesCombined className="size-6" />
              </div>
              <span className="sr-only">KaRLI AI Investing</span>
              <h1 className="text-xl font-bold">Welcome to KaRLI AI Investing</h1>
              <div className="text-center text-sm">
                Don&apos;t have an account?{" "}
                <a href="signup" className="underline underline-offset-4">
                  Sign up
                </a>
              </div>
            </div>
              <FormField
                control={form.control}
                name="username"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Username</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Password</FormLabel>
                    <FormControl>
                      <Input type="password" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit">Log in</Button>
          </div>
        </form>
        <div className="text-muted-foreground *:[a]:hover:text-primary text-center text-xs text-balance *:[a]:underline *:[a]:underline-offset-4">
        © KaRLI AI Invest (<a href="https://github.com/Nadav23AnT/KaRLI_AI_invest/" target="_blank">GitHub</a>)
        </div>
      </Form>
    </div>
  )
}
