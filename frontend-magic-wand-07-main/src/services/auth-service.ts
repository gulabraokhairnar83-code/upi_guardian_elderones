/**
 * UPI Guardian - Authentication Service
 * Manages JWT session tokens, login, registration, and user profile retrieval.
 */

import { apiClient, isMockEnabled, setAuthToken, clearAuthToken, getAuthToken } from "./api-client";

export interface UserSession {
  id: string;
  user_id?: string | undefined;
  name: string;
  email: string;
  phone?: string | undefined;
  role: "ELDER" | "CAREGIVER" | "elder" | "caregiver" | "demo";
  avatar: string;
  accountSafetyStatus?: string | undefined;
}

export interface AuthResponse {
  success: boolean;
  user: UserSession;
  access_token?: string;
  refresh_token?: string;
  token_type?: string;
  message?: string;
}

const mockSession: UserSession = {
  id: "usr_sunita_68",
  user_id: "usr_sunita_68",
  name: "Sunita Devi",
  email: "sunita.devi@example.com",
  phone: "+91 98765 43210",
  role: "ELDER",
  avatar: "SD",
  accountSafetyStatus: "Protected",
};

export const authService = {
  async login(credentials: { email: string; password: string }): Promise<UserSession> {
    if (isMockEnabled()) {
      setAuthToken("mock_access_token_demo", "mock_refresh_token_demo");
      return mockSession;
    }

    const res = await apiClient.post<AuthResponse>("/auth/login", credentials);
    if (res.access_token) {
      setAuthToken(res.access_token, res.refresh_token);
    }
    const user = res.user;
    return {
      ...user,
      id: user.user_id || user.id || "usr_ramesh_001",
      avatar: user.name ? user.name.slice(0, 2).toUpperCase() : "UG",
    };
  },

  async register(data: {
    name: string;
    email: string;
    password: string;
    phone?: string;
    role?: "ELDER" | "CAREGIVER";
  }): Promise<UserSession> {
    if (isMockEnabled()) {
      setAuthToken("mock_access_token_demo", "mock_refresh_token_demo");
      return {
        id: "usr_new_demo",
        user_id: "usr_new_demo",
        name: data.name,
        email: data.email,
        phone: data.phone,
        role: data.role || "ELDER",
        avatar: data.name.slice(0, 2).toUpperCase(),
        accountSafetyStatus: "Protected",
      };
    }

    const res = await apiClient.post<AuthResponse>("/auth/register", data);
    if (res.access_token) {
      setAuthToken(res.access_token, res.refresh_token);
    }
    const user = res.user;
    return {
      ...user,
      id: user.user_id || user.id || "usr_ramesh_001",
      avatar: user.name ? user.name.slice(0, 2).toUpperCase() : "UG",
    };
  },

  async getCurrentUser(): Promise<UserSession> {
    if (isMockEnabled()) {
      return mockSession;
    }

    const token = getAuthToken();
    if (!token) {
      // Fallback for seamless demo if not logged in
      return mockSession;
    }

    try {
      const res = await apiClient.get<{ success: boolean; user: UserSession }>("/auth/me");
      const user = res.user;
      return {
        ...user,
        id: user.user_id || user.id || "usr_ramesh_001",
        avatar: user.name ? user.name.slice(0, 2).toUpperCase() : "UG",
      };
    } catch {
      return mockSession;
    }
  },

  async logout(): Promise<void> {
    if (!isMockEnabled() && getAuthToken()) {
      try {
        await apiClient.post("/auth/logout");
      } catch {
        // Continue clearing local token even if network fails
      }
    }
    clearAuthToken();
  },
};
