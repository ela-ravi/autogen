"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import Cookies from "js-cookie";
import api from "./api";
import type { User, TokenResponse } from "./types";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
  setTokens: (tokens: TokenResponse) => void;
}

export const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  login: async () => {},
  signup: async () => {},
  logout: () => {},
  setTokens: () => {},
});

export function useAuthContext() {
  return useContext(AuthContext);
}

export function useAuthProvider() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const setTokens = useCallback((tokens: TokenResponse) => {
    Cookies.set("access_token", tokens.access_token, { expires: 1 });
    Cookies.set("refresh_token", tokens.refresh_token, { expires: 7 });
  }, []);

  const fetchUser = useCallback(async () => {
    try {
      const { data } = await api.get("/auth/me");
      setUser(data);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const token = Cookies.get("access_token");
    if (token) {
      fetchUser();
    } else {
      setLoading(false);
    }
  }, [fetchUser]);

  const login = async (email: string, password: string) => {
    const { data } = await api.post<TokenResponse>("/auth/login", {
      email,
      password,
    });
    setTokens(data);
    await fetchUser();
  };

  const signup = async (
    email: string,
    password: string,
    fullName: string
  ) => {
    const { data } = await api.post<TokenResponse>("/auth/signup", {
      email,
      password,
      full_name: fullName,
    });
    setTokens(data);
    await fetchUser();
  };

  const logout = () => {
    Cookies.remove("access_token");
    Cookies.remove("refresh_token");
    setUser(null);
  };

  return { user, loading, login, signup, logout, setTokens };
}
