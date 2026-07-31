import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { DriverView } from './components/DriverView';
import { OwnerView } from './components/OwnerView';
import { AdminView } from './components/AdminView';
import { WalletModal } from './components/WalletModal';
import { AuthModal } from './components/AuthModal';

const MainLayout: React.FC = () => {
  const { currentRole } = useAuth();
  const [isWalletOpen, setIsWalletOpen] = useState(false);
  const [isAuthOpen, setIsAuthOpen] = useState(false);

  return (
    <div className="min-h-screen flex flex-col justify-between">
      
      <div>
        <Navbar
          onOpenAuth={() => setIsAuthOpen(true)}
          onOpenWallet={() => setIsWalletOpen(true)}
        />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          
          {/* Active Workspace Banner */}
          <div className="mb-6 flex items-center justify-between p-4 rounded-2xl glass-panel border border-slate-800">
            <div>
              <h2 className="text-xl font-black text-white capitalize flex items-center space-x-2">
                <span>{currentRole} Workspace</span>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-bold uppercase tracking-wider">
                  Live Mode
                </span>
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                {currentRole === 'driver' && 'Search verified bikes, recharge wallet, and manage active rentals.'}
                {currentRole === 'owner' && 'Manage bike fleet listings, review booking requests, and inspect returns.'}
                {currentRole === 'admin' && 'Monitor platform revenue KPIs, approve bike listings, and manage user accounts.'}
              </p>
            </div>
          </div>

          {/* Role Views */}
          {currentRole === 'driver' && <DriverView onOpenWallet={() => setIsWalletOpen(true)} />}
          {currentRole === 'owner' && <OwnerView />}
          {currentRole === 'admin' && <AdminView />}

        </main>
      </div>

      {/* Footer */}
      <footer className="glass-panel border-t border-slate-800/80 py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-400">
          <p>© 2026 VeloRent Pro — Full Stack Bike Rental & Fleet Management System.</p>
          <div className="flex items-center space-x-4">
            <span className="flex items-center space-x-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>FastAPI Backend Active (Port 8000)</span>
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
