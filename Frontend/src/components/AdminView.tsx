import React, { useState } from 'react';
import { 
  Users, Bike, DollarSign, Activity, CheckCircle2, 
  Send 
} from 'lucide-react';

export const AdminView: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'kpis' | 'users' | 'bike_approvals' | 'notifications' | 'audit'>('kpis');
  
  const [users, setUsers] = useState([
    { id: 'u-1', name: 'John Owner', email: 'owner@example.com', role: 'owner', status: 'active', verified: true },
    { id: 'u-2', name: 'Alex Driver', email: 'driver@example.com', role: 'driver', status: 'active', verified: true },
    { id: 'u-3', name: 'Sam Pending', email: 'sam@example.com', role: 'driver', status: 'active', verified: false },
  ]);

  const [pendingBikes, setPendingBikes] = useState([
    { id: 'b-99', name: 'Yamaha R15 V4', reg: 'WB08EX1100', owner: 'John Owner', rent: 800, status: 'draft' },
  ]);

  const [broadcastMsg, setBroadcastMsg] = useState('');
  const [broadcastSent, setBroadcastSent] = useState(false);

  const toggleUserBlock = (userId: string) => {
    setUsers(users.map(u => u.id === userId ? { ...u, status: u.status === 'active' ? 'blocked' : 'active' } : u));
  };

  const approveBike = (bikeId: string) => {
    setPendingBikes(pendingBikes.filter(b => b.id !== bikeId));
  };

  const handleBroadcast = (e: React.FormEvent) => {
    e.preventDefault();
    if (!broadcastMsg) return;
    setBroadcastSent(true);
    setTimeout(() => {
      setBroadcastSent(false);
      setBroadcastMsg('');
    }, 2000);
  };

  return (
    <div className="space-y-6">
      
      {/* Executive Admin Header Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div className="glass-panel rounded-2xl p-4 flex items-center justify-between glow-cyan">
          <div>
            <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Gross Revenue</p>
            <p className="text-2xl font-black text-white mt-1">₹1,48,500</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
            <DollarSign className="w-5 h-5" />
          </div>
        </div>

        <div className="glass-panel rounded-2xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Platform Comm. (10%)</p>
            <p className="text-2xl font-black text-emerald-400 mt-1">₹14,850</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <Activity className="w-5 h-5" />
          </div>
        </div>

        <div className="glass-panel rounded-2xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Active Fleet</p>
            <p className="text-2xl font-black text-indigo-400 mt-1">42 Bikes</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <Bike className="w-5 h-5" />
          </div>
        </div>

        <div className="glass-panel rounded-2xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Total Users</p>
            <p className="text-2xl font-black text-purple-400 mt-1">128 Users</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400">
            <Users className="w-5 h-5" />
          </div>
        </div>

      </div>

      {/* Sub Tabs */}
      <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
        <button
          onClick={() => setActiveTab('kpis')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
            activeTab === 'kpis' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 glow-cyan' : 'text-slate-400 hover:text-white'
          }`}
        >
          Executive KPIs
        </button>

        <button
          onClick={() => setActiveTab('users')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
            activeTab === 'users' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 glow-cyan' : 'text-slate-400 hover:text-white'
          }`}
        >
          User Management ({users.length})
        </button>

        <button
          onClick={() => setActiveTab('bike_approvals')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
            activeTab === 'bike_approvals' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 glow-cyan' : 'text-slate-400 hover:text-white'
          }`}
        >
          Pending Bike Approvals ({pendingBikes.length})
        </button>

        <button
          onClick={() => setActiveTab('notifications')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
            activeTab === 'notifications' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 glow-cyan' : 'text-slate-400 hover:text-white'
          }`}
        >
          Broadcast Announcement
        </button>
      </div>

      {/* TAB 1: USERS TABLE */}
      {activeTab === 'users' && (
        <div className="glass-panel rounded-3xl p-6 space-y-4">
          <h3 className="text-base font-bold text-white">System User Accounts</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/80 text-slate-400 uppercase text-[10px]">
                <tr>
                  <th className="p-3">User Name</th>
                  <th className="p-3">Role</th>
                  <th className="p-3">KYC Verification</th>
                  <th className="p-3">Account Status</th>
                  <th className="p-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-900/40">
                    <td className="p-3">
                      <p className="font-bold text-white">{u.name}</p>
                      <p className="text-[10px] text-slate-400">{u.email}</p>
                    </td>
                    <td className="p-3 uppercase font-bold text-cyan-400">{u.role}</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        u.verified ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'
                      }`}>
                        {u.verified ? 'Verified' : 'Pending'}
                      </span>
                    </td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        u.status === 'active' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
                      }`}>
                        {u.status}
                      </span>
                    </td>
                    <td className="p-3 text-right">
                      <button
                        onClick={() => toggleUserBlock(u.id)}
                        className={`px-3 py-1 rounded-lg font-bold text-[10px] uppercase transition-all cursor-pointer ${
                          u.status === 'active'
                            ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20 hover:bg-rose-500/20'
                            : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20'
                        }`}
                      >
                        {u.status === 'active' ? 'Block User' : 'Unblock User'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 2: BIKE APPROVALS */}
      {activeTab === 'bike_approvals' && (
        <div className="glass-panel rounded-3xl p-6 space-y-4">
          <h3 className="text-base font-bold text-white">Pending Bike Verification Queue</h3>
          {pendingBikes.length === 0 ? (
            <p className="text-xs text-slate-400">All submitted bikes have been verified!</p>
          ) : (
            <div className="space-y-3">
              {pendingBikes.map((bike) => (
                <div key={bike.id} className="p-4 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between text-xs">
                  <div>
                    <p className="font-bold text-white">{bike.name} ({bike.reg})</p>
                    <p className="text-slate-400">Submitted by: {bike.owner} • Daily Rent: ₹{bike.rent}</p>
                  </div>
                  <button
                    onClick={() => approveBike(bike.id)}
                    className="px-4 py-2 rounded-xl bg-emerald-500 text-slate-950 font-bold text-xs hover:bg-emerald-400 transition-colors cursor-pointer"
                  >
                    Approve Listing & Publish
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 3: BROADCAST */}
      {activeTab === 'notifications' && (
        <form onSubmit={handleBroadcast} className="glass-panel rounded-3xl p-6 max-w-xl mx-auto space-y-4">
          <h3 className="text-base font-bold text-white">Send System-Wide Broadcast Notification</h3>
          <textarea
            value={broadcastMsg}
            onChange={(e) => setBroadcastMsg(e.target.value)}
            placeholder="Write announcement for all active Drivers & Owners..."
            className="w-full p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white h-24 focus:outline-none focus:border-cyan-500 resize-none"
          />
          {broadcastSent && (
            <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-400 flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <p>Broadcast notification delivered to all active users via Socket.IO & DB!</p>
            </div>
          )}
          <button
            type="submit"
            className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold text-xs uppercase tracking-wider shadow-lg shadow-cyan-500/25 cursor-pointer flex items-center justify-center space-x-2"
          >
            <Send className="w-4 h-4" />
            <span>Send Live Broadcast</span>
          </button>
        </form>
      )}

    </div>
  );
};
