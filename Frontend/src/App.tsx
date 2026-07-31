import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { DriverView } from './components/DriverView';
import { OwnerView } from './components/OwnerView';
import { AdminView } from './components/AdminView';
import { WalletModal } from './components/WalletModal';
import { AuthModal } from './components/AuthModal';
import { Car, Key, ShieldCheck, Sparkles } from 'lucide-react';

const MainLayout: React.FC = () => {
  const { currentRole, switchRole } = useAuth();
  const [isWalletOpen, setIsWalletOpen] = useState(false);
  const [isAuthOpen, setIsAuthOpen] = useState(false);

  return (
    <div className="min-h-screen flex flex-col justify-between">
      
      <div>
        <Navbar
          onOpenAuth={() => setIsAuthOpen(true)}
          onOpenWallet={() => setIsWalletOpen(true)}
        />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
          
          {/* Prominent Role Workspace Switcher Bar */}
          <div className="glass-panel rounded-3xl p-4 sm:p-6 border border-cyan-500/20 glow-cyan">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-5">
              <div>
                <h2 className="text-xl font-black text-white flex items-center space-x-2">
                  <span>Bike Management System</span>
                  <span className="text-xs px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-bold uppercase tracking-wider flex items-center space-x-1">
                    <Sparkles className="w-3 h-3" />
                    <span>3 Workspaces Active</span>
                  </span>
                </h2>
                <p className="text-xs text-slate-400 mt-1">
                  Click any workspace tab below to view and test the <b>Driver</b>, <b>Owner</b>, or <b>Admin</b> panels live.
                </p>
              </div>
            </div>

            {/* Big Interactive Role Workspace Selector Tabs */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              
              {/* Driver Tab */}
              <button
                onClick={() => switchRole('driver')}
                className={`p-4 rounded-2xl border text-left transition-all duration-200 cursor-pointer flex items-center space-x-3 ${
                  currentRole === 'driver'
                    ? 'bg-gradient-to-r from-cyan-500/20 to-blue-600/20 border-cyan-400 text-white shadow-lg shadow-cyan-500/15 glow-cyan'
                    : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-white'
                }`}
              >
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold shrink-0 ${
                  currentRole === 'driver' ? 'bg-cyan-500 text-slate-950' : 'bg-slate-800 text-slate-400'
                }`}>
                  <Car className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-cyan-400">Driver Portal</p>
                  <p className="text-sm font-black text-white">Search & Rent Bikes</p>
                  <p className="text-[10px] text-slate-400 mt-0.5">Wallet top-up & booking rules</p>
                </div>
              </button>

              {/* Owner Tab */}
              <button
                onClick={() => switchRole('owner')}
                className={`p-4 rounded-2xl border text-left transition-all duration-200 cursor-pointer flex items-center space-x-3 ${
                  currentRole === 'owner'
                    ? 'bg-gradient-to-r from-emerald-500/20 to-teal-600/20 border-emerald-400 text-white shadow-lg shadow-emerald-500/15 glow-emerald'
                    : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-white'
                }`}
              >
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold shrink-0 ${
                  currentRole === 'owner' ? 'bg-emerald-500 text-slate-950' : 'bg-slate-800 text-slate-400'
                }`}>
                  <Key className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-emerald-400">Owner Portal</p>
                  <p className="text-sm font-black text-white">Fleet & Bookings</p>
                  <p className="text-[10px] text-slate-400 mt-0.5">Add bikes & return inspection</p>
                </div>
              </button>

              {/* Admin Tab */}
              <button
                onClick={() => switchRole('admin')}
                className={`p-4 rounded-2xl border text-left transition-all duration-200 cursor-pointer flex items-center space-x-3 ${
                  currentRole === 'admin'
                    ? 'bg-gradient-to-r from-purple-500/20 to-indigo-600/20 border-purple-400 text-white shadow-lg shadow-purple-500/15'
                    : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-white'
                }`}
              >
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold shrink-0 ${
                  currentRole === 'admin' ? 'bg-purple-500 text-white' : 'bg-slate-800 text-slate-400'
                }`}>
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-purple-400">Admin Panel</p>
                  <p className="text-sm font-black text-white">Executive Control</p>
                  <p className="text-[10px] text-slate-400 mt-0.5">KPIs, users & approvals</p>
                </div>
              </button>

            </div>
          </div>

          {/* Active Workspace Container */}
          <div className="space-y-6">
            {currentRole === 'driver' && <DriverView onOpenWallet={() => setIsWalletOpen(true)} />}
            {currentRole === 'owner' && <OwnerView />}
            {currentRole === 'admin' && <AdminView />}
          </div>

        </main>
      </div>

      {/* Footer */}
      <footer className="glass-panel border-t border-slate-800/80 py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-400">
          <p>© 2026 VeloRent Pro — Full Stack Bike Rental & Fleet Management System.</p>
          <div className="flex items-center space-x-4">
            <span className="flex items-center space-x-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>FastAPI Backend Connected (Port 8000)</span>
            </span>
          </div>
        </div>
      </footer>

      {/* Modals */}
      <WalletModal isOpen={isWalletOpen} onClose={() => setIsWalletOpen(false)} />
      <AuthModal isOpen={isAuthOpen} onClose={() => setIsAuthOpen(false)} />

    </div>
  );
};

export function App() {
  return (
    <AuthProvider>
      <MainLayout />
    </AuthProvider>
  );
}

export default App;
