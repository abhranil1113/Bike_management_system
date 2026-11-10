import React, { useState, useEffect } from 'react';
import {
  Bike as BikeIcon, Plus, CheckCircle2, Clock, AlertCircle,
  DollarSign, FileText, X, ChevronRight, User as UserIcon,
  ShieldCheck, RefreshCw, Bell, LogOut, ArrowUpRight, Search,
  Activity, HelpCircle, ChevronDown, Check, AlertTriangle, Building, CreditCard,
  Lock, Mail, Phone, ArrowRight, Eye, EyeOff
} from 'lucide-react';
import { apiClient, getPortalUrl } from '../../shared/api';
import type { Bike, BookingRequest, ActiveAssignment, NotificationItem, User } from '../../shared/types';

export default function OwnerApp() {
  // Authentication & session state
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('access_token'));
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('owner_user');
    return saved ? JSON.parse(saved) : null;
  });

  // Auth form state
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [authEmail, setAuthEmail] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [authConfirmPassword, setAuthConfirmPassword] = useState('');
  const [authFullName, setAuthFullName] = useState('');
  const [authPhone, setAuthPhone] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);

  // Navigation tab
  const [activeTab, setActiveTab] = useState<'dashboard' | 'fleet' | 'requests' | 'rentals' | 'earnings' | 'kyc'>('dashboard');

  // Real Database state (No hardcoded demo values)
  const [bikes, setBikes] = useState<Bike[]>([]);
  const [loadingBikes, setLoadingBikes] = useState(false);
  const [showAddBikeModal, setShowAddBikeModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Booking requests
  const [bookingRequests, setBookingRequests] = useState<BookingRequest[]>([]);
  const [loadingRequests, setLoadingRequests] = useState(false);
  const [requestActionLoading, setRequestActionLoading] = useState<string | null>(null);

  // Active rentals
  const [activeRentals, setActiveRentals] = useState<ActiveAssignment[]>([]);
  const [loadingRentals, setLoadingRentals] = useState(false);

  // Return inspection dialog state
  const [inspectingRental, setInspectingRental] = useState<ActiveAssignment | null>(null);
  const [damageCharge, setDamageCharge] = useState<number>(0);
  const [inspectionNotes, setInspectionNotes] = useState('Vehicle in good condition.');
  const [inspectionSubmitting, setInspectionSubmitting] = useState(false);
  const [inspectionResult, setInspectionResult] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // New bike form state
  const [newBikeName, setNewBikeName] = useState('');
  const [newBrand, setNewBrand] = useState('Honda');
  const [newModel, setNewModel] = useState('Activa 6G');
  const [newRegNo, setNewRegNo] = useState('');
  const [newColor, setNewColor] = useState('Black');
  const [newFuel, setNewFuel] = useState('petrol');
  const [newKm, setNewKm] = useState(5000);
  const [newDailyRent, setNewDailyRent] = useState(350);
  const [newDeposit, setNewDeposit] = useState(1500);
  const [newHourlyRate, setNewHourlyRate] = useState<number>(100);
  const [newTariffs, setNewTariffs] = useState<Array<{ hours: number; price: number }>>([
    { hours: 1, price: 100 },
    { hours: 2, price: 190 },
    { hours: 4, price: 360 },
    { hours: 8, price: 680 },
    { hours: 12, price: 950 },
    { hours: 24, price: 1800 }
  ]);
  const [customHours, setCustomHours] = useState<number>(3);
  const [customPrice, setCustomPrice] = useState<number>(280);
  const [cashActionLoading, setCashActionLoading] = useState<string | null>(null);
  const [addBikeLoading, setAddBikeLoading] = useState(false);
  const [addBikeMsg, setAddBikeMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // KYC state
  const [bankAccount, setBankAccount] = useState('');
  const [bankIfsc, setBankIfsc] = useState('');
  const [businessName, setBusinessName] = useState('');
  const [kycSuccess, setKycSuccess] = useState<string | null>(null);

  // Notifications
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [showNotifications, setShowNotifications] = useState(false);

  // Check if user navigated to /admin or /driver path on port 6782 and redirect
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const p = window.location.pathname.toLowerCase();
      if (p === '/admin' || p.startsWith('/admin/')) {
        window.location.href = getPortalUrl(5431);
      } else if (p === '/driver' || p.startsWith('/driver/')) {
        window.location.href = getPortalUrl(3110);
      }
    }
  }, []);

  // Verify session on mount
  useEffect(() => {
    if (token) {
      validateSession();
      loadAllOwnerData();
    }
  }, [token]);

  const validateSession = async () => {
    try {
      const res = await apiClient.get('/auth/me');
      if (res.data?.data) {
        setUser(res.data.data);
        localStorage.setItem('owner_user', JSON.stringify(res.data.data));
      }
    } catch {
      handleLogout();
    }
  };

  const loadAllOwnerData = () => {
    fetchOwnerBikes();
    fetchBookingRequests();
    fetchActiveRentals();
  };

  const fetchOwnerBikes = async () => {
    setLoadingBikes(true);
    try {
      const res = await apiClient.get('/owner/bikes');
      if (res.data?.data) {
        setBikes(res.data.data);
      }
    } catch (err) {
      console.error('Failed to load owner fleet:', err);
    } finally {
      setLoadingBikes(false);
    }
  };

  const fetchBookingRequests = async () => {
    setLoadingRequests(true);
    try {
      const res = await apiClient.get('/owner/booking-requests');
      if (res.data?.data) {
        setBookingRequests(res.data.data);
      }
    } catch (err) {
      console.error('Failed to load booking requests:', err);
    } finally {
      setLoadingRequests(false);
    }
  };

  const fetchActiveRentals = async () => {
    setLoadingRentals(true);
    try {
      const res = await apiClient.get('/owner/active-rentals');
      if (res.data?.data) {
        setActiveRentals(res.data.data);
      }
    } catch (err) {
      console.error('Failed to load active rentals:', err);
    } finally {
      setLoadingRentals(false);
    }
  };

  // Sign In / Sign Up handler
  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError(null);

    try {
      if (authMode === 'login') {
        const res = await apiClient.post('/auth/login', {
          email: authEmail.trim(),
          password: authPassword
        });
        const data = res.data?.data;
        if (data?.access_token) {
          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('owner_user', JSON.stringify(data.user));
          setToken(data.access_token);
          setUser(data.user);
        }
      } else {
        if (authPassword !== authConfirmPassword) {
          setAuthError('Passwords do not match.');
          setAuthLoading(false);
          return;
        }
        const res = await apiClient.post('/auth/register', {
          full_name: authFullName.trim(),
          email: authEmail.trim(),
          phone: authPhone.trim(),
          password: authPassword,
          confirm_password: authConfirmPassword,
          role: 'owner'
        });
        const data = res.data?.data;
        if (data?.access_token) {
          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('owner_user', JSON.stringify(data.user));
          setToken(data.access_token);
          setUser(data.user);
        }
      }
    } catch (err: any) {
      console.error('Owner auth error:', err);
      const detail = err.response?.data?.detail;
      const message = err.response?.data?.message;
      let displayError = 'Authentication failed. Please verify credentials.';
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
    localStorage.removeItem('owner_user');
    setToken(null);
    setUser(null);
    setBikes([]);
    setBookingRequests([]);
    setActiveRentals([]);
  };

  const handleAddCustomTariff = () => {
    if (customHours <= 0 || customPrice <= 0) return;
    const filtered = newTariffs.filter(t => t.hours !== customHours);
    const updated = [...filtered, { hours: customHours, price: customPrice }].sort((a, b) => a.hours - b.hours);
    setNewTariffs(updated);
  };

  const handleRemoveTariff = (hours: number) => {
    setNewTariffs(newTariffs.filter(t => t.hours !== hours));
  };

  // Add new scooty to database
  const handleAddBike = async (e: React.FormEvent) => {
    e.preventDefault();
    setAddBikeLoading(true);
    setAddBikeMsg(null);
    try {
      const payload = {
        bike_name: newBikeName || `${newBrand} ${newModel}`,
        name: newBikeName || `${newBrand} ${newModel}`,
        brand: newBrand,
        model: newModel,
        registration_number: newRegNo.toUpperCase(),
        color: newColor,
        fuel_type: newFuel,
        ownership_type: 'self',
        km_driven: newKm,
        daily_rent: newDailyRent,
        hourly_rate: newHourlyRate,
        security_deposit: newDeposit,
        tariffs: newTariffs
      };
      await apiClient.post('/owner/bikes', payload);
      setAddBikeMsg({ type: 'success', text: 'Scooty submitted to database with tariffs! Awaiting admin verification.' });
      fetchOwnerBikes();
      setTimeout(() => {
        setShowAddBikeModal(false);
        setAddBikeMsg(null);
        setNewBikeName('');
        setNewRegNo('');
      }, 1500);
    } catch (err: any) {
      setAddBikeMsg({ type: 'error', text: err.response?.data?.detail || 'Failed to add scooty to database.' });
    } finally {
      setAddBikeLoading(false);
    }
  };

  // Toggle COD cash receipt status
  const handleToggleCashStatus = async (assignmentId: string, markReceived: boolean) => {
    setCashActionLoading(assignmentId);
    try {
      await apiClient.post(`/owner/assignments/${assignmentId}/cash-status`, {
        cash_received: markReceived
      });
      fetchActiveRentals();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update cash status.');
    } finally {
      setCashActionLoading(null);
    }
  };

  // Accept or reject booking request
  const handleBookingDecision = async (bookingId: string, decision: 'accept' | 'reject') => {
    let rejection_reason: string | undefined = undefined;
    if (decision === 'reject') {
      const entered = window.prompt('Please enter a reason for rejecting this booking (optional):');
      if (entered === null) return; // user cancelled prompt
      rejection_reason = entered.trim() || 'Rejected by owner';
    }

    setRequestActionLoading(bookingId);
    try {
      const res = await apiClient.post(`/owner/booking-requests/${bookingId}/decision`, {
        decision,
        accepted: decision === 'accept',
        rejection_reason,
      });
      fetchBookingRequests();
      fetchActiveRentals();
      fetchOwnerBikes();
      if (decision === 'reject' && res.data?.data?.refund_amount) {
        alert(`Booking rejected. ₹${res.data.data.refund_amount} has been automatically refunded to the driver's wallet.`);
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update booking status.');
    } finally {
      setRequestActionLoading(null);
    }
  };

  // Return inspection and deposit release
  const handleCompleteReturnInspection = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inspectingRental) return;
    setInspectionSubmitting(true);
    setInspectionResult(null);

    const deposit = inspectingRental.security_deposit_amount;
    const netRefund = Math.max(0, deposit - damageCharge);

    try {
      await apiClient.post('/owner/return-inspection', {
        assignment_id: inspectingRental.id,
        is_damaged: damageCharge > 0,
        damage_charge: damageCharge,
        notes: inspectionNotes
      });
      setInspectionResult({
        type: 'success',
        text: `Inspection recorded in database! Net deposit of ₹${netRefund} (₹${deposit} - ₹${damageCharge} damage) refunded to driver. Scooty returned to Available.`
      });
      fetchActiveRentals();
      fetchOwnerBikes();
      setTimeout(() => {
        setInspectingRental(null);
        setInspectionResult(null);
      }, 1800);
    } catch (err: any) {
      setInspectionResult({ type: 'error', text: err.response?.data?.detail || 'Return inspection failed.' });
    } finally {
      setInspectionSubmitting(false);
    }
  };

  // Update Owner Profile / Bank Details
  const handleSaveBankDetails = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.put('/owner/profile', {
        business_name: businessName,
        bank_account_number: bankAccount,
        bank_ifsc: bankIfsc
      });
      setKycSuccess('Bank payout credentials updated in database for admin verification.');
      validateSession();
      setTimeout(() => setKycSuccess(null), 3000);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update bank payout credentials.');
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
    if (!name) return 'OW';
    return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() || 'OW';
  };

  const getBikeImageUrl = (bike: Bike): string => {
    const img = bike.images?.[0];
    if (!img) return 'https://images.unsplash.com/photo-1558981806-ec527fa84c39?auto=format&fit=crop&w=600&q=80';
    if (typeof img === 'string') return img;
    return img.image_url || 'https://images.unsplash.com/photo-1558981806-ec527fa84c39?auto=format&fit=crop&w=600&q=80';
  };

  const filteredFleet = bikes.filter(b =>
    b.bike_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    b.registration_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
    b.brand.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Dynamic Revenue Calculation
  const activeRentalsRevenue = activeRentals.reduce((sum, r) => sum + (r.daily_rent_amount || 0), 0);
  const netOwnerPayout = Math.round(activeRentalsRevenue * 0.9);

  // =========================================================================
  // 1. FIRST: SIGN IN / SIGN UP SCREEN (If not authenticated)
  // =========================================================================
  if (!token || !user) {
    return (
      <div className="min-h-screen bg-[#f4f8f6] flex flex-col justify-center items-center p-4 font-sans text-slate-800">
        <div className="w-full max-w-md bg-white border border-slate-200/80 rounded-3xl p-8 shadow-sm">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-11 h-11 rounded-2xl bg-emerald-100 flex items-center justify-center text-emerald-800 font-bold shadow-xs">
              <BikeIcon className="w-6 h-6 text-emerald-700" />
            </div>
            <div>
              <h2 className="text-xl font-extrabold text-slate-900 tracking-tight">VeloRent Fleet</h2>
              <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">PORT 6782 • FLEET PARTNERS</p>
            </div>
          </div>

          <div className="flex bg-slate-100 p-1 rounded-2xl mb-6">
            <button
              onClick={() => { setAuthMode('login'); setAuthError(null); }}
              className={`flex-1 py-2 text-xs font-bold rounded-xl transition ${
                authMode === 'login' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => { setAuthMode('register'); setAuthError(null); }}
              className={`flex-1 py-2 text-xs font-bold rounded-xl transition ${
                authMode === 'register' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              Sign Up
            </button>
          </div>

          {authError && (
            <div className="mb-4 p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs font-semibold text-rose-700 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{authError}</span>
            </div>
          )}

          <form onSubmit={handleAuthSubmit} className="space-y-4">
            {authMode === 'register' && (
              <>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Owner / Fleet Name</label>
                  <div className="relative">
                    <UserIcon className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="text"
                      required
                      placeholder="e.g. Rajesh Sharma"
                      value={authFullName}
                      onChange={(e) => setAuthFullName(e.target.value)}
                      className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Contact Phone (10 Digits)</label>
                  <div className="relative">
                    <Phone className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="tel"
                      required
                      placeholder="e.g. 9845012345"
                      value={authPhone}
                      onChange={(e) => setAuthPhone(e.target.value)}
                      className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                    />
                  </div>
                </div>
              </>
            )}

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Email Address</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  required
                  placeholder="owner@velorent.com"
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
                  placeholder="Minimum 8 characters"
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

            {authMode === 'register' && (
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Confirm Password</label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    placeholder="Repeat password"
                    value={authConfirmPassword}
                    onChange={(e) => setAuthConfirmPassword(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                  />
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={authLoading}
              className="w-full mt-2 py-3 bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-xs rounded-xl shadow-xs transition flex items-center justify-center gap-2"
            >
              {authLoading ? (
                <span>Connecting to Database...</span>
              ) : (
                <>
                  <span>{authMode === 'login' ? 'Sign In to Fleet Portal' : 'Register as Fleet Partner'}</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 pt-4 border-t border-slate-100 flex flex-col items-center gap-2 text-[11px] text-slate-500">
            <div className="flex items-center gap-2">
              <span>Switch Portal:</span>
              <a href={getPortalUrl(3110)} className="font-bold text-emerald-800 hover:underline">
                Driver Portal (3110)
              </a>
              <span>•</span>
              <a href={getPortalUrl(5431)} className="font-bold text-purple-700 hover:underline flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5 text-purple-600" />
                <span>Admin Console (5431)</span>
              </a>
            </div>
            <span>Fleet Management • Database Authentication (PostgreSQL)</span>
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
              <BikeIcon className="w-5 h-5 text-emerald-700" />
            </div>
            <div>
              <h1 className="font-bold text-slate-900 text-base leading-tight">VeloRent</h1>
              <p className="text-[10px] font-bold text-slate-400 tracking-wider uppercase">FLEET PLATFORM</p>
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
                <p className="text-[11px] text-emerald-700 font-medium">Fleet Partner</p>
              </div>
            </div>
            <ChevronDown className="w-4 h-4 text-slate-400" />
          </div>

          {/* Section Category */}
          <div className="mt-6 mb-2">
            <p className="text-[11px] font-bold text-slate-400 tracking-wider uppercase px-2">FLEET OPERATIONS</p>
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
              onClick={() => setActiveTab('fleet')}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                activeTab === 'fleet'
                  ? 'bg-emerald-50 text-emerald-900 border border-emerald-100 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <div className="flex items-center gap-3">
                <BikeIcon className="w-4 h-4" />
                <span>My Fleet</span>
              </div>
              <span className="text-[10px] font-bold bg-slate-100 text-slate-700 px-2 py-0.5 rounded-full">
                {bikes.length}
              </span>
            </button>

            <button
              onClick={() => setActiveTab('requests')}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                activeTab === 'requests'
                  ? 'bg-emerald-50 text-emerald-900 border border-emerald-100 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <div className="flex items-center gap-3">
                <FileText className="w-4 h-4" />
                <span>Booking Requests</span>
              </div>
              {bookingRequests.filter(r => r.status === 'pending').length > 0 && (
                <span className="px-2 py-0.5 text-[10px] font-bold bg-amber-100 text-amber-800 rounded-full">
                  {bookingRequests.filter(r => r.status === 'pending').length} New
                </span>
              )}
            </button>

            <button
              onClick={() => setActiveTab('rentals')}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                activeTab === 'rentals'
                  ? 'bg-emerald-50 text-emerald-900 border border-emerald-100 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <div className="flex items-center gap-3">
                <Clock className="w-4 h-4" />
                <span>Active Rentals</span>
              </div>
              <span className="text-[10px] font-bold bg-slate-100 text-slate-700 px-2 py-0.5 rounded-full">
                {activeRentals.length}
              </span>
            </button>

            <button
              onClick={() => setActiveTab('earnings')}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                activeTab === 'earnings'
                  ? 'bg-emerald-50 text-emerald-900 border border-emerald-100 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <div className="flex items-center gap-3">
                <DollarSign className="w-4 h-4" />
                <span>Earnings & Payouts</span>
              </div>
              <span className="text-[11px] font-bold text-emerald-800">₹{netOwnerPayout}</span>
            </button>

            <button
              onClick={() => setActiveTab('kyc')}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                activeTab === 'kyc'
                  ? 'bg-emerald-50 text-emerald-900 border border-emerald-100 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <div className="flex items-center gap-3">
                <Building className="w-4 h-4" />
                <span>KYC & Bank Account</span>
              </div>
              <span className={`w-2 h-2 rounded-full ${user.is_verified ? 'bg-emerald-500' : 'bg-amber-500'}`}></span>
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
              Fleet management & insurance guidelines in one place.
            </p>
            <button
              onClick={() => alert("Fleet Partner Support: fleet-support@velorent.com")}
              className="mt-3 w-full bg-white hover:bg-emerald-50 text-emerald-950 font-bold text-[11px] py-1.5 px-3 rounded-lg text-center shadow-xs transition"
            >
              Explore help center
            </button>
          </div>

          {/* Quick Portal Switcher */}
          <div className="mt-3 p-2 bg-slate-50 border border-slate-200/70 rounded-xl space-y-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block px-1">Other Portals</span>
            <a
              href={getPortalUrl(5431)}
              className="flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold text-purple-700 hover:bg-purple-50 transition"
              title="Open Admin Portal on Port 5431"
            >
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-3.5 h-3.5 text-purple-600" />
                <span>Admin Console</span>
              </div>
              <span className="text-[10px] text-purple-500 font-mono">:5431</span>
            </a>
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
                placeholder="Search fleet, registration..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 pr-4 py-1.5 bg-slate-50 border border-slate-200/80 rounded-full text-xs text-slate-700 w-64 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition"
              />
            </div>

            <button
              onClick={() => setShowAddBikeModal(true)}
              className="flex items-center gap-2 px-3.5 py-1.5 bg-emerald-700 hover:bg-emerald-800 text-white rounded-full text-xs font-bold transition shadow-xs"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>List New Scooty</span>
            </button>

            {/* Portal Switcher Buttons */}
            <div className="hidden md:flex items-center gap-1 bg-slate-100 p-1 rounded-full text-[11px] font-bold">
              <a
                href={getPortalUrl(3110)}
                className="px-2.5 py-1 text-slate-500 hover:text-slate-900 hover:bg-white/60 rounded-full transition"
                title="Open Driver Portal (Port 3110)"
              >
                Driver
              </a>
              <span className="px-2.5 py-1 bg-white text-emerald-900 rounded-full shadow-xs">
                Owner
              </span>
              <a
                href={getPortalUrl(5431)}
                className="px-2.5 py-1 text-purple-700 hover:bg-purple-100/70 rounded-full transition flex items-center gap-1"
                title="Open Admin Governance Console (Port 5431)"
              >
                <ShieldCheck className="w-3.5 h-3.5 text-purple-600" />
                <span>Admin</span>
              </a>
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
                  Your fleet operations, incoming booking requests and earnings overview for today.
                </p>

                <div className="flex items-center gap-2 mt-4">
                  <span className="px-3 py-1 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full text-xs font-semibold text-white">
                    Fleet platform
                  </span>
                  <span className="px-3 py-1 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full text-xs font-medium text-emerald-100">
                    Live Database Connected
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={loadAllOwnerData}
                  className="px-4 py-2 bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/20 rounded-full text-xs font-semibold text-white flex items-center gap-2 shadow-xs transition"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  <span>Refresh overview</span>
                </button>
              </div>
            </div>
          </div>

          {/* ========================================================================= */}
          {/* 4 KPI METRIC CARDS */}
          {/* ========================================================================= */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500">Total fleet</span>
                <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center">
                  <BikeIcon className="w-4 h-4" />
                </div>
              </div>
              <div className="my-2">
                <span className="text-2xl font-extrabold text-slate-900">{bikes.length}</span>
              </div>
              <div className="flex items-center gap-1.5 text-[11px] font-bold text-emerald-700">
                <span>↗ {bikes.filter(b => b.status === 'available').length} available</span>
                <span className="font-normal text-slate-400">in database</span>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500">Booking requests</span>
                <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-700 flex items-center justify-center">
                  <FileText className="w-4 h-4" />
                </div>
              </div>
              <div className="my-2">
                <span className="text-2xl font-extrabold text-slate-900">
                  {bookingRequests.filter(r => r.status === 'pending').length}
                </span>
              </div>
              <div className="flex items-center gap-1.5 text-[11px] font-bold text-amber-700">
                <span>Needs review</span>
                <span className="font-normal text-slate-400">awaiting action</span>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500">Active rentals</span>
                <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center">
                  <Clock className="w-4 h-4" />
                </div>
              </div>
              <div className="my-2">
                <span className="text-2xl font-extrabold text-slate-900">{activeRentals.length}</span>
              </div>
              <div className="flex items-center gap-1.5 text-[11px] font-bold text-blue-700">
                <span>↗ On trip</span>
                <span className="font-normal text-slate-400">ready for return</span>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500">Estimated Net Payout</span>
                <div className="w-8 h-8 rounded-lg bg-purple-50 text-purple-700 flex items-center justify-center">
                  <DollarSign className="w-4 h-4" />
                </div>
              </div>
              <div className="my-2">
                <span className="text-2xl font-extrabold text-slate-900">₹{netOwnerPayout}</span>
              </div>
              <div className="flex items-center gap-1.5 text-[11px] font-bold text-purple-700">
                <span>↗ 90% net payout</span>
                <span className="font-normal text-slate-400">after 10% platform fee</span>
              </div>
            </div>
          </div>

          {/* ========================================================================= */}
          {/* TWO-COLUMN WORKSPACE MODULE */}
          {/* ========================================================================= */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left 8 Cols */}
            <div className="lg:col-span-8 bg-white rounded-2xl border border-slate-200/80 p-6 shadow-xs">
              {activeTab === 'dashboard' || activeTab === 'fleet' ? (
                <div>
                  <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
                    <div>
                      <h3 className="text-sm font-bold text-slate-900">Fleet Inventory in Database</h3>
                      <p className="text-xs text-slate-500 mt-0.5">Manage listed scooties, RC documents and daily rent</p>
                    </div>
                    <button
                      onClick={() => setShowAddBikeModal(true)}
                      className="text-xs font-bold text-emerald-700 hover:text-emerald-800 flex items-center gap-1"
                    >
                      <Plus className="w-3.5 h-3.5" />
                      <span>Add new scooty</span>
                    </button>
                  </div>

                  {loadingBikes ? (
                    <div className="p-12 text-center text-slate-400">
                      <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-emerald-600" />
                      <p className="text-xs">Loading fleet from database...</p>
                    </div>
                  ) : filteredFleet.length === 0 ? (
                    <div className="p-12 text-center text-slate-400 border border-dashed border-slate-200 rounded-2xl">
                      <BikeIcon className="w-10 h-10 mx-auto mb-2 text-slate-300" />
                      <p className="text-sm font-bold text-slate-700">No Scooties Listed Yet</p>
                      <p className="text-xs mt-1 text-slate-500">List your scooties with RC documents to start earning daily rent.</p>
                      <button
                        onClick={() => setShowAddBikeModal(true)}
                        className="mt-4 px-4 py-2 bg-emerald-700 text-white rounded-xl text-xs font-bold"
                      >
                        List First Scooty
                      </button>
                    </div>
                  ) : (
                    <div className="divide-y divide-slate-100">
                      {filteredFleet.map(bike => (
                        <div key={bike.id} className="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                          <div className="flex items-center gap-3.5">
                            <img
                              src={getBikeImageUrl(bike)}
                              alt={bike.bike_name}
                              className="w-16 h-12 object-cover rounded-xl bg-slate-100 border border-slate-200 shrink-0"
                            />
                            <div>
                              <h4 className="text-xs font-bold text-slate-900">{bike.bike_name}</h4>
                              <p className="text-[11px] text-slate-500">{bike.registration_number} • {bike.brand} • {bike.fuel_type}</p>
                              <p className="text-[11px] font-semibold text-slate-700 mt-0.5">
                                Daily Rent: ₹{bike.pricing?.daily_rent || 0} | Deposit: ₹{bike.pricing?.security_deposit || 0}
                              </p>
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            <span className={`px-2.5 py-1 text-[11px] font-bold rounded-full ${
                              bike.status === 'available' ? 'bg-emerald-100 text-emerald-800' :
                              bike.status === 'rented' || bike.status === 'assigned' ? 'bg-blue-100 text-blue-800' : 'bg-slate-100 text-slate-700'
                            }`}>
                              {bike.status.toUpperCase()}
                            </span>

                            <span className="px-2 py-1 text-[10px] font-bold bg-slate-50 border border-slate-200 text-slate-600 rounded-lg">
                              {bike.verification_status.toUpperCase()}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : activeTab === 'requests' ? (
                /* Booking Requests Tab */
                <div>
                  <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
                    <div>
                      <h3 className="text-sm font-bold text-slate-900">Incoming Booking Requests</h3>
                      <p className="text-xs text-slate-500 mt-0.5">Accept to dispatch scooty and lock driver rent & deposit</p>
                    </div>
                  </div>

                  {bookingRequests.length === 0 ? (
                    <div className="p-12 text-center text-slate-400 border border-dashed border-slate-200 rounded-2xl">
                      <FileText className="w-10 h-10 mx-auto mb-2 text-slate-300" />
                      <p className="text-sm font-bold text-slate-700">No Booking Requests Found</p>
                      <p className="text-xs mt-1 text-slate-500">When drivers book your scooties, their requests will appear here.</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {bookingRequests.map(req => (
                        <div key={req.id} className="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-3">
                          <div className="flex items-start justify-between">
                            <div>
                              <div className="flex items-center gap-2">
                                <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                                  req.status === 'approved' ? 'bg-emerald-100 text-emerald-800' :
                                  req.status === 'rejected' ? 'bg-rose-100 text-rose-800' :
                                  req.status === 'refunded' ? 'bg-purple-100 text-purple-800' :
                                  req.status === 'cancelled' ? 'bg-slate-200 text-slate-700' :
                                  'bg-amber-100 text-amber-800'
                                }`}>
                                  {req.status === 'pending' ? '⏳ Pending Review' :
                                   req.status === 'approved' ? '✓ Approved & Final' :
                                   req.status === 'rejected' ? '✕ Rejected' :
                                   req.status === 'refunded' ? '↩ Rejected & Refunded' :
                                   req.status === 'cancelled' ? '✕ Cancelled by Driver' : req.status}
                                </span>
                                <span className="text-[10px] font-bold bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full">
                                  {req.rental_hours || 24} Hours Duration
                                </span>
                                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                                  (req.payment_method || 'cod').toLowerCase() === 'cod' ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'
                                }`}>
                                  {(req.payment_method || 'cod').toUpperCase() === 'COD' ? '💵 Cash on Delivery' : '⚡ Online UPI'}
                                </span>
                              </div>

                              <h4 className="text-sm font-bold text-slate-900 mt-1">{req.bike_name} ({req.registration_number})</h4>
                              <p className="text-xs text-slate-600 mt-0.5">
                                Driver: <strong className="text-slate-900">{req.driver_name}</strong> {req.driver_phone ? `(Ph: ${req.driver_phone})` : ''}
                              </p>
                              {req.driver_address && (
                                <p className="text-[11px] text-slate-500 mt-0.5">
                                  Address: {req.driver_address}
                                </p>
                              )}
                              {req.message && <p className="text-xs text-slate-500 italic mt-1">"{req.message}"</p>}
                              {req.rejected_reason && (
                                <p className="text-[11px] text-rose-700 bg-rose-50 px-2.5 py-1 rounded-lg border border-rose-200 mt-1.5 font-medium">
                                  <strong>Note:</strong> {req.rejected_reason}
                                </p>
                              )}
                            </div>

                            <div className="text-right">
                              <p className="text-xs text-slate-400">Total Rent</p>
                              <p className="text-sm font-bold text-slate-900">₹{req.total_amount || req.daily_rent}</p>
                              {(req.payment_method || 'cod').toLowerCase() !== 'cod' && (
                                <p className="text-[11px] text-slate-500">Deposit: ₹{req.security_deposit}</p>
                              )}
                            </div>
                          </div>

                          {req.status === 'pending' && (
                            <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-200">
                              <button
                                onClick={() => handleBookingDecision(req.id, 'reject')}
                                disabled={requestActionLoading === req.id}
                                className="px-4 py-1.5 border border-slate-200 bg-white hover:bg-slate-100 text-slate-700 text-xs font-bold rounded-xl"
                              >
                                Reject
                              </button>
                              <button
                                onClick={() => handleBookingDecision(req.id, 'accept')}
                                disabled={requestActionLoading === req.id}
                                className="px-4 py-1.5 bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-bold rounded-xl shadow-xs"
                              >
                                {requestActionLoading === req.id ? 'Processing...' : (req.payment_method || 'cod').toLowerCase() === 'cod' ? 'Accept (Cash on Delivery)' : 'Accept & Lock Deposit'}
                              </button>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : activeTab === 'rentals' ? (
                /* Active Rentals Tab */
                <div>
                  <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
                    <div>
                      <h3 className="text-sm font-bold text-slate-900">Active Rentals & Vehicle Return</h3>
                      <p className="text-xs text-slate-500 mt-0.5">Manage cash receipt status, conduct return inspection and deposit refund</p>
                    </div>
                  </div>

                  {activeRentals.length === 0 ? (
                    <div className="p-12 text-center text-slate-400 border border-dashed border-slate-200 rounded-2xl">
                      <Clock className="w-10 h-10 mx-auto mb-2 text-slate-300" />
                      <p className="text-sm font-bold text-slate-700">No Active Rentals in Database</p>
                      <p className="text-xs mt-1 text-slate-500">When you accept booking requests, dispatched scooties appear here.</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {activeRentals.map(rental => (
                        <div key={rental.id} className="p-4 bg-slate-50 rounded-2xl border border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-4">
                          <div>
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                              <h4 className="text-sm font-bold text-slate-900">{rental.bike_name}</h4>
                              <span className="text-xs font-semibold text-slate-500">({rental.registration_number})</span>

                              <span className="text-[10px] font-bold bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">
                                {rental.rental_hours || 24}h Rental
                              </span>

                              {(rental.payment_method || 'cod').toLowerCase() === 'cod' ? (
                                rental.cash_received ? (
                                  <span className="text-[10px] font-bold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full flex items-center gap-1">
                                    ✓ Cash Received
                                  </span>
                                ) : (
                                  <span className="text-[10px] font-bold bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full flex items-center gap-1">
                                    ⏳ Cash Pending (COD)
                                  </span>
                                )
                              ) : (
                                <span className="text-[10px] font-bold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full">
                                  ⚡ Paid Online
                                </span>
                              )}

                              {rental.cod_admin_escalated && (
                                <span className="text-[10px] font-bold bg-rose-100 text-rose-800 px-2 py-0.5 rounded-full">
                                  🚨 Unpaid &gt; 10h (Escalated to Admin)
                                </span>
                              )}
                            </div>

                            <p className="text-xs text-slate-600 mt-1">
                              Rented to: <strong>{rental.driver_name}</strong> {rental.driver_phone ? `• Phone: ${rental.driver_phone}` : ''}
                            </p>
                            <p className="text-xs text-slate-500 mt-0.5">
                              Assigned: {new Date(rental.assigned_at).toLocaleString()} • Rent: ₹{rental.total_rent_amount || rental.daily_rent_amount} • Locked Deposit: ₹{rental.security_deposit_amount}
                            </p>
                          </div>

                          <div className="flex items-center gap-2 shrink-0">
                            {/* COD Cash Receipt Toggle Button */}
                            {(rental.payment_method || 'cod').toLowerCase() === 'cod' && (
                              rental.cash_received ? (
                                <button
                                  onClick={() => handleToggleCashStatus(rental.id, false)}
                                  disabled={cashActionLoading === rental.id}
                                  className="px-3 py-2 border border-slate-200 bg-white hover:bg-rose-50 hover:text-rose-700 text-slate-600 rounded-xl text-xs font-bold transition shadow-xs"
                                >
                                  {cashActionLoading === rental.id ? 'Updating...' : 'Mark Not Received'}
                                </button>
                              ) : (
                                <button
                                  onClick={() => handleToggleCashStatus(rental.id, true)}
                                  disabled={cashActionLoading === rental.id}
                                  className="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold transition shadow-xs flex items-center gap-1.5"
                                >
                                  <span>{cashActionLoading === rental.id ? 'Updating...' : '✓ Mark Cash Received'}</span>
                                </button>
                              )
                            )}

                            <button
                              onClick={() => {
                                setInspectingRental(rental);
                                setDamageCharge(0);
                                setInspectionNotes('Vehicle inspected. No major dents or mechanical issues.');
                                setInspectionResult(null);
                              }}
                              className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold shadow-xs shrink-0"
                            >
                              Conduct Return Inspection
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : activeTab === 'earnings' ? (
                /* Earnings View */
                <div>
                  <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
                    <div>
                      <h3 className="text-sm font-bold text-slate-900">Earnings & Payout Ledger</h3>
                      <p className="text-xs text-slate-500 mt-0.5">Calculated from active and completed rentals in database</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                      <p className="text-[11px] text-slate-400 font-semibold uppercase">Gross Active Rental Volume</p>
                      <p className="text-xl font-extrabold text-slate-900 mt-1">₹{activeRentalsRevenue}</p>
                    </div>
                    <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                      <p className="text-[11px] text-slate-400 font-semibold uppercase">Platform Fee (10%)</p>
                      <p className="text-xl font-extrabold text-rose-600 mt-1">-₹{Math.round(activeRentalsRevenue * 0.1)}</p>
                    </div>
                    <div className="p-4 bg-emerald-50 rounded-xl border border-emerald-200">
                      <p className="text-[11px] text-emerald-800 font-semibold uppercase">Net Settled to Bank (90%)</p>
                      <p className="text-xl font-extrabold text-emerald-950 mt-1">₹{netOwnerPayout}</p>
                    </div>
                  </div>
                </div>
              ) : (
                /* KYC View */
                <div>
                  <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
                    <div>
                      <h3 className="text-sm font-bold text-slate-900">Owner KYC & Bank Payout Details</h3>
                      <p className="text-xs text-slate-500 mt-0.5">Register bank account to receive weekly payouts</p>
                    </div>
                  </div>

                  {kycSuccess && (
                    <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-800 font-semibold mb-4">
                      {kycSuccess}
                    </div>
                  )}

                  <form onSubmit={handleSaveBankDetails} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-bold text-slate-700 mb-1">Business / Fleet Entity Name</label>
                        <input
                          type="text"
                          placeholder="e.g. Urban EV Rentals"
                          value={businessName}
                          onChange={(e) => setBusinessName(e.target.value)}
                          className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-bold text-slate-700 mb-1">Bank Account Number</label>
                        <input
                          type="text"
                          required
                          placeholder="e.g. 50100492814590"
                          value={bankAccount}
                          onChange={(e) => setBankAccount(e.target.value)}
                          className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-bold text-slate-700 mb-1">Bank IFSC Code</label>
                        <input
                          type="text"
                          required
                          placeholder="e.g. HDFC0001234"
                          value={bankIfsc}
                          onChange={(e) => setBankIfsc(e.target.value.toUpperCase())}
                          className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 uppercase focus:outline-none focus:ring-1 focus:ring-emerald-500"
                        />
                      </div>
                    </div>

                    <div className="pt-3 border-t border-slate-100 flex justify-end">
                      <button
                        type="submit"
                        className="px-5 py-2 bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-bold rounded-xl shadow-xs"
                      >
                        Save Bank Details to Database
                      </button>
                    </div>
                  </form>
                </div>
              )}
            </div>

            {/* Right 4 Cols */}
            <div className="lg:col-span-4 bg-white rounded-2xl border border-slate-200/80 p-6 shadow-xs flex flex-col justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-900 leading-tight">Fleet operations</h3>
                <p className="text-xs text-slate-500 mt-0.5 mb-5">Open a workspace module to take action.</p>

                <div className="space-y-3">
                  <div
                    onClick={() => setShowAddBikeModal(true)}
                    className="p-3.5 bg-slate-50 hover:bg-emerald-50/70 border border-slate-100 hover:border-emerald-200 rounded-xl cursor-pointer transition flex items-center justify-between group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center">
                        <Plus className="w-4 h-4" />
                      </div>
                      <div>
                        <p className="text-xs font-bold text-slate-900 leading-tight">Add new scooty</p>
                        <p className="text-[11px] text-slate-500 mt-0.5">List RC, pricing & photos</p>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-emerald-700 group-hover:translate-x-0.5 transition" />
                  </div>

                  <div
                    onClick={() => setActiveTab('requests')}
                    className="p-3.5 bg-slate-50 hover:bg-emerald-50/70 border border-slate-100 hover:border-emerald-200 rounded-xl cursor-pointer transition flex items-center justify-between group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-lg bg-amber-100 text-amber-800 flex items-center justify-center">
                        <FileText className="w-4 h-4" />
                      </div>
                      <div>
                        <p className="text-xs font-bold text-slate-900 leading-tight">Booking requests</p>
                        <p className="text-[11px] text-slate-500 mt-0.5">Review & lock driver deposits</p>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-emerald-700 group-hover:translate-x-0.5 transition" />
                  </div>

                  <div
                    onClick={() => setActiveTab('rentals')}
                    className="p-3.5 bg-slate-50 hover:bg-emerald-50/70 border border-slate-100 hover:border-emerald-200 rounded-xl cursor-pointer transition flex items-center justify-between group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-lg bg-blue-100 text-blue-800 flex items-center justify-center">
                        <Clock className="w-4 h-4" />
                      </div>
                      <div>
                        <p className="text-xs font-bold text-slate-900 leading-tight">Inspect return vehicle</p>
                        <p className="text-[11px] text-slate-500 mt-0.5">Record damage & refund deposit</p>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-emerald-700 group-hover:translate-x-0.5 transition" />
                  </div>

                  <div
                    onClick={() => setActiveTab('kyc')}
                    className="p-3.5 bg-slate-50 hover:bg-emerald-50/70 border border-slate-100 hover:border-emerald-200 rounded-xl cursor-pointer transition flex items-center justify-between group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-lg bg-purple-100 text-purple-800 flex items-center justify-center">
                        <Building className="w-4 h-4" />
                      </div>
                      <div>
                        <p className="text-xs font-bold text-slate-900 leading-tight">Bank payout setup</p>
                        <p className="text-[11px] text-slate-500 mt-0.5">Direct 90% net revenue transfer</p>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-emerald-700 group-hover:translate-x-0.5 transition" />
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
                <span className="flex items-center gap-1.5 font-semibold text-emerald-800">
                  <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                  Live Database Connected
                </span>
                <span>Port 6782</span>
              </div>
            </div>
          </div>
        </main>
      </div>

      {/* Add Scooty Modal */}
      {showAddBikeModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-100 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="text-base font-bold text-slate-900">List New Scooty for Rent</h3>
              <button onClick={() => setShowAddBikeModal(false)} className="text-slate-400 hover:text-slate-700">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddBike} className="mt-4 space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Brand</label>
                  <select
                    value={newBrand}
                    onChange={(e) => setNewBrand(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-800"
                  >
                    <option value="Honda">Honda</option>
                    <option value="Ather">Ather (EV)</option>
                    <option value="TVS">TVS</option>
                    <option value="Ola">Ola (EV)</option>
                    <option value="Suzuki">Suzuki</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Model</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Activa 6G / 450X"
                    value={newModel}
                    onChange={(e) => setNewModel(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-800"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Registration Number</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. KA-01-AB-1234"
                    value={newRegNo}
                    onChange={(e) => setNewRegNo(e.target.value.toUpperCase())}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-800 uppercase"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Fuel Type</label>
                  <select
                    value={newFuel}
                    onChange={(e) => setNewFuel(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-800"
                  >
                    <option value="petrol">Petrol</option>
                    <option value="electric">Electric (EV)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Base Hourly Rate (₹/hr)</label>
                  <input
                    type="number"
                    min="10"
                    step="5"
                    value={newHourlyRate}
                    onChange={(e) => setNewHourlyRate(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-900"
                  />
                  <p className="text-[10px] text-slate-400 mt-0.5">Fallback rate per hour</p>
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Daily Rent (24h) (₹)</label>
                  <input
                    type="number"
                    min="100"
                    step="10"
                    value={newDailyRent}
                    onChange={(e) => setNewDailyRent(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-900"
                  />
                </div>
              </div>

              {/* Time-Based Tariff Setup */}
              <div className="p-3 bg-slate-50/80 rounded-xl border border-slate-200 space-y-2.5">
                <div className="flex items-center justify-between">
                  <label className="block text-xs font-bold text-slate-800">Time-Based Rental Tariffs</label>
                  <span className="text-[10px] text-emerald-700 font-semibold">{newTariffs.length} Active Packages</span>
                </div>
                <p className="text-[11px] text-slate-500">Configure time-based tariffs (e.g. 1 hr = ₹100, 2 hrs = ₹190, etc.)</p>

                <div className="flex flex-wrap gap-1.5 pt-1">
                  {newTariffs.map(t => (
                    <span key={t.hours} className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-white border border-slate-200 rounded-lg text-xs font-bold text-slate-800 shadow-xs">
                      <span>{t.hours} hr: ₹{t.price}</span>
                      <button
                        type="button"
                        onClick={() => handleRemoveTariff(t.hours)}
                        className="text-slate-400 hover:text-rose-600 font-extrabold ml-0.5"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>

                <div className="flex items-center gap-2 pt-2 border-t border-slate-200/60">
                  <div className="w-1/3">
                    <input
                      type="number"
                      min="1"
                      placeholder="Hours"
                      value={customHours}
                      onChange={(e) => setCustomHours(Number(e.target.value))}
                      className="w-full px-2.5 py-1.5 bg-white border border-slate-200 rounded-lg text-xs font-bold text-slate-800"
                    />
                  </div>
                  <div className="w-1/3">
                    <input
                      type="number"
                      min="10"
                      placeholder="₹ Price"
                      value={customPrice}
                      onChange={(e) => setCustomPrice(Number(e.target.value))}
                      className="w-full px-2.5 py-1.5 bg-white border border-slate-200 rounded-lg text-xs font-bold text-slate-800"
                    />
                  </div>
                  <button
                    type="button"
                    onClick={handleAddCustomTariff}
                    className="w-1/3 py-1.5 bg-slate-800 hover:bg-slate-900 text-white rounded-lg text-xs font-bold shadow-xs transition"
                  >
                    + Add Tariff
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Security Deposit (₹)</label>
                <input
                  type="number"
                  min="200"
                  step="100"
                  value={newDeposit}
                  onChange={(e) => setNewDeposit(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-900"
                />
              </div>

              {addBikeMsg && (
                <div className={`p-3 rounded-xl text-xs font-semibold ${
                  addBikeMsg.type === 'success' ? 'bg-emerald-50 text-emerald-800' : 'bg-rose-50 text-rose-800'
                }`}>
                  {addBikeMsg.text}
                </div>
              )}

              <div className="flex gap-2 justify-end pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowAddBikeModal(false)}
                  className="px-4 py-2 border border-slate-200 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={addBikeLoading}
                  className="px-5 py-2 bg-emerald-700 hover:bg-emerald-800 text-white rounded-xl text-xs font-bold shadow-xs"
                >
                  {addBikeLoading ? 'Writing to Database...' : 'Submit to Database'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Return & Damage Inspection Modal */}
      {inspectingRental && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-100">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="text-base font-bold text-slate-900">Vehicle Return Inspection</h3>
              <button onClick={() => setInspectingRental(null)} className="text-slate-400 hover:text-slate-700">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCompleteReturnInspection} className="mt-4 space-y-4">
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs">
                <p className="font-bold text-slate-900">{inspectingRental.bike_name} ({inspectingRental.registration_number})</p>
                <p className="text-slate-500 mt-0.5">Renter: {inspectingRental.driver_name} {inspectingRental.driver_phone ? `• Phone: ${inspectingRental.driver_phone}` : ''}</p>
                <p className="text-slate-700 font-semibold mt-1">Locked Security Deposit: ₹{inspectingRental.security_deposit_amount}</p>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Damage Assessment Deduction (₹)</label>
                <input
                  type="number"
                  min="0"
                  max={inspectingRental.security_deposit_amount}
                  value={damageCharge}
                  onChange={(e) => setDamageCharge(Number(e.target.value))}
                  className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm font-bold text-slate-900"
                />
                <p className="text-[11px] text-slate-400 mt-1">
                  Enter ₹0 if no damage. Any deducted amount covers repair costs.
                </p>
              </div>

              <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-200 text-xs flex justify-between items-center font-bold text-emerald-950">
                <span>Net Deposit to Refund to Driver:</span>
                <span className="text-sm text-emerald-800">
                  ₹{Math.max(0, inspectingRental.security_deposit_amount - damageCharge)}
                </span>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Inspection Notes</label>
                <textarea
                  rows={2}
                  value={inspectionNotes}
                  onChange={(e) => setInspectionNotes(e.target.value)}
                  className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800"
                ></textarea>
              </div>

              {inspectionResult && (
                <div className={`p-3 rounded-xl text-xs font-semibold ${
                  inspectionResult.type === 'success' ? 'bg-emerald-50 text-emerald-800' : 'bg-rose-50 text-rose-800'
                }`}>
                  {inspectionResult.text}
                </div>
              )}

              <div className="flex gap-2 justify-end pt-2">
                <button
                  type="button"
                  onClick={() => setInspectingRental(null)}
                  className="px-4 py-2 border border-slate-200 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={inspectionSubmitting}
                  className="px-5 py-2 bg-emerald-700 hover:bg-emerald-800 text-white rounded-xl text-xs font-bold shadow-xs"
                >
                  {inspectionSubmitting ? 'Recording in Database...' : 'Confirm Return & Release Deposit'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
