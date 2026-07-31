import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import type { UserRole } from '../types';
import { Bike, Wallet, Bell, Shield, LogOut, ChevronDown, PlusCircle } from 'lucide-react';

interface NavbarProps {
  onOpenAuth: () => void;
  onOpenWallet: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenAuth, onOpenWallet }) => {
  const { user, currentRole, switchRole, walletBalance, logout } = useAuth();
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserDropdown, setShowUserDropdown] = useState(false);

  const notifications = [
    { id: 1, title: 'Wallet Recharged', time: '5m ago', desc: 'Successfully added INR 1,000 to wallet.' },
    { id: 2, title: 'Booking Approved', time: '1h ago', desc: 'Owner accepted your request for Yamaha FZ 25.' },
    { id: 3, title: 'Verification Completed', time: '1d ago', desc: 'Your driving license has been verified by Admin.' },
  ];

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Logo */}
        <div className="flex items-center space-x-3 cursor-pointer">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 via-indigo-500 to-purple-600 p-0.5 shadow-lg shadow-cyan-500/20">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Bike className="w-6 h-6 text-cyan-400" />
            </div>
          </div>
          <div>
            <span className="text-lg font-bold bg-gradient-to-r from-white via-slate-200 to-cyan-400 bg-clip-text text-transparent">
              VeloRent<span className="text-cyan-400">Pro</span>
            </span>
            <span className="hidden sm:inline-block ml-2 text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-semibold">
              Enterprise v2.0
            </span>
          </div>
        </div>

        {/* Role Switcher Pills */}
        <div className="hidden md:flex items-center p-1 bg-slate-900/90 rounded-xl border border-slate-800">
          {(['driver', 'owner', 'admin'] as UserRole[]).map((role) => (
            <button
              key={role}
              onClick={() => switchRole(role)}
              className={`px-4 py-1.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all duration-200 ${
                currentRole === role
                  ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md shadow-cyan-500/25 font-bold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              {role} Workspace
            </button>
          ))}
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-3">
          
          {/* Wallet Balance Pill */}
          <button
            onClick={onOpenWallet}
            className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-slate-900/80 border border-emerald-500/30 hover:border-emerald-500/60 transition-all duration-200 group glow-emerald cursor-pointer"
          >
            <div className="w-6 h-6 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400 group-hover:scale-110 transition-transform">
              <Wallet className="w-3.5 h-3.5" />
            </div>
            <div className="text-left">
              <p className="text-[10px] text-slate-400 leading-none">Wallet</p>
              <p className="text-xs font-bold text-emerald-400 leading-tight">
                ₹{walletBalance.toLocaleString('en-IN')}
              </p>
            </div>
            <PlusCircle className="w-3.5 h-3.5 text-emerald-400 opacity-60 group-hover:opacity-100 transition-opacity ml-1" />
          </button>

          {/* Notifications Bell */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="p-2 rounded-xl bg-slate-900/80 border border-slate-800 text-slate-300 hover:text-white hover:border-slate-700 transition-all relative"
            >
              <Bell className="w-4 h-4" />
              <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
              <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-cyan-400"></span>
            </button>

            {/* Notifications Dropdown */}
            {showNotifications && (
              <div className="absolute right-0 mt-3 w-80 glass-panel rounded-2xl p-4 shadow-2xl border border-slate-800 z-50 animate-in fade-in slide-in-from-top-2">
                <div className="flex items-center justify-between pb-2 border-b border-slate-800 mb-3">
                  <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider">Notifications</h4>
                  <span className="text-[10px] text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded-full font-semibold">3 Unread</span>
                </div>
                <div className="space-y-2.5">
                  {notifications.map((n) => (
                    <div key={n.id} className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800/60 hover:border-slate-700 transition-all cursor-pointer">
                      <div className="flex items-center justify-between mb-1">
                        <p className="text-xs font-semibold text-slate-200">{n.title}</p>
                        <span className="text-[10px] text-slate-500">{n.time}</span>
                      </div>
                      <p className="text-[11px] text-slate-400 leading-snug">{n.desc}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* User Profile */}
          {user ? (
            <div className="relative">
              <button
                onClick={() => setShowUserDropdown(!showUserDropdown)}
                className="flex items-center space-x-2 p-1.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition-all cursor-pointer"
              >
                <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center text-white text-xs font-bold">
                  {user.full_name.charAt(0)}
                </div>
                <span className="hidden sm:inline-block text-xs font-medium text-slate-200 max-w-[100px] truncate">
                  {user.full_name}
                </span>
                <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
              </button>

              {showUserDropdown && (
                <div className="absolute right-0 mt-3 w-56 glass-panel rounded-2xl p-2 shadow-2xl border border-slate-800 z-50">
                  <div className="px-3 py-2 border-b border-slate-800/80 mb-1">
                    <p className="text-xs font-bold text-white">{user.full_name}</p>
                    <p className="text-[10px] text-slate-400 truncate">{user.email}</p>
                    <div className="mt-1 flex items-center space-x-1">
                      <Shield className="w-3 h-3 text-cyan-400" />
                      <span className="text-[10px] uppercase font-bold text-cyan-400 tracking-wider">
                        {currentRole}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={logout}
                    className="w-full flex items-center space-x-2 px-3 py-2 rounded-xl text-xs font-medium text-rose-400 hover:bg-rose-500/10 transition-colors"
                  >
                    <LogOut className="w-4 h-4" />
                    <span>Log Out</span>
                  </button>
                </div>
              )}
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white text-xs font-bold shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 transition-all cursor-pointer"
            >
              Sign In
            </button>
          )}

        </div>

      </div>
    </header>
  );
};
