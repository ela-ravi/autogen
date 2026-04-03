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
import type { User, TokenResponse, SignupResponse } from "./types";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, fullName: string) => Promise<SignupResponse>;
  verifyOtp: (email: string, code: string) => Promise<void>;
  resendOtp: (email: string) => Promise<void>;
  googleLogin: (credential: string) => Promise<TokenResponse>;
  logout: () => void;
  setTokens: (tokens: TokenResponse) => void;
}

export const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  login: async () => {},
  signup: async () => ({ message: "", email: "", requires_verification: true }),
  verifyOtp: async () => {},
  resendOtp: async () => {},
  googleLogin: async () => ({} as TokenResponse),
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
  ): Promise<SignupResponse> => {
    const { data } = await api.post<SignupResponse>("/auth/signup", {
      email,
      password,
      full_name: fullName,
    });
    return data;
  };

  const verifyOtp = async (email: string, code: string) => {
    const { data } = await api.post<TokenResponse>("/auth/verify-otp", {
      email,
      code,
    });
    setTokens(data);
    await fetchUser();
  };

  const resendOtp = async (email: string) => {
    await api.post("/auth/resend-otp", { email });
  };

  const googleLogin = async (credential: string): Promise<TokenResponse> => {
    const { data } = await api.post<TokenResponse>("/auth/google", {
      token: credential,
    });
    setTokens(data);
    await fetchUser();
    return data;
  };

  const logout = () => {
    Cookies.remove("access_token");
    Cookies.remove("refresh_token");
    setUser(null);
  };

  return { user, loading, login, signup, verifyOtp, resendOtp, googleLogin, logout, setTokens };
}
