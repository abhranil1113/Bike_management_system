import React, { createContext, useContext, useState } from 'react';
import type { User, UserRole } from '../types';

interface AuthContextType {
  user: User | null;
  token: string | null;
  currentRole: UserRole;
  walletBalance: number;
  login: (token: string, user: User) => void;
  logout: () => void;
  switchRole: (role: UserRole) => void;
  updateWalletBalance: (newBalance: number) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('user_data');
    return saved ? JSON.parse(saved) : {
      id: 'demo-user-1',
      full_name: 'Alex Driver',
      email: 'alex.driver@example.com',
      phone: '9876543210',
      role: 'driver',
      is_active: true,
      is_verified: true,
      wallet_balance: 2500,
    };
  });

  const [token, setToken] = useState<string | null>(() => localStorage.getItem('access_token'));
  const [currentRole, setCurrentRole] = useState<UserRole>(user?.role || 'driver');
  const [walletBalance, setWalletBalance] = useState<number>(user?.wallet_balance ?? 2500);

  const login = (newToken: string, newUser: User) => {
    setToken(newToken);
    setUser(newUser);
    setCurrentRole(newUser.role);
    setWalletBalance(newUser.wallet_balance ?? 0);
    localStorage.setItem('access_token', newToken);
    localStorage.setItem('user_data', JSON.stringify(newUser));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_data');
  };

  const switchRole = (role: UserRole) => {
    setCurrentRole(role);
    if (user) {
      const updated = { ...user, role };
      setUser(updated);
      localStorage.setItem('user_data', JSON.stringify(updated));
    }
  };

  const updateWalletBalance = (newBalance: number) => {
    setWalletBalance(newBalance);
    if (user) {
      const updated = { ...user, wallet_balance: newBalance };
      setUser(updated);
      localStorage.setItem('user_data', JSON.stringify(updated));
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, currentRole, walletBalance, login, logout, switchRole, updateWalletBalance }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
