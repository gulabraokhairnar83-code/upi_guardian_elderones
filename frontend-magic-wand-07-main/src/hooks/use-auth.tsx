/**
 * UPI Guardian - Authentication Hook and Provider
 */

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { authService, type UserSession } from "@/services/auth-service";

interface AuthContextType {
  user: UserSession | null;
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;
  login: (credentials: { email: string; password: string }) => Promise<UserSession>;
  register: (data: {
    name: string;
    email: string;
    password: string;
    phone?: string;
    role?: "ELDER" | "CAREGIVER";
  }) => Promise<UserSession>;
  logout: () => Promise<void>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserSession | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    authService
      .getCurrentUser()
      .then((curr) => {
        if (mounted) {
          setUser(curr);
          setLoading(false);
        }
      })
      .catch(() => {
        if (mounted) {
          setLoading(false);
        }
      });
    return () => {
      mounted = false;
    };
  }, []);

  const login = async (credentials: { email: string; password: string }) => {
    setError(null);
    setLoading(true);
    try {
      const loggedIn = await authService.login(credentials);
      setUser(loggedIn);
      return loggedIn;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Authentication failed.";
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const register = async (data: {
    name: string;
    email: string;
    password: string;
    phone?: string;
    role?: "ELDER" | "CAREGIVER";
  }) => {
    setError(null);
    setLoading(true);
    try {
      const created = await authService.register(data);
      setUser(created);
      return created;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Registration failed.";
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
  };

  const clearError = () => setError(null);

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        error,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}
