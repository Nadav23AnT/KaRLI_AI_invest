import { Navigate, Outlet } from "react-router-dom"

export function PrivateRoute() {
	const auth = localStorage.getItem("isAuthenticated") === "true"
	return auth ? <Outlet /> : <Navigate to="/login" />;
}
