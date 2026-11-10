import React, { useState, useEffect } from 'react';
import {
  ShieldCheck, Users, Bike as BikeIcon, DollarSign,
  AlertCircle, AlertTriangle, CheckCircle2, XCircle, Search, Filter,
  Send, FileText, ChevronRight, RefreshCw, Bell, LogOut,
  User as UserIcon, Lock, Unlock, Eye, HelpCircle, Activity,
  ChevronDown, Building, CreditCard, Radio, Mail, ArrowRight, EyeOff,
  ExternalLink, Image as ImageIcon, Phone, MapPin, Check, Camera
} from 'lucide-react';
import { apiClient, getBackendBaseUrl, getPortalUrl } from '../../shared/api';
import type { AdminStats, User, Bike, NotificationItem, CodEscalationItem } from '../../shared/types';

interface DriverItem {
  user_id: string;
  email: string;
  phone?: string;
  full_name: string;
  address?: string;
  driving_license_number?: string;
  driving_license_file?: string;
  aadhaar_number?: string;
  aadhaar_file?: string;
  pan_number?: string;
  pan_file?: string;
  profile_picture?: string;
  emergency_contact?: {
    name?: string;
    phone?: string;
  };
  verification_status: 'verified' | 'pending' | 'rejected' | string;
  rejection_reason?: string;
  is_active: boolean;
}

interface OwnerItem {
  user_id: string;
  email: string;
  business_name?: string;
  full_name?: string;
  phone?: string;
  bank_account_number?: string;
  bank_ifsc?: string;
  verification_status: 'verified' | 'pending' | 'rejected' | string;
  is_active: boolean;
}

