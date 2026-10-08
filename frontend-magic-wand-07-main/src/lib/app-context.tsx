import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

type AppContextValue = {
  dark: boolean;
  senior: boolean;
  reducedMotion: boolean;
  toggleDark: () => void;
  toggleSenior: () => void;
  setReducedMotion: (value: boolean) => void;
};

const AppContext = createContext<AppContextValue | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [dark, setDark] = useState(false);
  const [senior, setSenior] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    document.documentElement.classList.toggle("senior", senior);
    document.documentElement.classList.toggle("reduce-motion", reducedMotion);
  }, [dark, senior, reducedMotion]);

  return <AppContext.Provider value={{ dark, senior, reducedMotion, toggleDark: () => setDark((v) => !v), toggleSenior: () => setSenior((v) => !v), setReducedMotion }}>{children}</AppContext.Provider>;
}

export function useApp() {
  const value = useContext(AppContext);
  if (!value) throw new Error("useApp must be used inside AppProvider");
  return value;
}