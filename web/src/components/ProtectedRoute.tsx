import type { ReactElement } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

interface Props {
  children: ReactElement;
  allowedRole: "doctor" | "pharmacist";
}

export default function ProtectedRoute({ children, allowedRole }: Props) {
  const { role } = useAuth();
  if (!role) return <Navigate to="/login" replace />;
  if (role !== allowedRole) return <Navigate to={`/${role}`} replace />;
  return children;
}
