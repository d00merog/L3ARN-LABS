import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../utils/api';
import { useRouter } from 'next/router';
import { useSession, signIn, signOut } from 'next-auth/react';

interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { data: session, status } = useSession();

  useEffect(() => {
    const checkAuthStatus = async () => {
      if (status === 'authenticated' && session?.user?.email) {
        try {
          const response = await api.get('/users/me');
          setUser(response.data);
        } catch (err) {
          console.error('Error fetching user data:', err);
          setError('Session expired. Please log in again.');
        }
      }
      setIsLoading(false);
    };

    checkAuthStatus();
  }, [status, session]);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await signIn('credentials', {
        redirect: false,
        email,
        password,
      });
      if (result?.error) {
        setError(result.error);
      } else {
        const response = await api.get('/users/me');
        setUser(response.data);
        router.push('/dashboard');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError('Invalid email or password. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await signOut({ redirect: false });
      setUser(null);
      router.push('/');
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isLoading, error }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
