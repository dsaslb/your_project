import React, { createContext, useContext, useEffect, useState } from "react";
import * as SecureStore from "expo-secure-store";
import { Platform } from "react-native";
import api from "../api/client";

// 웹과 네이티브 환경을 구분하여 토큰 저장/조회
const tokenStorage = {
  async getItem(key: string): Promise<string | null> {
    if (Platform.OS === 'web') {
      return localStorage.getItem(key);
    } else {
      return await SecureStore.getItemAsync(key);
    }
  },
  
  async setItem(key: string, value: string): Promise<void> {
    if (Platform.OS === 'web') {
      localStorage.setItem(key, value);
    } else {
      await SecureStore.setItemAsync(key, value);
    }
  },
  
  async removeItem(key: string): Promise<void> {
    if (Platform.OS === 'web') {
      localStorage.removeItem(key);
    } else {
      await SecureStore.deleteItemAsync(key);
    }
  }
};

type AuthValue = { 
  user: any|null; 
  login:(id:string,pw:string)=>Promise<void>; 
  logout:()=>Promise<void>; 
  loading:boolean; 
};

const AuthContext = createContext<AuthValue>({} as any);
export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<any|null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { 
    (async () => {
      const token = await tokenStorage.getItem("token");
      if (token) { 
        try { 
          const me = await api.get("/api/auth/me"); 
          setUser(me.data); 
        } catch {} 
      }
      setLoading(false);
    })(); 
  }, []);

  const login = async (id:string, pw:string) => {
    const r = await api.post("/api/auth/login", { username:id, password:pw });
    await tokenStorage.setItem("token", r.data?.access_token);
    const me = await api.get("/api/auth/me"); 
    setUser(me.data);
  };

  const logout = async () => { 
    await tokenStorage.removeItem("token"); 
    setUser(null); 
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}
