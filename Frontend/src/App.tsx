import React from 'react';
import { Bike, ShieldCheck, Key, ExternalLink, ArrowRight, Zap, CheckCircle2, ChevronRight, Activity, Wallet } from 'lucide-react';

export function App() {
  return (
    <div className="min-h-screen bg-[#f4f8f6] text-slate-800 flex flex-col justify-between font-sans">

      {/* Top Banner */}
      <header className="border-b border-slate-200/80 bg-white/80 backdrop-blur-md sticky top-0 z-20">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center text-emerald-800 font-bold shadow-xs">
              <Bike className="w-5 h-5 text-emerald-700" />
            </div>
            <div>
              <span className="text-base font-bold text-slate-900 tracking-tight">VeloRent</span>
              <span className="text-[10px] px-2 py-0.5 ml-2 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 font-bold uppercase tracking-wider">
                Multi-Port System
              </span>
            </div>
          </div>
          <div className="flex items-center space-x-2 text-xs font-semibold text-emerald-800">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>FastAPI Backend Ready (Port 8000)</span>
          </div>
        </div>
      </header>

      {/* Hero Greeting & Port Selector */}
      <main className="max-w-6xl mx-auto px-6 py-10 flex-1 w-full space-y-8">

        {/* Hero Greeting Banner matching the screenshot */}
        <div className="bg-gradient-to-r from-[#0d5940] via-[#0e6b4e] to-[#0a4a35] text-white rounded-3xl p-8 shadow-sm relative overflow-hidden">
          <div className="absolute right-0 top-0 bottom-0 w-80 bg-white/5 rounded-l-full pointer-events-none"></div>

          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <p className="text-[11px] font-bold tracking-wider text-emerald-200/90 uppercase">
                {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
              </p>
              <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight mt-1 text-white">
                VeloRent Workspace Hub
              </h1>
              <p className="text-xs md:text-sm text-emerald-100/90 mt-1">
                Each portal runs independently on its designated port with customized workflows and permissions.
              </p>

              <div className="flex items-center gap-2 mt-4">
                <span className="px-3 py-1 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full text-xs font-semibold text-white">
                  3 Portals Architecture
                </span>
                <span className="px-3 py-1 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full text-xs font-medium text-emerald-100">
                  Driver, Owner & Admin Operations
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className="px-4 py-2 bg-white/15 backdrop-blur-sm border border-white/20 rounded-full text-xs font-semibold text-white flex items-center gap-2">
                <Activity className="w-3.5 h-3.5" />
                <span>All Services Operational</span>
              </span>
            </div>
          </div>
        </div>

        {/* 3 Dedicated Portal Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

          {/* 1. Driver Portal */}
          <div className="bg-white border border-slate-200/80 rounded-2xl p-6 shadow-xs hover:shadow-md transition-all flex flex-col justify-between space-y-6 group">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center font-bold">
                  <Bike className="w-5 h-5" />
                </div>
                <span className="text-xs font-mono font-bold px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">
                  PORT 3110
                </span>
              </div>

              <div>
                <h3 className="text-base font-bold text-slate-900">Driver Portal</h3>
                <p className="text-xs text-emerald-700 font-semibold mt-0.5">Scooty Rental & Renter Operations</p>
                <p className="text-xs text-slate-500 mt-2 leading-relaxed">
                  Browse scooties, upload driving license & Aadhaar, recharge wallet (₹500 min policy), book with deposit locks, and request return inspections.
                </p>
              </div>

              <div className="space-y-1.5 text-xs text-slate-600 font-medium pt-2 border-t border-slate-100">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  <span>Wallet recharge (Razorpay min ₹500)</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  <span>Active rental duration tracker</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  <span>Single active rental limit enforcement</span>
                </div>
              </div>
            </div>

            <a
              href="http://localhost:3110"
              target="_blank"
              rel="noreferrer"
              className="w-full py-2.5 px-4 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-xs flex items-center justify-center space-x-2 transition shadow-xs group-hover:translate-y-[-1px]"
            >
              <span>Launch Driver Portal</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>

          {/* 2. Owner Portal */}
          <div className="bg-white border border-slate-200/80 rounded-2xl p-6 shadow-xs hover:shadow-md transition-all flex flex-col justify-between space-y-6 group">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center font-bold">
                  <Key className="w-5 h-5" />
                </div>
                <span className="text-xs font-mono font-bold px-2.5 py-1 rounded-full bg-blue-50 text-blue-800 border border-blue-200">
                  PORT 6782
                </span>
              </div>

              <div>
                <h3 className="text-base font-bold text-slate-900">Fleet Owner Portal</h3>
                <p className="text-xs text-blue-700 font-semibold mt-0.5">Scooty Owners & Fleet Managers</p>
                <p className="text-xs text-slate-500 mt-2 leading-relaxed">
                  List scooties with RC documents and deposit pricing, accept/reject booking requests, conduct return inspections, record damages, and refund deposits.
                </p>
              </div>

              <div className="space-y-1.5 text-xs text-slate-600 font-medium pt-2 border-t border-slate-100">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                  <span>List scooties with RC & deposit</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                  <span>Booking request queue (Accept/Reject)</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                  <span>Vehicle inspection & damage refund dialog</span>
                </div>
              </div>
            </div>

            <a
              href="http://localhost:6782"
              target="_blank"
              rel="noreferrer"
              className="w-full py-2.5 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs flex items-center justify-center space-x-2 transition shadow-xs group-hover:translate-y-[-1px]"
            >
              <span>Launch Owner Portal</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>

          {/* 3. Admin Portal */}
          <div className="bg-white border border-slate-200/80 rounded-2xl p-6 shadow-xs hover:shadow-md transition-all flex flex-col justify-between space-y-6 group">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-700 flex items-center justify-center font-bold">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <span className="text-xs font-mono font-bold px-2.5 py-1 rounded-full bg-purple-50 text-purple-800 border border-purple-200">
                  PORT 5431
                </span>
              </div>

              <div>
                <h3 className="text-base font-bold text-slate-900">Admin Governance Portal</h3>
                <p className="text-xs text-purple-700 font-semibold mt-0.5">Executive & Verification Oversight</p>
                <p className="text-xs text-slate-500 mt-2 leading-relaxed">
                  Verify driver DL/Aadhaar documents, approve owner bank accounts & scooty RC listings, track gross revenue and 10% platform cuts, and moderate users.
                </p>
              </div>

              <div className="space-y-1.5 text-xs text-slate-600 font-medium pt-2 border-t border-slate-100">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-purple-600 shrink-0" />
                  <span>Driver & Owner KYC verification queues</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-purple-600 shrink-0" />
                  <span>Scooty RC and pricing approval</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-purple-600 shrink-0" />
                  <span>10% commission tracking & broadcast alerts</span>
                </div>
              </div>
            </div>

            <a
              href="http://localhost:5431"
              target="_blank"
              rel="noreferrer"
              className="w-full py-2.5 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs flex items-center justify-center space-x-2 transition shadow-xs group-hover:translate-y-[-1px]"
            >
              <span>Launch Admin Portal</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>

        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200/80 bg-white py-4 text-center text-xs text-slate-500">
        <p>VeloRent Enterprise Scooty & Bike Rental Architecture • Multi-Port Separation (Ports 3110, 6782, 5431)</p>
      </footer>
    </div>
  );
}
