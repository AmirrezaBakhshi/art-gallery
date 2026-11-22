import { Navigate } from "react-router-dom";

export default function ProtectedRoute({ children }) {
  return localStorage.getItem("authToken") && localStorage.getItem("user") ? children : <Navigate to="/login" replace />;
}
