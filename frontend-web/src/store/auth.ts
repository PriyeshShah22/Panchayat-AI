import { create } from "zustand";
import { persist } from "zustand/middleware";
import { api } from "../api/client";

export interface AuthUser {
  id: number;
  email: string;
  full_name: string;
  is_superuser: boolean;
  society_id: number | null;
  roles: { id: number; name: string }[];
}

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: AuthUser | null;
  setTokens: (a: string, r: string) => void;
  setUser: (u: AuthUser | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      setTokens: (accessToken, refreshToken) => set({ accessToken, refreshToken }),
      setUser: (user) => set({ user }),
      logout: () => {
        set({ accessToken: null, refreshToken: null, user: null });
        try { api.post("/auth/logout-stub", {}); } catch { /* ignore */ }
      },
    }),
    { name: "smart-society-auth" }
  )
);
