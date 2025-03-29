import { ThemeProvider } from "@/components/theme-provider"
import { Routes, Route } from "react-router-dom";
import DashboardPage from "./pages/DashboardPage/DashboardPage";
import SignUpPage from "./pages/SignUpPage/SignUpPage";
import LoginPage from "./pages/LoginPage/LoginPage";
import { PrivateRoute } from "./components/private-route";

export default function App() {
    return (
        <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
            <Routes>
                <Route path='/' element={<PrivateRoute/>}>
                    <Route path='/' element={<DashboardPage/>}/>
                </Route>
                <Route path="/signup" element={<SignUpPage />} />
                <Route path="/login" element={<LoginPage />} />
            </Routes>
        </ThemeProvider>
    );
}