import { createContext, useContext, useMemo, useState } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("nexus_token"));

  const value = useMemo(
    () => ({
      token,
      isAuthenticated: Boolean(token),
      signIn: (newToken) => {
        localStorage.setItem("nexus_token", newToken);
        setToken(newToken);
      },
      signOut: () => {
        localStorage.removeItem("nexus_token");
        setToken(null);
      },
    }),
    [token]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
