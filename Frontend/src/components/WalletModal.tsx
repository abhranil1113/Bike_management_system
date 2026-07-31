import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Wallet, ShieldCheck, X, CheckCircle2, AlertCircle } from 'lucide-react';

interface WalletModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const WalletModal: React.FC<WalletModalProps> = ({ isOpen, onClose }) => {
  const { walletBalance, updateWalletBalance } = useAuth();
  const [amount, setAmount] = useState<number>(1000);
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleRecharge = () => {
    setErrorMsg(null);
    setSuccessMsg(null);

    // Rule: Minimum wallet recharge = ₹500
    if (amount < 500) {
      setErrorMsg('Minimum wallet recharge amount is ₹500.');
      return;
    }

    setIsProcessing(true);

    // Simulate Razorpay payment signature & callback
    setTimeout(() => {
      const newBal = walletBalance + amount;
      updateWalletBalance(newBal);
      setIsProcessing(false);
      setSuccessMsg(`INR ${amount.toLocaleString('en-IN')} successfully credited to your wallet via Razorpay!`);
      setTimeout(() => {
        setSuccessMsg(null);
        onClose();
      }, 1800);
    }, 1200);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in">
      <div className="relative w-full max-w-md glass-panel rounded-3xl p-6 border border-slate-800 shadow-2xl glow-emerald">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800/80 mb-5">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Wallet className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Recharge Wallet</h3>
              <p className="text-xs text-slate-400">Razorpay Payment Integration</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Current Balance */}
        <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 mb-5 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Available Balance</p>
            <p className="text-2xl font-black text-emerald-400 mt-0.5">
              ₹{walletBalance.toLocaleString('en-IN')}
            </p>
          </div>
          <div className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-bold uppercase tracking-wider">
            Active Ledger
          </div>
        </div>

        {/* Minimum Rule Note */}
        <div className="mb-4 flex items-center space-x-2 text-xs text-amber-400 bg-amber-500/10 border border-amber-500/20 p-3 rounded-xl">
          <ShieldCheck className="w-4 h-4 shrink-0 text-amber-400" />
          <p>Rule: Minimum single recharge requirement is <span className="font-bold">₹500</span>.</p>
        </div>

        {/* Amount Input */}
        <div className="space-y-3 mb-6">
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
            Select or Enter Amount (INR)
          </label>

          {/* Quick Buttons */}
          <div className="grid grid-cols-4 gap-2">
            {[500, 1000, 2500, 5000].map((preset) => (
              <button
                key={preset}
                type="button"
                onClick={() => {
                  setAmount(preset);
                  setErrorMsg(null);
                }}
                className={`py-2 rounded-xl text-xs font-bold transition-all border ${
                  amount === preset
                    ? 'bg-emerald-500 text-slate-950 border-emerald-400 shadow-md shadow-emerald-500/20'
                    : 'bg-slate-900 text-slate-300 border-slate-800 hover:border-slate-700'
                }`}
              >
                ₹{preset}
              </button>
            ))}
          </div>

          <div className="relative mt-2">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 font-bold text-sm">
              ₹
            </span>
            <input
              type="number"
              min="500"
              value={amount}
              onChange={(e) => {
                setAmount(Number(e.target.value));
                setErrorMsg(null);
              }}
              className="w-full pl-8 pr-4 py-3 rounded-xl bg-slate-900 border border-slate-800 text-white font-bold focus:outline-none focus:border-emerald-500 transition-colors text-base"
              placeholder="500"
            />
          </div>
        </div>

        {/* Status Alerts */}
        {errorMsg && (
          <div className="mb-4 flex items-center space-x-2 text-xs text-rose-400 bg-rose-500/10 border border-rose-500/20 p-3 rounded-xl">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <p>{errorMsg}</p>
          </div>
        )}

        {successMsg && (
          <div className="mb-4 flex items-center space-x-2 text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 p-3 rounded-xl animate-in zoom-in-95">
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
            <p>{successMsg}</p>
          </div>
        )}

        {/* Razorpay Pay CTA */}
        <button
          onClick={handleRecharge}
          disabled={isProcessing}
          className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-600 text-slate-950 font-black text-sm uppercase tracking-wider shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40 transition-all disabled:opacity-50 flex items-center justify-center space-x-2 cursor-pointer"
        >
          {isProcessing ? (
            <>
              <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></div>
              <span>Connecting Razorpay Gateway...</span>
            </>
          ) : (
            <span>Pay & Credit ₹{amount.toLocaleString('en-IN')}</span>
          )}
        </button>

      </div>
    </div>
  );
};