export default function AdminApp() {
  // Authentication & session state
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('access_token'));
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('admin_user');
    return saved ? JSON.parse(saved) : null;
  });

  // Auth form state
  const [authEmail, setAuthEmail] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);

  // Navigation tab
  const [activeTab, setActiveTab] = useState<'dashboard' | 'drivers' | 'owners' | 'bikes' | 'users' | 'broadcast' | 'audit' | 'cod_escalations'>('dashboard');

  // Real Database state (No hardcoded demo values)
  const [stats, setStats] = useState<AdminStats>({
    total_users: 0,
    active_drivers: 0,
    active_owners: 0,
    total_bikes: 0,
    active_rentals: 0,
    gross_revenue: 0,
    platform_commission: 0,
    cod_unpaid_count: 0,
    cod_escalations_count: 0
  });
  const [loadingStats, setLoadingStats] = useState(false);

  // COD Escalations list (> 10h uncollected cash)
  const [codEscalations, setCodEscalations] = useState<CodEscalationItem[]>([]);
  const [loadingEscalations, setLoadingEscalations] = useState(false);

  // Verification lists from database
  const [drivers, setDrivers] = useState<DriverItem[]>([]);
  const [loadingDrivers, setLoadingDrivers] = useState(false);

  const [owners, setOwners] = useState<OwnerItem[]>([]);
  const [loadingOwners, setLoadingOwners] = useState(false);

  const [pendingBikes, setPendingBikes] = useState<Bike[]>([]);
  const [loadingBikes, setLoadingBikes] = useState(false);

  const [usersList, setUsersList] = useState<User[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(false);

  // Search filter
  const [searchQuery, setSearchQuery] = useState('');

  // Action status feedback
  const [actionMsg, setActionMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Broadcast state
  const [broadcastTitle, setBroadcastTitle] = useState('');
  const [broadcastMessage, setBroadcastMessage] = useState('');
  const [broadcastSending, setBroadcastSending] = useState(false);

  // Verify session on mount
  useEffect(() => {
    if (token) {
      validateSession();
      loadAllAdminData();
    }
  }, [token]);

  const validateSession = async () => {
    try {
      const res = await apiClient.get('/auth/me');
      if (res.data?.data) {
        setUser(res.data.data);
        localStorage.setItem('admin_user', JSON.stringify(res.data.data));
      }
    } catch {
      handleLogout();
    }
  };

  const loadAllAdminData = () => {
    fetchStats();
    fetchDrivers();
    fetchOwners();
    fetchBikes();
    fetchUsers();
    fetchCodEscalations();
  };

  const fetchCodEscalations = async () => {
    setLoadingEscalations(true);
    try {
      const res = await apiClient.get('/admin/cod-escalations');
      if (res.data?.data) {
        setCodEscalations(res.data.data);
      }
    } catch (err) {
      console.error('Failed to load COD escalations:', err);
    } finally {
      setLoadingEscalations(false);
    }
  };

  const fetchStats = async () => {
    setLoadingStats(true);
    try {
      const res = await apiClient.get('/admin/stats');
      if (res.data?.data) {
        setStats(res.data.data);
      }
    } catch (err) {
      console.error('Failed to load admin stats:', err);
    } finally {
      setLoadingStats(false);
    }
  };

  const fetchDrivers = async () => {
    setLoadingDrivers(true);
    try {
      const res = await apiClient.get('/admin/drivers');
      if (res.data?.data) {
        setDrivers(res.data.data);
      }
    } catch (err) {
      console.error('Failed to load drivers:', err);
    } finally {
      setLoadingDrivers(false);
    }
  };

  const fetchOwners = async () => {
    setLoadingOwners(true);
    try {
      const res = await apiClient.get('/admin/owners');
      if (res.data?.data) {
        setOwners(res.data.data);
      }
    } catch (err) {
      console.error('Failed to load owners:', err);
    } finally {
      setLoadingOwners(false);
    }
  };

  const fetchBikes = async () => {
    setLoadingBikes(true);
    try {
      const res = await apiClient.get('/admin/bikes?status=pending');
      if (res.data?.data) {
        setPendingBikes(res.data.data);
      }
    } catch (err) {
      console.error('Failed to load scooties:', err);
    } finally {
      setLoadingBikes(false);
    }
  };

  const fetchUsers = async () => {
    setLoadingUsers(true);
    try {
      const res = await apiClient.get('/admin/users');
      if (res.data?.data) {
        setUsersList(res.data.data);
      }
    } catch (err) {
      console.error('Failed to load users:', err);
    } finally {
      setLoadingUsers(false);
    }
  };

  // Sign In handler
  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError(null);

    try {
      const res = await apiClient.post('/auth/login', {
        email: authEmail.trim(),
        password: authPassword
      });
      const data = res.data?.data;
      if (data?.access_token) {
        if (data.user?.role !== 'admin') {
          setAuthError('Access Denied: This portal requires Administrator privileges.');
          setAuthLoading(false);
          return;
        }
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('admin_user', JSON.stringify(data.user));
        setToken(data.access_token);
        setUser(data.user);
      }
    } catch (err: any) {
      console.error('Admin auth error:', err);
      const detail = err.response?.data?.detail;
      const message = err.response?.data?.message;
      let displayError = 'Invalid admin credentials.';
      if (typeof detail === 'string') {
        displayError = detail;
      } else if (Array.isArray(detail)) {
        displayError = detail.map((d: any) => d.msg || JSON.stringify(d)).join(', ');
      } else if (typeof message === 'string') {
        displayError = message;
      } else if (err.message) {
        displayError = err.message;
      }
      setAuthError(displayError);
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('admin_user');
    setToken(null);
    setUser(null);
    setDrivers([]);
    setOwners([]);
    setPendingBikes([]);
    setUsersList([]);
  };

  // Driver verification action
  const handleDriverVerify = async (userId: string, decision: 'verified' | 'rejected', reason?: string) => {
    try {
      await apiClient.post(`/admin/verify-driver/${userId}`, {
        approved: decision === 'verified',
        rejection_reason: reason
      });
      setDrivers(prev => prev.map(d => d.user_id === userId ? { ...d, verification_status: decision, rejection_reason: reason } : d));
      setActionMsg({ type: 'success', text: `Driver KYC has been marked ${decision} in database.` });
      fetchDrivers();
      fetchStats();
    } catch (err: any) {
      setActionMsg({ type: 'error', text: err.response?.data?.detail || 'Action failed.' });
    }
    setTimeout(() => setActionMsg(null), 3000);
  };

  // Owner verification action
  const handleOwnerVerify = async (userId: string, decision: 'verified' | 'rejected') => {
    try {
      await apiClient.post(`/admin/verify/owner/${userId}`, { status: decision });
      setOwners(prev => prev.map(o => o.user_id === userId ? { ...o, verification_status: decision } : o));
      setActionMsg({ type: 'success', text: `Owner KYC & Bank payout account marked as ${decision} in database.` });
      fetchOwners();
      fetchStats();
    } catch (err: any) {
      setActionMsg({ type: 'error', text: err.response?.data?.detail || 'Action failed.' });
    }
    setTimeout(() => setActionMsg(null), 2500);
  };

  // Bike listing verification action
  const handleBikeVerify = async (bikeId: string, decision: 'verified' | 'rejected') => {
    try {
      await apiClient.post(`/admin/verify/bike/${bikeId}`, { status: decision });
      setPendingBikes(prev => prev.filter(b => b.id !== bikeId));
      setActionMsg({ type: 'success', text: `Scooty listing has been ${decision} in database.` });
      fetchBikes();
      fetchStats();
    } catch (err: any) {
      setActionMsg({ type: 'error', text: err.response?.data?.detail || 'Action failed.' });
    }
    setTimeout(() => setActionMsg(null), 2500);
  };

  // User moderation toggle (Active / Blocked)
  const handleToggleUserStatus = async (userId: string, currentStatus: boolean) => {
    try {
      await apiClient.post(`/admin/users/${userId}/status`, { is_active: !currentStatus });
      setUsersList(prev => prev.map(u => u.id === userId ? { ...u, is_active: !currentStatus } : u));
      setActionMsg({ type: 'success', text: `User status updated in database.` });
    } catch (err: any) {
      setActionMsg({ type: 'error', text: err.response?.data?.detail || 'Failed to update user status.' });
    }
    setTimeout(() => setActionMsg(null), 2500);
  };

  // Send system broadcast
  const handleSendBroadcast = async (e: React.FormEvent) => {
    e.preventDefault();
    setBroadcastSending(true);
    try {
      await apiClient.post('/admin/broadcast', { title: broadcastTitle, message: broadcastMessage });
      setActionMsg({ type: 'success', text: 'Broadcast notification recorded and dispatched to all active users!' });
      setBroadcastTitle('');
      setBroadcastMessage('');
    } catch (err: any) {
      setActionMsg({ type: 'error', text: err.response?.data?.detail || 'Failed to send broadcast.' });
    } finally {
      setBroadcastSending(false);
      setTimeout(() => setActionMsg(null), 2500);
    }
  };

  // Dynamic Time-of-Day Greeting
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const getInitials = (name?: string) => {
    if (!name) return 'AD';
    return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() || 'AD';
  };

  // =========================================================================
  // 1. FIRST: SIGN IN SCREEN (If not authenticated)
  // =========================================================================
  if (!token || !user) {
    return (
      <div className="min-h-screen bg-[#f4f8f6] flex flex-col justify-center items-center p-4 font-sans text-slate-800">
        <div className="w-full max-w-md bg-white border border-slate-200/80 rounded-3xl p-8 shadow-sm">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-11 h-11 rounded-2xl bg-emerald-100 flex items-center justify-center text-emerald-800 font-bold shadow-xs">
              <ShieldCheck className="w-6 h-6 text-emerald-700" />
            </div>
            <div>
              <h2 className="text-xl font-extrabold text-slate-900 tracking-tight">Admin Portal</h2>
              <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">PORT 5431 • LOGIN ONLY</p>
            </div>
          </div>

          <div className="p-3 bg-emerald-50 border border-emerald-100 rounded-2xl mb-5 text-xs text-emerald-900 font-medium">
            <span className="font-bold">Administrator Sign In:</span> Enter authorized admin email and password. Public self-registration is disabled for platform security.
          </div>

          {authError && (
            <div className="mb-4 p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs font-semibold text-rose-700 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{authError}</span>
            </div>
          )}

          <form onSubmit={handleAuthSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Admin Email</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  required
                  placeholder="admin@velorent.com"
                  value={authEmail}
                  onChange={(e) => setAuthEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  placeholder="Enter admin password"
                  value={authPassword}
                  onChange={(e) => setAuthPassword(e.target.value)}
                  className="w-full pl-10 pr-10 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={authLoading}
              className="w-full mt-2 py-3 bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-xs rounded-xl shadow-xs transition flex items-center justify-center gap-2"
            >
              {authLoading ? (
                <span>Authenticating Admin...</span>
              ) : (
                <>
                  <span>Sign In to Governance Console</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 pt-4 border-t border-slate-100 flex flex-col items-center gap-2.5 text-[11px] text-slate-500">
            <div className="w-full p-2.5 bg-slate-50 rounded-xl border border-slate-200/80 text-left space-y-1">
              <span className="font-bold text-slate-700 block">Default Admin Credentials:</span>
              <div className="flex justify-between font-mono text-[11px] text-slate-600">
                <span>Email: <b className="text-slate-900">admin@velorent.com</b></span>
                <span>Pass: <b className="text-slate-900">Admin@12345</b></span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span>Switch Portal:</span>
              <a href={getPortalUrl(3110)} className="font-bold text-emerald-800 hover:underline">
                Driver Portal (3110)
              </a>
              <span>•</span>
              <a href={getPortalUrl(6782)} className="font-bold text-emerald-800 hover:underline">
                Owner Portal (6782)
              </a>
            </div>
            <span>Enterprise Admin Portal • RBAC Security & Audit Active</span>
          </div>
        </div>
      </div>
    );
  }

  // =========================================================================
  // 2. MAIN WORKSPACE (Authenticated)
  // =========================================================================
  const displayName = user.full_name || user.email.split('@')[0];

  return (
    <div className="min-h-screen flex bg-[#f4f8f6] text-slate-800 font-sans">
      {/* ========================================================================= */}
      {/* SIDEBAR PANEL (Slide Bar Navigation) */}
      {/* ========================================================================= */}
      <aside className="w-64 bg-white border-r border-slate-200/80 flex flex-col justify-between p-5 shrink-0 min-h-screen sticky top-0">
        <div>
          {/* Logo brand */}
          <div className="flex items-center gap-3 px-1 py-1">
            <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center text-emerald-800 font-bold shadow-xs">
              <ShieldCheck className="w-5 h-5 text-emerald-700" />
            </div>
            <div>
              <h1 className="font-bold text-slate-900 text-base leading-tight">VeloRent</h1>
              <p className="text-[10px] font-bold text-slate-400 tracking-wider uppercase">GOVERNANCE OPS</p>
            </div>
          </div>

          {/* User profile badge */}
          <div className="mt-5 p-2 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-900 font-bold flex items-center justify-center text-xs">
                {getInitials(displayName)}
              </div>
              <div className="overflow-hidden">
                <p className="text-xs font-semibold text-slate-900 truncate leading-tight">{displayName}</p>
                <p className="text-[11px] text-emerald-700 font-medium">Administrator</p>
              </div>
            </div>
            <ChevronDown className="w-4 h-4 text-slate-400" />
          </div>

          {/* Section Category */}
          <div className="mt-6 mb-2">
            <p className="text-[11px] font-bold text-slate-400 tracking-wider uppercase px-2">PLATFORM OPERATIONS</p>
          </div>

          {/* Navigation Items in Slide Bar */}
          <nav className="space-y-1">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                activeTab === 'dashboard'
                  ? 'bg-emerald-50 text-emerald-900 border border-emerald-100 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <Activity className="w-4 h-4" />
              <span>Dashboard</span>
            </button>

            <button
              onClick={() => setActiveTab('drivers')}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                activeTab === 'drivers'
                  ? 'bg-emerald-50 text-emerald-900 border border-emerald-100 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <div className="flex items-center gap-3">
                <Users className="w-4 h-4" />
                <span>Driver KYC</span>
              </div>
              {drivers.filter(d => d.verification_status === 'pending').length > 0 && (
                <span className="text-[10px] font-bold bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full">
                  {drivers.filter(d => d.verification_status === 'pending').length} Needs Review
                </span>
              )}
            </button>

            <button
              onClick={() => setActiveTab('owners')}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                activeTab === 'owners'
                  ? 'bg-emerald-50 text-emerald-900 border border-emerald-100 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <div className="flex items-center gap-3">
                <Building className="w-4 h-4" />
                <span>Owner KYC & Bank</span>
              </div>
              <span className="text-[10px] font-bold bg-slate-100 text-slate-700 px-2 py-0.5 rounded-full">
                {owners.length}
              </span>
            </button>

            <button
              onClick={() => setActiveTab('bikes')}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                activeTab === 'bikes'
                  ? 'bg-emerald-50 text-emerald-900 border border-emerald-100 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <div className="flex items-center gap-3">
                <BikeIcon className="w-4 h-4" />
                <span>Scooty Approvals</span>
              </div>
              {pendingBikes.length > 0 && (
                <span className="px-2 py-0.5 text-[10px] font-bold bg-amber-100 text-amber-800 rounded-full">
                  {pendingBikes.length} Queue
                </span>
              )}
            </button>

            <button
              onClick={() => setActiveTab('users')}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                activeTab === 'users'
                  ? 'bg-emerald-50 text-emerald-900 border border-emerald-100 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <div className="flex items-center gap-3">
                <Users className="w-4 h-4" />
                <span>User Directory</span>
              </div>
              <span className="text-[10px] font-bold bg-slate-100 text-slate-700 px-2 py-0.5 rounded-full">
                {usersList.length}
              </span>
            </button>

            <button
              onClick={() => setActiveTab('cod_escalations')}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                activeTab === 'cod_escalations'
                  ? 'bg-rose-50 text-rose-950 border border-rose-200 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <div className="flex items-center gap-3">
                <AlertTriangle className="w-4 h-4 text-amber-600" />
                <span>COD Alerts &gt; 10h</span>
              </div>
              {codEscalations.filter(c => c.is_escalated).length > 0 && (
                <span className="px-2 py-0.5 text-[10px] font-bold bg-rose-100 text-rose-800 rounded-full animate-pulse">
                  {codEscalations.filter(c => c.is_escalated).length} Alert
                </span>
              )}
            </button>

            <button
              onClick={() => setActiveTab('broadcast')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                activeTab === 'broadcast'
                  ? 'bg-emerald-50 text-emerald-900 border border-emerald-100 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <Radio className="w-4 h-4" />
              <span>Broadcast Notice</span>
            </button>
          </nav>
        </div>

        {/* Bottom Help Widget & Signout */}
        <div className="pt-4 border-t border-slate-100">
          <div className="bg-gradient-to-br from-emerald-800 to-teal-900 text-white rounded-2xl p-4 shadow-sm relative overflow-hidden">
            <div className="w-7 h-7 rounded-lg bg-white/10 flex items-center justify-center text-white mb-2">
              <HelpCircle className="w-4 h-4" />
            </div>
            <h4 className="text-xs font-bold leading-tight">Need a hand?</h4>
            <p className="text-[11px] text-emerald-100/90 mt-1 leading-normal">
              Platform governance & security audit controls.
            </p>
            <button
              onClick={() => alert("Admin Compliance Console: System secure and operational.")}
              className="mt-3 w-full bg-white hover:bg-emerald-50 text-emerald-950 font-bold text-[11px] py-1.5 px-3 rounded-lg text-center shadow-xs transition"
            >
              Explore help center
            </button>
          </div>

          {/* Quick Portal Switcher */}
          <div className="mt-3 p-2 bg-slate-50 border border-slate-200/70 rounded-xl space-y-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block px-1">Other Portals</span>
            <a
              href={getPortalUrl(3110)}
              className="flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:text-emerald-700 hover:bg-emerald-50 transition"
              title="Open Driver Portal on Port 3110"
            >
              <div className="flex items-center gap-2">
                <BikeIcon className="w-3.5 h-3.5 text-slate-500" />
                <span>Driver Platform</span>
              </div>
              <span className="text-[10px] text-slate-400 font-mono">:3110</span>
            </a>
            <a
              href={getPortalUrl(6782)}
              className="flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:text-emerald-700 hover:bg-emerald-50 transition"
              title="Open Owner Portal on Port 6782"
            >
              <div className="flex items-center gap-2">
                <Building className="w-3.5 h-3.5 text-slate-500" />
                <span>Owner Fleet</span>
              </div>
              <span className="text-[10px] text-slate-400 font-mono">:6782</span>
            </a>
          </div>

          <button
            onClick={handleLogout}
            className="w-full mt-3 flex items-center gap-2.5 px-3 py-2 text-xs font-medium text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-xl transition-colors"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign out</span>
          </button>
        </div>
      </aside>

      {/* ========================================================================= */}
      {/* MAIN VIEWPORT */}
      {/* ========================================================================= */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-16 px-8 flex items-center justify-between bg-white/70 backdrop-blur-md border-b border-slate-200/60 sticky top-0 z-20">
          <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
            <span>Workspace</span>
            <span className="text-slate-300">/</span>
            <span className="text-slate-900 font-semibold capitalize">{activeTab.replace('_', ' ')}</span>
          </div>

          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search anything..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 pr-4 py-1.5 bg-slate-50 border border-slate-200/80 rounded-full text-xs text-slate-700 w-64 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition"
              />
            </div>

            <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-50 border border-emerald-200 rounded-full text-xs font-bold text-emerald-900">
              <DollarSign className="w-3.5 h-3.5 text-emerald-700" />
              <span>Platform 10% Cut: ₹{stats.platform_commission.toLocaleString()}</span>
            </div>

            {/* Portal Switcher Buttons */}
            <div className="hidden md:flex items-center gap-1 bg-slate-100 p-1 rounded-full text-[11px] font-bold">
              <a
                href={getPortalUrl(3110)}
                className="px-2.5 py-1 text-slate-500 hover:text-slate-900 hover:bg-white/60 rounded-full transition"
                title="Open Driver Portal (Port 3110)"
              >
                Driver
              </a>
              <a
                href={getPortalUrl(6782)}
                className="px-2.5 py-1 text-slate-500 hover:text-slate-900 hover:bg-white/60 rounded-full transition"
                title="Open Owner Portal (Port 6782)"
              >
                Owner
              </a>
              <span className="px-2.5 py-1 bg-white text-purple-900 rounded-full shadow-xs flex items-center gap-1">
                <ShieldCheck className="w-3 h-3 text-purple-600" />
                <span>Admin</span>
              </span>
            </div>

            <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
              <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-900 font-bold flex items-center justify-center text-xs">
                {getInitials(displayName)}
              </div>
              <span className="text-xs font-bold text-slate-900">{displayName}</span>
            </div>
          </div>
        </header>

        {/* Main Body */}
        <main className="p-8 space-y-6">
          {/* ========================================================================= */}
          {/* HERO GREETING BANNER (Dynamic Time-of-Day Greeting) */}
          {/* ========================================================================= */}
          <div className="bg-gradient-to-r from-[#0d5940] via-[#0e6b4e] to-[#0a4a35] text-white rounded-3xl p-7 shadow-sm relative overflow-hidden">
            <div className="absolute right-0 top-0 bottom-0 w-80 bg-white/5 rounded-l-full pointer-events-none"></div>

            <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <p className="text-[11px] font-bold tracking-wider text-emerald-200/90 uppercase">
                  {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                </p>
                <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight mt-1 text-white">
                  {getGreeting()}, {displayName.split(' ')[0]}
                </h2>
                <p className="text-xs md:text-sm text-emerald-100/90 mt-1">
                  Your platform governance, verification queues and revenue overview for today.
                </p>

                <div className="flex items-center gap-2 mt-4">
                  <span className="px-3 py-1 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full text-xs font-semibold text-white">
                    Governance platform
                  </span>
                  <span className="px-3 py-1 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full text-xs font-medium text-emerald-100">
                    Live Database Connected
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={loadAllAdminData}
                  className="px-4 py-2 bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/20 rounded-full text-xs font-semibold text-white flex items-center gap-2 shadow-xs transition"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  <span>Refresh overview</span>
                </button>
              </div>
            </div>
          </div>

          {/* URGENT COD ESCALATIONS ALERT BANNER (> 10h UNPAID CASH) */}
          {codEscalations.filter(c => c.is_escalated).length > 0 && (
            <div className="p-4 bg-rose-50 border border-rose-300 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xs">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-rose-200 text-rose-900 flex items-center justify-center font-bold">
                  <AlertTriangle className="w-5 h-5 text-rose-800" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-rose-950">
                    URGENT: {codEscalations.filter(c => c.is_escalated).length} Cash on Delivery Rental(s) Overdue &gt; 10 Hours!
                  </h4>
                  <p className="text-[11px] text-rose-800 mt-0.5">
                    Owner has not received cash payment for over 10 hours. Immediate administrative intervention required.
                  </p>
                </div>
              </div>
              <button
                onClick={() => setActiveTab('cod_escalations')}
                className="px-4 py-2 bg-rose-800 hover:bg-rose-900 text-white rounded-xl text-xs font-bold shadow-xs transition shrink-0"
              >
                Inspect Escalations →
              </button>
            </div>
          )}

          {actionMsg && (
            <div className={`p-4 rounded-2xl flex items-center gap-3 text-xs font-semibold shadow-xs ${
              actionMsg.type === 'success' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'
            }`}>
              <CheckCircle2 className="w-4 h-4 text-emerald-700 shrink-0" />
              <span>{actionMsg.text}</span>
            </div>
          )}

          {/* ========================================================================= */}
          {/* 4 KPI METRIC CARDS */}
          {/* ========================================================================= */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500">Gross rental revenue</span>
                <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center">
                  <DollarSign className="w-4 h-4" />
                </div>
              </div>
              <div className="my-2">
                <span className="text-2xl font-extrabold text-slate-900">₹{stats.gross_revenue.toLocaleString()}</span>
              </div>
              <div className="flex items-center gap-1.5 text-[11px] font-bold text-emerald-700">
                <span>↗ Total volume</span>
                <span className="font-normal text-slate-400">in live database</span>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500">Platform commission</span>
                <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center">
                  <CreditCard className="w-4 h-4" />
                </div>
              </div>
              <div className="my-2">
                <span className="text-2xl font-extrabold text-slate-900">₹{stats.platform_commission.toLocaleString()}</span>
              </div>
              <div className="flex items-center gap-1.5 text-[11px] font-bold text-blue-700">
                <span>↗ 10% auto-cut</span>
                <span className="font-normal text-slate-400">retained profit</span>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500">Pending verifications</span>
                <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-700 flex items-center justify-center">
                  <FileText className="w-4 h-4" />
                </div>
              </div>
              <div className="my-2">
                <span className="text-2xl font-extrabold text-slate-900">
                  {drivers.filter(d => d.verification_status === 'pending').length + pendingBikes.length}
                </span>
              </div>
              <div className="flex items-center gap-1.5 text-[11px] font-bold text-amber-700">
                <span>Needs review</span>
                <span className="font-normal text-slate-400">KYC & RC queues</span>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500">Active fleet</span>
                <div className="w-8 h-8 rounded-lg bg-purple-50 text-purple-700 flex items-center justify-center">
                  <BikeIcon className="w-4 h-4" />
                </div>
              </div>
              <div className="my-2">
                <span className="text-2xl font-extrabold text-slate-900">{stats.total_bikes}</span>
              </div>
              <div className="flex items-center gap-1.5 text-[11px] font-bold text-purple-700">
                <span>↗ {stats.active_rentals || 0} on trip</span>
                <span className="font-normal text-slate-400">scooties registered</span>
              </div>
            </div>
          </div>

          {/* Two-Column Workspace Module */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left 8 Cols */}
            <div className="lg:col-span-8 bg-white rounded-2xl border border-slate-200/80 p-6 shadow-xs">
              {activeTab === 'cod_escalations' ? (
                /* COD Escalations (> 10h Uncollected Cash) */
                <div>
                  <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
                    <div>
                      <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4 text-rose-600" />
                        <span>Cash on Delivery (COD) Uncollected Alerts</span>
                      </h3>
                      <p className="text-xs text-slate-500 mt-0.5">Rentals where cash payment was not received by owner. Escalated to admin after 10 hours.</p>
                    </div>
                  </div>

                  {loadingEscalations ? (
                    <div className="p-12 text-center text-slate-400">
                      <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-emerald-600" />
                      <p className="text-xs">Loading COD escalations from database...</p>
                    </div>
                  ) : codEscalations.length === 0 ? (
                    <div className="p-12 text-center text-slate-400 border border-dashed border-slate-200 rounded-2xl">
                      <CheckCircle2 className="w-10 h-10 mx-auto mb-2 text-emerald-600" />
                      <p className="text-sm font-bold text-slate-700">All Cash Payments Settled</p>
                      <p className="text-xs mt-1 text-slate-500">No overdue or escalated Cash on Delivery rentals detected in the system.</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {codEscalations.map(esc => (
                        <div
                          key={esc.assignment_id}
                          className={`p-4 rounded-2xl border ${
                            esc.is_escalated
                              ? 'bg-rose-50/70 border-rose-200 ring-1 ring-rose-200'
                              : 'bg-amber-50/60 border-amber-200'
                          }`}
                        >
                          <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 pb-3 border-b border-slate-200/60">
                            <div>
                              <div className="flex items-center gap-2 flex-wrap">
                                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                                  esc.is_escalated ? 'bg-rose-200 text-rose-950 font-extrabold' : 'bg-amber-200 text-amber-950'
                                }`}>
                                  {esc.is_escalated ? '🚨 URGENT: OVERDUE > 10 HOURS' : '⏳ PENDING COD CASH'}
                                </span>
                                <span className="text-xs font-bold text-slate-900">
                                  {esc.bike_name} ({esc.registration_number})
                                </span>
                              </div>
                              <p className="text-xs text-slate-600 mt-1">
                                Duration: <strong>{esc.rental_hours}h</strong> • Elapsed since assignment: <strong className="text-rose-700">{esc.elapsed_hours} hour(s)</strong>
                              </p>
                            </div>

                            <div className="text-right">
                              <p className="text-xs text-slate-500">Uncollected Rent</p>
                              <p className="text-base font-extrabold text-rose-700">₹{esc.rent_amount}</p>
                            </div>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-3 text-xs">
                            <div className="p-2.5 bg-white/80 rounded-xl border border-slate-200">
                              <p className="font-bold text-slate-900">Driver Details</p>
                              <p className="text-slate-600 mt-0.5">{esc.driver_name} ({esc.driver_email})</p>
                              <p className="text-slate-500">Phone: {esc.driver_phone || 'N/A'}</p>
                            </div>
                            <div className="p-2.5 bg-white/80 rounded-xl border border-slate-200">
                              <p className="font-bold text-slate-900">Owner Details</p>
                              <p className="text-slate-600 mt-0.5">{esc.owner_name} ({esc.owner_email})</p>
                              <p className="text-slate-500">Phone: {esc.owner_phone || 'N/A'}</p>
                            </div>
                          </div>

                          <div className="mt-3 pt-2.5 border-t border-slate-200/60 flex items-center justify-between">
                            <p className="text-[11px] text-slate-500">
                              Assigned on: {new Date(esc.assigned_at).toLocaleString()}
                            </p>
                            <button
                              onClick={() => alert(`Admin Intervene: Please contact Driver at ${esc.driver_phone || esc.driver_email} and Owner at ${esc.owner_phone || esc.owner_email} regarding cash payment of ₹${esc.rent_amount}.`)}
                              className="px-3.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-bold shadow-xs transition"
                            >
                              Intervene / Contact
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : activeTab === 'dashboard' || activeTab === 'drivers' ? (
                <div>
                  <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
                    <div>
                      <h3 className="text-sm font-bold text-slate-900">Driver KYC Verification Queue</h3>
                      <p className="text-xs text-slate-500 mt-0.5">Validate Driving License & Aadhaar card before permitting scooty rental</p>
                    </div>
                  </div>

                  {loadingDrivers ? (
                    <div className="p-12 text-center text-slate-400">
                      <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-emerald-600" />
                      <p className="text-xs">Loading drivers from database...</p>
                    </div>
                  ) : drivers.length === 0 ? (
                    <div className="p-12 text-center text-slate-400 border border-dashed border-slate-200 rounded-2xl">
                      <Users className="w-10 h-10 mx-auto mb-2 text-slate-300" />
                      <p className="text-sm font-bold text-slate-700">No Drivers Registered Yet</p>
                      <p className="text-xs mt-1 text-slate-500">When drivers sign up and upload KYC documents, their profiles will appear here.</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {drivers.map(d => (
                        <div key={d.user_id} className="p-4 bg-slate-50/50 hover:bg-slate-50 border border-slate-200/80 rounded-2xl transition">
                          <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                            <div className="flex items-start gap-3.5">
                              {d.profile_picture ? (
                                <img
                                  src={`${getBackendBaseUrl()}/${d.profile_picture.replace(/^\//, '')}`}
                                  alt={d.full_name}
                                  className="w-12 h-12 rounded-xl object-cover border border-slate-200 shrink-0"
                                />
                              ) : (
                                <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-800 font-bold flex items-center justify-center shrink-0 text-sm">
                                  {d.full_name ? d.full_name.slice(0, 2).toUpperCase() : 'DR'}
                                </div>
                              )}

                              <div>
                                <div className="flex items-center gap-2">
                                  <h4 className="text-sm font-bold text-slate-900">{d.full_name}</h4>
                                  <span className={`px-2.5 py-0.5 text-[10px] font-bold rounded-full ${
                                    d.verification_status === 'verified' ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' :
                                    d.verification_status === 'rejected' ? 'bg-rose-100 text-rose-800 border border-rose-200' :
                                    d.verification_status === 'pending' ? 'bg-amber-100 text-amber-800 border border-amber-200' :
                                    'bg-slate-100 text-slate-700 border border-slate-200'
                                  }`}>
                                    {d.verification_status.toUpperCase()}
                                  </span>
                                </div>
                                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500 mt-1">
                                  <span>✉ {d.email}</span>
                                  {d.phone && <span>📞 {d.phone}</span>}
                                  {d.address && <span>📍 {d.address}</span>}
                                </div>

                                {d.emergency_contact?.name && (
                                  <p className="text-[11px] text-slate-500 mt-1">
                                    <span className="font-semibold text-slate-700">Emergency Contact:</span> {d.emergency_contact.name} ({d.emergency_contact.phone || 'No phone'})
                                  </p>
                                )}

                                {d.rejection_reason && d.verification_status === 'rejected' && (
                                  <p className="text-[11px] text-rose-600 font-medium mt-1">
                                    Rejection Reason: {d.rejection_reason}
                                  </p>
                                )}

                                {/* Document inspection badges & links */}
                                <div className="mt-3 flex flex-wrap gap-2">
                                  {/* Driving License */}
                                  <div className="flex items-center gap-1.5 px-2.5 py-1 bg-white border border-slate-200 rounded-lg text-xs">
                                    <FileText className="w-3.5 h-3.5 text-emerald-600" />
                                    <span className="font-semibold text-slate-800">DL: {d.driving_license_number || 'N/A'}</span>
                                    {d.driving_license_file ? (
                                      <a
                                        href={`${getBackendBaseUrl()}/${d.driving_license_file.replace(/^\//, '')}`}
                                        target="_blank"
                                        rel="noreferrer"
                                        className="text-emerald-700 hover:text-emerald-900 font-bold ml-1 inline-flex items-center gap-0.5"
                                      >
                                        [View] <ExternalLink className="w-3 h-3" />
                                      </a>
                                    ) : (
                                      <span className="text-slate-400 text-[10px] ml-1">(No file)</span>
                                    )}
                                  </div>

                                  {/* Aadhaar Card */}
                                  <div className="flex items-center gap-1.5 px-2.5 py-1 bg-white border border-slate-200 rounded-lg text-xs">
                                    <FileText className="w-3.5 h-3.5 text-emerald-600" />
                                    <span className="font-semibold text-slate-800">Aadhaar: {d.aadhaar_number || 'N/A'}</span>
                                    {d.aadhaar_file ? (
                                      <a
                                        href={`${getBackendBaseUrl()}/${d.aadhaar_file.replace(/^\//, '')}`}
                                        target="_blank"
                                        rel="noreferrer"
                                        className="text-emerald-700 hover:text-emerald-900 font-bold ml-1 inline-flex items-center gap-0.5"
                                      >
                                        [View] <ExternalLink className="w-3 h-3" />
                                      </a>
                                    ) : (
                                      <span className="text-slate-400 text-[10px] ml-1">(No file)</span>
                                    )}
                                  </div>

                                  {/* PAN Card */}
                                  <div className="flex items-center gap-1.5 px-2.5 py-1 bg-white border border-slate-200 rounded-lg text-xs">
                                    <FileText className="w-3.5 h-3.5 text-emerald-600" />
                                    <span className="font-semibold text-slate-800">PAN: {d.pan_number || 'N/A'}</span>
                                    {d.pan_file ? (
                                      <a
                                        href={`${getBackendBaseUrl()}/${d.pan_file.replace(/^\//, '')}`}
                                        target="_blank"
                                        rel="noreferrer"
                                        className="text-emerald-700 hover:text-emerald-900 font-bold ml-1 inline-flex items-center gap-0.5"
                                      >
                                        [View] <ExternalLink className="w-3 h-3" />
                                      </a>
                                    ) : (
                                      <span className="text-slate-400 text-[10px] ml-1">(No file)</span>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </div>

                            {/* Actions */}
                            <div className="flex items-center gap-2 shrink-0 self-end md:self-center">
                              {d.verification_status !== 'verified' && (
                                <button
                                  onClick={() => handleDriverVerify(d.user_id, 'verified')}
                                  className="px-3.5 py-2 bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-bold rounded-xl shadow-xs transition flex items-center gap-1.5"
                                >
                                  <Check className="w-3.5 h-3.5" />
                                  <span>Approve KYC</span>
                                </button>
                              )}
                              {d.verification_status !== 'rejected' && (
                                <button
                                  onClick={() => {
                                    const reason = prompt('Enter rejection reason (optional):') || 'Document verification failed.';
                                    handleDriverVerify(d.user_id, 'rejected', reason);
                                  }}
                                  className="px-3.5 py-2 border border-slate-200 bg-white hover:bg-rose-50 hover:border-rose-200 text-rose-700 text-xs font-bold rounded-xl transition flex items-center gap-1.5"
                                >
                                  <XCircle className="w-3.5 h-3.5" />
                                  <span>Reject</span>
                                </button>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : activeTab === 'owners' ? (
                /* Owner Verification Tab */
                <div>
                  <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
                    <div>
                      <h3 className="text-sm font-bold text-slate-900">Fleet Owner KYC & Bank Payout Accounts</h3>
                      <p className="text-xs text-slate-500 mt-0.5">Approve bank accounts for weekly rental payouts</p>
                    </div>
                  </div>

                  {loadingOwners ? (
                    <div className="p-12 text-center text-slate-400">
                      <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-emerald-600" />
                      <p className="text-xs">Loading fleet owners from database...</p>
                    </div>
                  ) : owners.length === 0 ? (
                    <div className="p-12 text-center text-slate-400 border border-dashed border-slate-200 rounded-2xl">
                      <Building className="w-10 h-10 mx-auto mb-2 text-slate-300" />
                      <p className="text-sm font-bold text-slate-700">No Fleet Owners Registered Yet</p>
                      <p className="text-xs mt-1 text-slate-500">Fleet partners will appear here once they register.</p>
                    </div>
                  ) : (
                    <div className="divide-y divide-slate-100">
                      {owners.map(o => (
                        <div key={o.user_id} className="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                          <div>
                            <div className="flex items-center gap-2">
                              <h4 className="text-xs font-bold text-slate-900">{o.full_name || o.business_name || 'Fleet Owner'}</h4>
                              <span className={`px-2 py-0.5 text-[10px] font-bold rounded-full ${
                                o.verification_status === 'verified' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                              }`}>
                                {o.verification_status.toUpperCase()}
                              </span>
                            </div>
                            <p className="text-[11px] text-slate-500 mt-0.5">{o.email}</p>
                            <div className="mt-1 flex flex-wrap gap-2 text-[11px] text-slate-600 font-medium">
                              <span className="bg-slate-50 px-2 py-0.5 rounded border border-slate-200">A/C: {o.bank_account_number || 'Not Submitted'}</span>
                              <span className="bg-slate-50 px-2 py-0.5 rounded border border-slate-200">IFSC: {o.bank_ifsc || 'Not Submitted'}</span>
                            </div>
                          </div>

                          {o.verification_status === 'pending' && (
                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => handleOwnerVerify(o.user_id, 'rejected')}
                                className="px-3 py-1.5 border border-slate-200 bg-white hover:bg-slate-100 text-slate-700 text-xs font-bold rounded-xl"
                              >
                                Reject
                              </button>
                              <button
                                onClick={() => handleOwnerVerify(o.user_id, 'verified')}
                                className="px-3.5 py-1.5 bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-bold rounded-xl shadow-xs"
                              >
                                Verify Bank Account
                              </button>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : activeTab === 'bikes' ? (
                /* Scooty Listing Queue */
                <div>
                  <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
                    <div>
                      <h3 className="text-sm font-bold text-slate-900">Scooty Listing Approvals Queue</h3>
                      <p className="text-xs text-slate-500 mt-0.5">Verify RC copy, model specifications and fair pricing policy</p>
                    </div>
                  </div>

                  {loadingBikes ? (
                    <div className="p-12 text-center text-slate-400">
                      <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-emerald-600" />
                      <p className="text-xs">Loading scooty approval queue from database...</p>
                    </div>
                  ) : pendingBikes.length === 0 ? (
                    <div className="p-12 text-center text-slate-400 border border-dashed border-slate-200 rounded-2xl">
                      <BikeIcon className="w-10 h-10 mx-auto mb-2 text-slate-300" />
                      <p className="text-sm font-bold text-slate-700">Approval Queue is Clear</p>
                      <p className="text-xs mt-1 text-slate-500">No scooties are currently pending RC verification.</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {pendingBikes.map(b => (
                        <div key={b.id} className="p-4 bg-slate-50 rounded-2xl border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="text-[10px] font-bold bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full">
                                Pending RC Verification
                              </span>
                              <h4 className="text-xs font-bold text-slate-900">{b.bike_name}</h4>
                            </div>
                            <p className="text-[11px] text-slate-500 mt-0.5">{b.registration_number} • {b.brand} • {b.fuel_type}</p>
                            <p className="text-xs font-bold text-slate-800 mt-1">
                              Daily Rent: ₹{b.pricing?.daily_rent} | Deposit: ₹{b.pricing?.security_deposit}
                            </p>
                          </div>

                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => handleBikeVerify(b.id, 'rejected')}
                              className="px-3.5 py-1.5 border border-slate-200 bg-white hover:bg-slate-100 text-slate-700 text-xs font-bold rounded-xl"
                            >
                              Reject Listing
                            </button>
                            <button
                              onClick={() => handleBikeVerify(b.id, 'verified')}
                              className="px-4 py-1.5 bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-bold rounded-xl shadow-xs"
                            >
                              Verify & Publish
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : activeTab === 'users' ? (
                /* User Moderation Directory */
                <div>
                  <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
                    <div>
                      <h3 className="text-sm font-bold text-slate-900">User Moderation Directory</h3>
                      <p className="text-xs text-slate-500 mt-0.5">Manage drivers, owners and block/unblock accounts</p>
                    </div>
                  </div>

                  {usersList.length === 0 ? (
                    <div className="p-8 text-center text-slate-400">
                      <p className="text-xs">No registered users found in database.</p>
                    </div>
                  ) : (
                    <div className="divide-y divide-slate-100">
                      {usersList.map(u => (
                        <div key={u.id} className="py-3 flex items-center justify-between">
                          <div>
                            <p className="text-xs font-bold text-slate-900">{u.full_name || u.email}</p>
                            <p className="text-[11px] text-slate-500">{u.email} • Role: <strong className="uppercase">{u.role}</strong></p>
                          </div>
                          <button
                            onClick={() => handleToggleUserStatus(u.id, u.is_active)}
                            className={`px-3 py-1 rounded-xl text-xs font-bold ${
                              u.is_active
                                ? 'bg-rose-50 text-rose-700 border border-rose-200 hover:bg-rose-100'
                                : 'bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-100'
                            }`}
                          >
                            {u.is_active ? 'Block User' : 'Unblock User'}
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                /* Broadcast Tab */
                <div>
                  <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
                    <div>
                      <h3 className="text-sm font-bold text-slate-900">Platform Broadcast Console</h3>
                      <p className="text-xs text-slate-500 mt-0.5">Send alerts, terms updates or festival surge messages to all users</p>
                    </div>
                  </div>

                  <form onSubmit={handleSendBroadcast} className="space-y-4">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">Announcement Title</label>
                      <input
                        type="text"
                        required
                        placeholder="e.g. System Maintenance Notice / Festival Surge Alert"
                        value={broadcastTitle}
                        onChange={(e) => setBroadcastTitle(e.target.value)}
                        className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-800 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">Broadcast Message Body</label>
                      <textarea
                        rows={3}
                        required
                        placeholder="Write announcement message..."
                        value={broadcastMessage}
                        onChange={(e) => setBroadcastMessage(e.target.value)}
                        className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                      ></textarea>
                    </div>

                    <div className="flex justify-end pt-2">
                      <button
                        type="submit"
                        disabled={broadcastSending}
                        className="px-5 py-2 bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-bold rounded-xl shadow-xs flex items-center gap-2"
                      >
                        <Send className="w-3.5 h-3.5" />
                        <span>{broadcastSending ? 'Saving to Database...' : 'Dispatch Platform Broadcast'}</span>
                      </button>
                    </div>
                  </form>
                </div>
              )}
            </div>

            {/* Right 4 Cols: Quick Actions */}
            <div className="lg:col-span-4 bg-white rounded-2xl border border-slate-200/80 p-6 shadow-xs flex flex-col justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-900 leading-tight">Governance operations</h3>
                <p className="text-xs text-slate-500 mt-0.5 mb-5">Open a workspace module to take action.</p>

                <div className="space-y-3">
                  <div
                    onClick={() => setActiveTab('drivers')}
                    className="p-3.5 bg-slate-50 hover:bg-emerald-50/70 border border-slate-100 hover:border-emerald-200 rounded-xl cursor-pointer transition flex items-center justify-between group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center">
                        <Users className="w-4 h-4" />
                      </div>
                      <div>
                        <p className="text-xs font-bold text-slate-900 leading-tight">Verify driver KYC</p>
                        <p className="text-[11px] text-slate-500 mt-0.5">DL & Aadhaar verification queue</p>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-emerald-700 group-hover:translate-x-0.5 transition" />
                  </div>

                  <div
                    onClick={() => setActiveTab('owners')}
                    className="p-3.5 bg-slate-50 hover:bg-emerald-50/70 border border-slate-100 hover:border-emerald-200 rounded-xl cursor-pointer transition flex items-center justify-between group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-lg bg-blue-100 text-blue-800 flex items-center justify-center">
                        <Building className="w-4 h-4" />
                      </div>
                      <div>
                        <p className="text-xs font-bold text-slate-900 leading-tight">Verify owner bank accounts</p>
                        <p className="text-[11px] text-slate-500 mt-0.5">Authorize payout credentials</p>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-emerald-700 group-hover:translate-x-0.5 transition" />
                  </div>

                  <div
                    onClick={() => setActiveTab('bikes')}
                    className="p-3.5 bg-slate-50 hover:bg-emerald-50/70 border border-slate-100 hover:border-emerald-200 rounded-xl cursor-pointer transition flex items-center justify-between group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-lg bg-amber-100 text-amber-800 flex items-center justify-center">
                        <BikeIcon className="w-4 h-4" />
                      </div>
                      <div>
                        <p className="text-xs font-bold text-slate-900 leading-tight">Approve scooty listings</p>
                        <p className="text-[11px] text-slate-500 mt-0.5">RC documents & pricing checks</p>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-emerald-700 group-hover:translate-x-0.5 transition" />
                  </div>

                  <div
                    onClick={() => setActiveTab('broadcast')}
                    className="p-3.5 bg-slate-50 hover:bg-emerald-50/70 border border-slate-100 hover:border-emerald-200 rounded-xl cursor-pointer transition flex items-center justify-between group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-lg bg-purple-100 text-purple-800 flex items-center justify-center">
                        <Radio className="w-4 h-4" />
                      </div>
                      <div>
                        <p className="text-xs font-bold text-slate-900 leading-tight">Dispatch broadcast notice</p>
                        <p className="text-[11px] text-slate-500 mt-0.5">Platform announcements</p>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-emerald-700 group-hover:translate-x-0.5 transition" />
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
                <span className="flex items-center gap-1.5 font-semibold text-emerald-800">
                  <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                  Admin Governance Live
                </span>
                <span>Port 5431</span>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
