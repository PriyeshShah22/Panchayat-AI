import { create } from "zustand";
import { persist } from "zustand/middleware";

interface ThemeState {
  mode: "light" | "dark";
  toggle: () => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      mode: "light",
      toggle: () => set((s) => ({ mode: s.mode === "light" ? "dark" : "light" })),
    }),
    { name: "smart-society-theme" }
  )
);
