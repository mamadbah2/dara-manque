import { useState, useCallback } from "react";
import { login as apiLogin } from "../api/client";

type Role = "doctor" | "pharmacist";

export function useAuth() {
  const [role, setRole] = useState<Role | null>(
    localStorage.getItem("role") as Role | null
  );

  const signIn = useCallback(async (email: string, password: string): Promise<Role> => {
    const res = await apiLogin(email, password);
    localStorage.setItem("token", res.data.access_token);
    localStorage.setItem("role", res.data.role);
    localStorage.setItem("email", email);
    setRole(res.data.role);
    return res.data.role;
  }, []);

  const signOut = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    localStorage.removeItem("email");
    setRole(null);
  }, []);

  return { role, signIn, signOut };
}
