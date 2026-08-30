import React, { createContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { authApi } from '@/api/authApi';
import { User, LoginInput, PatientRegisterInput, DoctorRegisterInput } from '@/types';

export interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginInput) => Promise<User>;
  registerPatient: (data: PatientRegisterInput) => Promise<User>;
  registerDoctor: (data: DoctorRegisterInput) => Promise<User>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_STORAGE_KEY = 'verticare_token';

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_STORAGE_KEY));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Restore authenticated session on initial application load
  useEffect(() => {
    async function restoreSession() {
      const storedToken = localStorage.getItem(TOKEN_STORAGE_KEY);
      if (storedToken) {
        try {
          const currentUser = await authApi.getMe();
          setUser(currentUser);
          setToken(storedToken);
        } catch (error) {
          console.warn('Session token expired or invalid, logging out.');
          localStorage.removeItem(TOKEN_STORAGE_KEY);
          setUser(null);
          setToken(null);
        }
      }
      setIsLoading(false);
    }
    restoreSession();
  }, []);

  const login = useCallback(async (credentials: LoginInput): Promise<User> => {
    const authData = await authApi.login(credentials);
    const receivedToken = authData.access_token;
    const authenticatedUser = authData.user;

    localStorage.setItem(TOKEN_STORAGE_KEY, receivedToken);
    setToken(receivedToken);
    setUser(authenticatedUser);
    return authenticatedUser;
  }, []);

  const registerPatient = useCallback(async (data: PatientRegisterInput): Promise<User> => {
    const createdUser = await authApi.registerPatient(data);
    return createdUser;
  }, []);

  const registerDoctor = useCallback(async (data: DoctorRegisterInput): Promise<User> => {
    const createdUser = await authApi.registerDoctor(data);
    return createdUser;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    setToken(null);
    setUser(null);
    window.location.href = '/login';
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        isLoading,
        login,
        registerPatient,
        registerDoctor,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

