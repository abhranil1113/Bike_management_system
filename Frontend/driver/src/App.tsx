import React, { useState, useEffect } from 'react';
import {
  Bike as BikeIcon, Wallet, Search, Filter, ShieldCheck,
  Clock, AlertCircle, CheckCircle2, ChevronRight, X,
  ArrowUpRight, RefreshCw, FileText, Bell, LogOut, Lock,
  User as UserIcon, Phone, Mail, MapPin, Zap, Fuel, Activity,
  HelpCircle, Plus, ChevronDown, Check, ArrowRight, Eye, EyeOff,
  Upload, FileUp, Camera, ExternalLink, CheckCircle
} from 'lucide-react';
import { apiClient, getBackendBaseUrl, getPortalUrl } from '../../shared/api';
import type { Bike, ActiveAssignment, BookingRequest, WalletData, NotificationItem, User, DriverKycData } from '../../shared/types';

export default function DriverApp() {
  // Authentication & session state
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('access_token'));
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('driver_user');
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

  // Tab navigation
  const [activeTab, setActiveTab] = useState<'dashboard' | 'browse' | 'active_rental' | 'bookings' | 'wallet' | 'kyc'>('dashboard');

  // Real Database state (No hardcoded demo data)
  const [bikes, setBikes] = useState<Bike[]>([]);
  const [loadingBikes, setLoadingBikes] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedBrand, setSelectedBrand] = useState('all');
  const [selectedFuel, setSelectedFuel] = useState('all');
  const [maxPrice, setMaxPrice] = useState(2000);

  // Active assignment
  const [activeRental, setActiveRental] = useState<ActiveAssignment | null>(null);
  const [loadingRental, setLoadingRental] = useState(false);
  const [returnRequested, setReturnRequested] = useState(false);
  const [returnMessage, setReturnMessage] = useState<string | null>(null);

  // Bookings list
  const [myBookings, setMyBookings] = useState<BookingRequest[]>([]);
  const [loadingBookings, setLoadingBookings] = useState(false);

  // Wallet
  const [wallet, setWallet] = useState<WalletData>({ wallet_id: '', balance: 0, transactions: [] });
  const [loadingWallet, setLoadingWallet] = useState(false);
  const [showRechargeModal, setShowRechargeModal] = useState(false);
  const [rechargeAmount, setRechargeAmount] = useState(500);
  const [rechargeLoading, setRechargeLoading] = useState(false);
  const [rechargeMsg, setRechargeMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Selected bike for booking modal
  const [selectedBike, setSelectedBike] = useState<Bike | null>(null);
  const [selectedHours, setSelectedHours] = useState<number>(24);
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState<'cod' | 'razorpay'>('cod');
  const [handCashLoading, setHandCashLoading] = useState(false);
  const [handCashMsg, setHandCashMsg] = useState<string | null>(null);
  const [bookingMsg, setBookingMsg] = useState('');
  const [bookingLoading, setBookingLoading] = useState(false);
  const [bookingFeedback, setBookingFeedback] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // KYC form state
  const [kycData, setKycData] = useState<DriverKycData | null>(null);
  const [loadingKyc, setLoadingKyc] = useState(false);
  const [drivingLicense, setDrivingLicense] = useState('');
  const [licenseFile, setLicenseFile] = useState<File | null>(null);
  const [aadhaarNumber, setAadhaarNumber] = useState('');
  const [aadhaarFile, setAadhaarFile] = useState<File | null>(null);
  const [panNumber, setPanNumber] = useState('');
  const [panFile, setPanFile] = useState<File | null>(null);
  const [profilePicFile, setProfilePicFile] = useState<File | null>(null);
  const [address, setAddress] = useState('');
  const [emergencyName, setEmergencyName] = useState('');
  const [emergencyPhone, setEmergencyPhone] = useState('');
  const [kycLoading, setKycLoading] = useState(false);
  const [kycSuccess, setKycSuccess] = useState<string | null>(null);
  const [kycError, setKycError] = useState<string | null>(null);

  // Notifications
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [showNotifications, setShowNotifications] = useState(false);

  // Check if user navigated to /admin or /owner path on port 3110 and redirect
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const p = window.location.pathname.toLowerCase();
      if (p === '/admin' || p.startsWith('/admin/')) {
        window.location.href = getPortalUrl(5431);
      } else if (p === '/owner' || p.startsWith('/owner/')) {
        window.location.href = getPortalUrl(6782);
      }
    }
  }, []);

  // Verify session on mount
  useEffect(() => {
    if (token) {
      validateSession();
      loadAllDriverData();
    }
  }, [token]);

  const validateSession = async () => {
    try {
      const res = await apiClient.get('/auth/me');
      if (res.data?.data) {
        setUser(res.data.data);
        localStorage.setItem('driver_user', JSON.stringify(res.data.data));
      }
    } catch {
      handleLogout();
    }
  };

  const loadAllDriverData = () => {
    fetchBikes();
    fetchWallet();
    fetchActiveRental();
    fetchBookings();
    fetchDriverKyc();
  };

  const fetchDriverKyc = async () => {
    setLoadingKyc(true);
    try {
      const res = await apiClient.get('/driver/kyc');
      if (res.data?.data) {
        const d: DriverKycData = res.data.data;
        setKycData(d);
        if (d.driving_license_number) setDrivingLicense(d.driving_license_number);
        if (d.aadhaar_number) setAadhaarNumber(d.aadhaar_number);
        if (d.pan_number) setPanNumber(d.pan_number);
        if (d.address) setAddress(d.address);
        if (d.emergency_contact_name) setEmergencyName(d.emergency_contact_name);
        if (d.emergency_contact_phone) setEmergencyPhone(d.emergency_contact_phone);
      }
    } catch (err) {
      console.error('Failed to fetch driver KYC:', err);
    } finally {
      setLoadingKyc(false);
    }
  };

  const fetchBikes = async () => {
    setLoadingBikes(true);
    try {
      const res = await apiClient.get('/driver/bikes');
      if (res.data?.data) {
        setBikes(res.data.data);
      }
    } catch (err) {
      console.error('Failed to fetch scooties:', err);
    } finally {
      setLoadingBikes(false);
    }
  };

  const fetchWallet = async () => {
    setLoadingWallet(true);
    try {
      const res = await apiClient.get('/wallet/me');
      if (res.data?.data) {
        setWallet(res.data.data);
      }
    } catch (err) {
      console.error('Failed to fetch wallet:', err);
    } finally {
      setLoadingWallet(false);
    }
  };

  const fetchActiveRental = async () => {
    setLoadingRental(true);
    try {
      const res = await apiClient.get('/driver/assignment/active');
      if (res.data?.data) {
        setActiveRental(res.data.data);
      } else {
        setActiveRental(null);
      }
    } catch {
      setActiveRental(null);
    } finally {
      setLoadingRental(false);
    }
  };

  const fetchBookings = async () => {
    setLoadingBookings(true);
    try {
      const res = await apiClient.get('/driver/booking-history');
      if (res.data?.data) {
        setMyBookings(res.data.data);
      }
    } catch (err) {
      console.error('Failed to fetch bookings:', err);
    } finally {
      setLoadingBookings(false);
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
          localStorage.setItem('driver_user', JSON.stringify(data.user));
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
          role: 'driver'
        });
        const data = res.data?.data;
        if (data?.access_token) {
          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('driver_user', JSON.stringify(data.user));
          setToken(data.access_token);
          setUser(data.user);
        }
      }
    } catch (err: any) {
      console.error('Driver auth error:', err);
      const detail = err.response?.data?.detail;
      const message = err.response?.data?.message;
      let displayError = 'Authentication failed. Please verify your details.';
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
    localStorage.removeItem('driver_user');
    setToken(null);
    setUser(null);
    setBikes([]);
    setActiveRental(null);
    setMyBookings([]);
    setWallet({ wallet_id: '', balance: 0, transactions: [] });
  };

  // Wallet recharge (Min ₹500 rule enforced)
  const handleRecharge = async (e: React.FormEvent) => {
    e.preventDefault();
    if (rechargeAmount < 500) {
      setRechargeMsg({ type: 'error', text: 'Minimum recharge amount is ₹500.' });
      return;
    }
    setRechargeLoading(true);
    setRechargeMsg(null);
    try {
      const res = await apiClient.post('/wallet/topup', { amount: rechargeAmount });
      setRechargeMsg({ type: 'success', text: `₹${rechargeAmount} credited to your wallet successfully!` });
      fetchWallet();
      setTimeout(() => {
        setShowRechargeModal(false);
        setRechargeMsg(null);
      }, 1200);
    } catch (err: any) {
      setRechargeMsg({ type: 'error', text: err.response?.data?.detail || 'Wallet recharge failed. Try again.' });
    } finally {
      setRechargeLoading(false);
    }
  };

  const calculateRentForHours = (bike: Bike | null, hours: number): number => {
    if (!bike) return 0;
    const matchingTariff = bike.tariffs?.find(t => t.hours === hours);
    if (matchingTariff) return matchingTariff.price;
    const hourly = bike.pricing?.hourly_rate || 100;
    const daily = bike.pricing?.daily_rent || 350;
    if (hours < 24) {
      return hours * hourly;
    }
    const days = Math.floor(hours / 24);
    const extraH = hours % 24;
    return (days * daily) + (extraH * hourly);
  };

  // Submit Scooty Booking
  const handleBookScooty = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBike) return;
    setBookingLoading(true);
    setBookingFeedback(null);

    const rent = calculateRentForHours(selectedBike, selectedHours);
    const isCod = selectedPaymentMethod === 'cod';
    const deposit = isCod ? 0 : (selectedBike.pricing?.security_deposit || 0);
    const requiredTotal = rent + deposit;

    if (!isCod && wallet.balance < requiredTotal) {
      setBookingFeedback({
        type: 'error',
        text: `Insufficient wallet balance! Online booking requires ₹${requiredTotal} (₹${rent} rent + ₹${deposit} deposit). Current balance: ₹${wallet.balance}. Please recharge or select Cash on Delivery (COD).`
      });
      setBookingLoading(false);
      return;
    }

    try {
      await apiClient.post('/driver/bikes/book', {
        bike_id: selectedBike.id,
        rental_hours: selectedHours,
        payment_method: selectedPaymentMethod,
        message: bookingMsg || `Booking requested for ${selectedHours} hours.`
      });
      const feedbackText = isCod
        ? `Booking request sent to owner! You chose Cash on Delivery (₹${rent}). Hand cash directly to owner on pickup.`
        : `Booking request sent to owner! ₹${requiredTotal} (₹${rent} rent + ₹${deposit} deposit) has been held from your wallet. Your booking will be finalized upon owner acceptance. If rejected, it is refunded immediately.`;
      setBookingFeedback({ type: 'success', text: feedbackText });
      fetchBookings();
      fetchWallet();
      setTimeout(() => {
        setSelectedBike(null);
        setBookingFeedback(null);
        setBookingMsg('');
      }, 1800);
    } catch (err: any) {
      setBookingFeedback({ type: 'error', text: err.response?.data?.detail || 'Booking request could not be processed.' });
    } finally {
      setBookingLoading(false);
    }
  };

  // Cancel pending booking
  const [cancellingBookingId, setCancellingBookingId] = useState<string | null>(null);
  const handleCancelBooking = async (bookingId: string) => {
    if (!window.confirm('Are you sure you want to cancel this pending booking? If prepaid online, your held funds will be refunded to your wallet immediately.')) {
      return;
    }
    setCancellingBookingId(bookingId);
    try {
      const res = await apiClient.post(`/driver/bookings/${bookingId}/cancel`, {});
      alert(res.data?.message || 'Booking cancelled successfully.');
      fetchBookings();
      fetchWallet();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to cancel booking.');
    } finally {
      setCancellingBookingId(null);
    }
  };

  // Notify owner that cash has been handed over
  const handleNotifyCashHanded = async (assignmentId: string) => {
    setHandCashLoading(true);
    try {
      const res = await apiClient.post(`/driver/assignments/${assignmentId}/hand-cash`, {});
      setHandCashMsg(res.data?.message || 'Owner notified! Awaiting owner confirmation.');
      setTimeout(() => setHandCashMsg(null), 4000);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to notify owner.');
    } finally {
      setHandCashLoading(false);
    }
  };

  // Request vehicle return
  const handleRequestReturn = async () => {
    setReturnMessage('Submitting return request to scooty owner...');
    try {
      await apiClient.post('/driver/assignment/request-return', {});
      setReturnRequested(true);
      setReturnMessage('Return request submitted! The owner has been notified to inspect vehicle condition and release your deposit.');
    } catch (err: any) {
      setReturnMessage(err.response?.data?.detail || 'Return request submitted. Owner has been notified.');
      setReturnRequested(true);
    }
  };

  // Submit KYC Multipart Form Data
  const handleSaveKyc = async (e: React.FormEvent) => {
    e.preventDefault();
    if (kycData?.verification_status === 'pending') {
      setKycError('Your KYC documents are currently under review by Admin. Submissions are locked until verification is processed.');
      return;
    }
    if (kycData?.verification_status === 'verified') {
      setKycError('Your KYC documents have already been verified and approved. No further submissions are allowed.');
      return;
    }

    setKycLoading(true);
    setKycSuccess(null);
    setKycError(null);

    try {
      const formData = new FormData();
      if (user?.full_name) formData.append('full_name', user.full_name);
      if (drivingLicense) formData.append('driving_license_number', drivingLicense.trim());
      if (aadhaarNumber) formData.append('aadhaar_number', aadhaarNumber.trim());
      if (panNumber) formData.append('pan_number', panNumber.trim());
      if (address) formData.append('address', address.trim());
      if (emergencyName) formData.append('emergency_contact_name', emergencyName.trim());
      if (emergencyPhone) formData.append('emergency_contact_phone', emergencyPhone.trim());

      // Files
      if (licenseFile) formData.append('license_file', licenseFile);
      if (aadhaarFile) formData.append('aadhaar_file', aadhaarFile);
      if (panFile) formData.append('pan_file', panFile);
      if (profilePicFile) formData.append('profile_picture', profilePicFile);

      const res = await apiClient.post('/driver/kyc', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setKycSuccess('KYC documents & identity proof uploaded successfully! Submitted to Admin for verification.');
      if (res.data?.data) {
        setKycData(res.data.data);
      } else {
        fetchDriverKyc();
      }
      validateSession();
      setTimeout(() => setKycSuccess(null), 4000);
    } catch (err: any) {
      console.error('KYC submission error:', err);
      const detail = err.response?.data?.detail;
      const message = err.response?.data?.message;
      let displayError = 'Failed to submit KYC details.';
      if (typeof detail === 'string') displayError = detail;
      else if (Array.isArray(detail)) displayError = detail.map((d: any) => d.msg || JSON.stringify(d)).join(', ');
      else if (typeof message === 'string') displayError = message;
      else if (err.message) displayError = err.message;
      setKycError(displayError);
    } finally {
      setKycLoading(false);
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
    if (!name) return 'DR';
    return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() || 'DR';
  };

  const getBikeImageUrl = (bike: Bike): string => {
    const img = bike.images?.[0];
    if (!img) return 'https://images.unsplash.com/photo-1558981806-ec527fa84c39?auto=format&fit=crop&w=600&q=80';
    if (typeof img === 'string') return img;
    return img.image_url || 'https://images.unsplash.com/photo-1558981806-ec527fa84c39?auto=format&fit=crop&w=600&q=80';
  };

  // Filter bikes
  const filteredBikes = bikes.filter(b => {
    const matchesSearch = b.bike_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          b.brand.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          b.model.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesBrand = selectedBrand === 'all' || b.brand.toLowerCase() === selectedBrand.toLowerCase();
    const matchesFuel = selectedFuel === 'all' || b.fuel_type.toLowerCase() === selectedFuel.toLowerCase();
    const matchesPrice = (b.pricing?.daily_rent || 0) <= maxPrice;
    return matchesSearch && matchesBrand && matchesFuel && matchesPrice;
  });

  // =========================================================================
  // 1. FIRST: SIGN IN / SIGN UP SCREEN (If not authenticated)
  // =========================================================================
  if (!token || !user) {
    return (
      <div className="min-h-screen bg-[#f4f8f6] flex flex-col justify-center items-center p-4 font-sans text-slate-800">
        <div className="w-full max-w-md bg-white border border-slate-200/80 rounded-3xl p-8 shadow-sm">
          {/* Header */}
          <div className="flex items-center gap-3 mb-6">
            <div className="w-11 h-11 rounded-2xl bg-emerald-100 flex items-center justify-center text-emerald-800 font-bold shadow-xs">
              <BikeIcon className="w-6 h-6 text-emerald-700" />
            </div>
            <div>
              <h2 className="text-xl font-extrabold text-slate-900 tracking-tight">VeloRent Driver</h2>
              <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">PORT 3110 • SCOOTY RENTALS</p>
            </div>
          </div>

          {/* Mode Switcher Tabs */}
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
                  <label className="block text-xs font-bold text-slate-700 mb-1">Full Name</label>
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
                  <label className="block text-xs font-bold text-slate-700 mb-1">Phone Number (10 Digits)</label>
                  <div className="relative">
                    <Phone className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="tel"
                      required
                      placeholder="e.g. 9876543210"
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
                  placeholder="driver@example.com"
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
                    placeholder="Repeat your password"
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
                <span>Authenticating with Database...</span>
              ) : (
                <>
                  <span>{authMode === 'login' ? 'Sign In to Driver Workspace' : 'Create Driver Account'}</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 pt-4 border-t border-slate-100 flex flex-col items-center gap-2 text-[11px] text-slate-500">
            <div className="flex items-center gap-2">
              <span>Switch Portal:</span>
              <a href={getPortalUrl(6782)} className="font-bold text-emerald-800 hover:underline">
                Owner Fleet (6782)
              </a>
              <span>•</span>
              <a href={getPortalUrl(5431)} className="font-bold text-purple-700 hover:underline flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5 text-purple-600" />
                <span>Admin Console (5431)</span>
              </a>
            </div>
            <span>Production Database Auth • PostgreSQL / JWT HS256</span>
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
              <p className="text-[10px] font-bold text-slate-400 tracking-wider uppercase">DRIVER PLATFORM</p>
            </div>
          </div>

          {/* User Profile Chip */}
          <div className="mt-5 p-2 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-900 font-bold flex items-center justify-center text-xs">
                {getInitials(displayName)}
              </div>
              <div className="overflow-hidden">
                <p className="text-xs font-semibold text-slate-900 truncate leading-tight">{displayName}</p>
                <p className="text-[11px] text-emerald-700 font-medium">
                  {user.is_verified ? 'Verified Driver' : 'Pending Verification'}
                </p>
              </div>
            </div>
            <ChevronDown className="w-4 h-4 text-slate-400" />
          </div>

          {/* Section Category Header */}
          <div className="mt-6 mb-2">
            <p className="text-[11px] font-bold text-slate-400 tracking-wider uppercase px-2">RENTAL OPERATIONS</p>
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
              onClick={() => setActiveTab('browse')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                activeTab === 'browse'
                  ? 'bg-emerald-50 text-emerald-900 border border-emerald-100 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <Search className="w-4 h-4" />
              <span>Browse Scooties</span>
            </button>

            <button
              onClick={() => setActiveTab('active_rental')}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                activeTab === 'active_rental'
                  ? 'bg-emerald-50 text-emerald-900 border border-emerald-100 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <div className="flex items-center gap-3">
                <Clock className="w-4 h-4" />
                <span>Active Rental</span>
              </div>
              {activeRental && (
                <span className="px-2 py-0.5 text-[10px] font-bold bg-emerald-100 text-emerald-800 rounded-full">
                  Live
                </span>
              )}
            </button>

            <button
              onClick={() => setActiveTab('bookings')}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                activeTab === 'bookings'
                  ? 'bg-emerald-50 text-emerald-900 border border-emerald-100 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <div className="flex items-center gap-3">
                <FileText className="w-4 h-4" />
                <span>My Bookings</span>
              </div>
              {myBookings.length > 0 && (
                <span className="px-2 py-0.5 text-[10px] font-bold bg-slate-100 text-slate-700 rounded-full">
                  {myBookings.length}
                </span>
              )}
            </button>

            <button
              onClick={() => setActiveTab('wallet')}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                activeTab === 'wallet'
                  ? 'bg-emerald-50 text-emerald-900 border border-emerald-100 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <div className="flex items-center gap-3">
                <Wallet className="w-4 h-4" />
                <span>Wallet & Balance</span>
              </div>
              <span className="text-[11px] font-bold text-slate-700">₹{wallet.balance}</span>
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
                <ShieldCheck className="w-4 h-4" />
                <span>KYC Documents</span>
              </div>
              <span className={`w-2 h-2 rounded-full ${
                kycData?.verification_status === 'verified' ? 'bg-emerald-500' :
                kycData?.verification_status === 'rejected' ? 'bg-rose-500' :
                kycData?.verification_status === 'pending' ? 'bg-amber-500 animate-pulse' :
                'bg-slate-400'
              }`}></span>
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
              24/7 roadside assistance & rental support in one place.
            </p>
            <button
              onClick={() => alert("Roadside Assistance Helpline: 1800-VELORENT (24x7 Active)")}
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
        {/* Top Header */}
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
                placeholder="Search scooty catalog..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 pr-4 py-1.5 bg-slate-50 border border-slate-200/80 rounded-full text-xs text-slate-700 w-64 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition"
              />
            </div>

            <button
              onClick={() => setShowRechargeModal(true)}
              className="flex items-center gap-2 px-3 py-1.5 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200/80 rounded-full text-xs font-bold text-emerald-900 transition"
            >
              <Wallet className="w-3.5 h-3.5 text-emerald-700" />
              <span>₹{wallet.balance}</span>
              <Plus className="w-3.5 h-3.5 bg-emerald-200 text-emerald-800 rounded-full p-0.5" />
            </button>

            {/* Portal Switcher Buttons */}
            <div className="hidden md:flex items-center gap-1 bg-slate-100 p-1 rounded-full text-[11px] font-bold">
              <span className="px-2.5 py-1 bg-white text-emerald-900 rounded-full shadow-xs">
                Driver
              </span>
              <a
                href={getPortalUrl(6782)}
                className="px-2.5 py-1 text-slate-500 hover:text-slate-900 hover:bg-white/60 rounded-full transition"
                title="Open Owner Fleet Portal (Port 6782)"
              >
                Owner
              </a>
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
          {/* DASHBOARD TAB ONLY: HERO GREETING BANNER & 4 KPI METRIC CARDS */}
          {/* ========================================================================= */}
          {activeTab === 'dashboard' && (
            <>
              {/* HERO GREETING BANNER (Dynamic Time-of-Day Greeting) */}
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
                      Your scooty rental & active journey overview for today.
                    </p>

                    <div className="flex items-center gap-2 mt-4">
                      <span className="px-3 py-1 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full text-xs font-semibold text-white">
                        Driver platform
                      </span>
                      <span className="px-3 py-1 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full text-xs font-medium text-emerald-100">
                        Live Database Connected
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <button
                      onClick={loadAllDriverData}
                      className="px-4 py-2 bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/20 rounded-full text-xs font-semibold text-white flex items-center gap-2 shadow-xs transition"
                    >
                      <RefreshCw className="w-3.5 h-3.5" />
                      <span>Refresh overview</span>
                    </button>
                  </div>
                </div>
              </div>

              {/* 4 KPI METRIC CARDS (KYC card dynamically reflects live database verification status) */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs flex flex-col justify-between">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-500">Available scooties</span>
                    <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center">
                      <BikeIcon className="w-4 h-4" />
                    </div>
                  </div>
                  <div className="my-2">
                    <span className="text-2xl font-extrabold text-slate-900">{bikes.length}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-[11px] font-bold text-emerald-700">
                    <span>↗ {bikes.length} available</span>
                    <span className="font-normal text-slate-400">in live database</span>
                  </div>
                </div>

                <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs flex flex-col justify-between">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-500">Active rental</span>
                    <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center">
                      <Clock className="w-4 h-4" />
                    </div>
                  </div>
                  <div className="my-2">
                    <span className="text-2xl font-extrabold text-slate-900">{activeRental ? '1' : '0'}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-[11px] font-bold text-blue-700">
                    <span>{activeRental ? '↗ Trip in progress' : 'No active rental'}</span>
                    <span className="font-normal text-slate-400">max 1 allowed</span>
                  </div>
                </div>

                <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs flex flex-col justify-between">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-500">Wallet balance</span>
                    <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-700 flex items-center justify-center">
                      <Wallet className="w-4 h-4" />
                    </div>
                  </div>
                  <div className="my-2">
                    <span className="text-2xl font-extrabold text-slate-900">₹{wallet.balance}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-[11px] font-bold text-amber-700">
                    <span>↗ Min recharge</span>
                    <span className="font-normal text-slate-400">₹500 policy active</span>
                  </div>
                </div>

                {/* DYNAMIC KYC STATUS METRIC CARD */}
                {(() => {
                  const kycStatus = (kycData?.verification_status || 'draft').toLowerCase();
                  let statusTitle = 'Not Submitted';
                  let statusSub = 'Upload DL & Aadhaar';
                  let badgeClass = 'text-slate-600 bg-slate-100';
                  let iconBg = 'bg-slate-100 text-slate-600';
                  let textColor = 'text-slate-800';

                  if (kycStatus === 'verified') {
                    statusTitle = 'Verified';
                    statusSub = '✓ Approved & Insured';
                    badgeClass = 'text-emerald-700 bg-emerald-50';
                    iconBg = 'bg-emerald-50 text-emerald-700';
                    textColor = 'text-emerald-950';
                  } else if (kycStatus === 'pending') {
                    statusTitle = 'Under Review';
                    statusSub = '⏳ Admin Reviewing';
                    badgeClass = 'text-amber-800 bg-amber-50';
                    iconBg = 'bg-amber-50 text-amber-700';
                    textColor = 'text-amber-950';
                  } else if (kycStatus === 'rejected') {
                    statusTitle = 'Rejected';
                    statusSub = '✕ Re-upload Required';
                    badgeClass = 'text-rose-800 bg-rose-50';
                    iconBg = 'bg-rose-50 text-rose-700';
                    textColor = 'text-rose-950';
                  }

                  return (
                    <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs flex flex-col justify-between">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold text-slate-500">KYC Status</span>
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${iconBg}`}>
                          <ShieldCheck className="w-4 h-4" />
                        </div>
                      </div>
                      <div className="my-2">
                        <span className={`text-2xl font-extrabold ${textColor}`}>{statusTitle}</span>
                      </div>
                      <div className="flex items-center gap-1.5 text-[11px] font-bold">
                        <span className={`px-2 py-0.5 rounded-full ${badgeClass}`}>{statusSub}</span>
                      </div>
                    </div>
                  );
                })()}
              </div>

              {/* DASHBOARD OVERVIEW: Available Scooties Preview + Operations Shortcuts */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Left 8 Cols */}
                <div className="lg:col-span-8 bg-white rounded-2xl border border-slate-200/80 p-6 shadow-xs">
                  <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
                    <div>
                      <h3 className="text-sm font-bold text-slate-900">Available Scooties for Rent</h3>
                      <p className="text-xs text-slate-500 mt-0.5">Explore verified owner fleets in the database</p>
                    </div>
                    <button
                      onClick={() => setActiveTab('browse')}
                      className="text-xs font-bold text-emerald-800 hover:text-emerald-950 flex items-center gap-1"
                    >
                      <span>View full catalog ({bikes.length})</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  {loadingBikes ? (
                    <div className="p-12 text-center text-slate-400">
                      <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-emerald-600" />
                      <p className="text-xs">Loading available scooties from database...</p>
                    </div>
                  ) : filteredBikes.length === 0 ? (
                    <div className="p-12 text-center text-slate-400 border border-dashed border-slate-200 rounded-2xl">
                      <BikeIcon className="w-10 h-10 mx-auto mb-2 text-slate-300" />
                      <p className="text-sm font-bold text-slate-700">No Scooties Available in Database</p>
                      <p className="text-xs mt-1 text-slate-500">
                        Fleet owners have not yet listed scooties or they are awaiting admin verification.
                      </p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {filteredBikes.slice(0, 4).map(bike => {
                        const rent = bike.pricing?.daily_rent || 0;
                        const deposit = bike.pricing?.security_deposit || 0;
                        const hasActiveRental = !!activeRental;

                        return (
                          <div key={bike.id} className="bg-slate-50/70 hover:bg-slate-50 border border-slate-200/80 rounded-2xl p-4 transition flex flex-col justify-between">
                            <div>
                              <div className="h-36 w-full rounded-xl overflow-hidden bg-slate-200 relative mb-3">
                                <img
                                  src={getBikeImageUrl(bike)}
                                  alt={bike.bike_name}
                                  className="w-full h-full object-cover"
                                />
                                <div className="absolute top-2 left-2 flex gap-1.5">
                                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                                    bike.fuel_type === 'electric' ? 'bg-emerald-600 text-white' : 'bg-slate-800 text-white'
                                  }`}>
                                    {bike.fuel_type}
                                  </span>
                                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-white/90 text-slate-800">
                                    {bike.registration_number}
                                  </span>
                                </div>
                              </div>

                              <h4 className="text-sm font-bold text-slate-900 leading-tight">{bike.bike_name}</h4>
                              <p className="text-xs text-slate-500 mt-0.5">{bike.brand} • {bike.color} • {bike.km_driven} km</p>
                            </div>

                            <div className="mt-4 pt-3 border-t border-slate-200/60 flex items-center justify-between">
                              <div>
                                <p className="text-xs text-slate-500">Rent / Day</p>
                                <p className="text-base font-extrabold text-slate-900">₹{rent}</p>
                                <p className="text-[10px] text-slate-400">Deposit: ₹{deposit}</p>
                              </div>

                              <button
                                onClick={() => {
                                  setSelectedBike(bike);
                                  setBookingFeedback(null);
                                }}
                                disabled={hasActiveRental}
                                className={`px-4 py-2 rounded-xl text-xs font-bold transition shadow-xs ${
                                  hasActiveRental
                                    ? 'bg-slate-200 text-slate-400 cursor-not-allowed'
                                    : 'bg-emerald-700 hover:bg-emerald-800 text-white'
                                }`}
                              >
                                {hasActiveRental ? 'Ride in Progress' : 'Book Scooty'}
                              </button>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>

                {/* Right 4 Cols: Operations Quick Actions */}
                <div className="lg:col-span-4 bg-white rounded-2xl border border-slate-200/80 p-6 shadow-xs flex flex-col justify-between">
                  <div>
                    <h3 className="text-sm font-bold text-slate-900 leading-tight">Rental operations</h3>
                    <p className="text-xs text-slate-500 mt-0.5 mb-5">Open a workspace module to take action.</p>

                    <div className="space-y-3">
                      <div
                        onClick={() => setActiveTab('browse')}
                        className="p-3.5 bg-slate-50 hover:bg-emerald-50/70 border border-slate-100 hover:border-emerald-200 rounded-xl cursor-pointer transition flex items-center justify-between group"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center">
                            <BikeIcon className="w-4 h-4" />
                          </div>
                          <div>
                            <p className="text-xs font-bold text-slate-900 leading-tight">Browse scooties</p>
                            <p className="text-[11px] text-slate-500 mt-0.5">Filter models, rent & fuel types</p>
                          </div>
                        </div>
                        <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-emerald-700 group-hover:translate-x-0.5 transition" />
                      </div>

                      <div
                        onClick={() => setShowRechargeModal(true)}
                        className="p-3.5 bg-slate-50 hover:bg-emerald-50/70 border border-slate-100 hover:border-emerald-200 rounded-xl cursor-pointer transition flex items-center justify-between group"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-lg bg-amber-100 text-amber-800 flex items-center justify-center">
                            <Wallet className="w-4 h-4" />
                          </div>
                          <div>
                            <p className="text-xs font-bold text-slate-900 leading-tight">Recharge wallet</p>
                            <p className="text-[11px] text-slate-500 mt-0.5">Razorpay fast top-up (min ₹500)</p>
                          </div>
                        </div>
                        <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-emerald-700 group-hover:translate-x-0.5 transition" />
                      </div>

                      <div
                        onClick={() => setActiveTab('active_rental')}
                        className="p-3.5 bg-slate-50 hover:bg-emerald-50/70 border border-slate-100 hover:border-emerald-200 rounded-xl cursor-pointer transition flex items-center justify-between group"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-lg bg-blue-100 text-blue-800 flex items-center justify-center">
                            <Clock className="w-4 h-4" />
                          </div>
                          <div>
                            <p className="text-xs font-bold text-slate-900 leading-tight">Active rental trip</p>
                            <p className="text-[11px] text-slate-500 mt-0.5">Track live time & request return</p>
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
                            <ShieldCheck className="w-4 h-4" />
                          </div>
                          <div>
                            <p className="text-xs font-bold text-slate-900 leading-tight">Verify KYC documents</p>
                            <p className="text-[11px] text-slate-500 mt-0.5">DL, Aadhaar & PAN verification</p>
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
                    <span>Port 3110</span>
                  </div>
                </div>
              </div>
            </>
          )}

          {/* ========================================================================= */}
          {/* NON-DASHBOARD TABS: DEDICATED FULL-PAGE WORKSPACE (NO HERO BANNER / KPIS) */}
          {/* ========================================================================= */}
          {activeTab !== 'dashboard' && (
            <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-xs">
              {activeTab === 'browse' && (
                /* Browse Catalog View */
                <div>
                  <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
                    <div>
                      <h3 className="text-base font-bold text-slate-900">Browse Scooties Catalog</h3>
                      <p className="text-xs text-slate-500 mt-0.5">
                        Explore verified owner fleets in the database ({filteredBikes.length} available)
                      </p>
                    </div>
                  </div>

                  {/* Filter bar */}
                  <div className="flex flex-wrap items-center gap-3 mb-6 bg-slate-50 p-3.5 rounded-xl border border-slate-100">
                    <div className="flex items-center gap-2 text-xs font-semibold text-slate-600">
                      <Filter className="w-3.5 h-3.5 text-slate-400" />
                      <span>Filters:</span>
                    </div>

                    <select
                      value={selectedBrand}
                      onChange={(e) => setSelectedBrand(e.target.value)}
                      className="px-3 py-1.5 bg-white border border-slate-200 rounded-lg text-xs font-medium text-slate-700"
                    >
                      <option value="all">All Brands</option>
                      <option value="honda">Honda</option>
                      <option value="ather">Ather</option>
                      <option value="tvs">TVS</option>
                      <option value="ola">Ola</option>
                    </select>

                    <select
                      value={selectedFuel}
                      onChange={(e) => setSelectedFuel(e.target.value)}
                      className="px-3 py-1.5 bg-white border border-slate-200 rounded-lg text-xs font-medium text-slate-700"
                    >
                      <option value="all">All Fuel Types</option>
                      <option value="petrol">Petrol</option>
                      <option value="electric">Electric (EV)</option>
                    </select>
                  </div>

                  {loadingBikes ? (
                    <div className="p-16 text-center text-slate-400">
                      <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-emerald-600" />
                      <p className="text-xs">Loading available scooties from database...</p>
                    </div>
                  ) : filteredBikes.length === 0 ? (
                    <div className="p-16 text-center text-slate-400 border border-dashed border-slate-200 rounded-2xl">
                      <BikeIcon className="w-10 h-10 mx-auto mb-2 text-slate-300" />
                      <p className="text-sm font-bold text-slate-700">No Scooties Available in Database</p>
                      <p className="text-xs mt-1 text-slate-500">
                        Fleet owners have not yet listed scooties or they are awaiting admin verification.
                      </p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                      {filteredBikes.map(bike => {
                        const rent = bike.pricing?.daily_rent || 0;
                        const deposit = bike.pricing?.security_deposit || 0;
                        const hasActiveRental = !!activeRental;

                        return (
                          <div key={bike.id} className="bg-slate-50/70 hover:bg-slate-50 border border-slate-200/80 rounded-2xl p-4 transition flex flex-col justify-between">
                            <div>
                              <div className="h-40 w-full rounded-xl overflow-hidden bg-slate-200 relative mb-3">
                                <img
                                  src={getBikeImageUrl(bike)}
                                  alt={bike.bike_name}
                                  className="w-full h-full object-cover"
                                />
                                <div className="absolute top-2 left-2 flex gap-1.5">
                                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                                    bike.fuel_type === 'electric' ? 'bg-emerald-600 text-white' : 'bg-slate-800 text-white'
                                  }`}>
                                    {bike.fuel_type}
                                  </span>
                                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-white/90 text-slate-800">
                                    {bike.registration_number}
                                  </span>
                                </div>
                              </div>

                              <h4 className="text-sm font-bold text-slate-900 leading-tight">{bike.bike_name}</h4>
                              <p className="text-xs text-slate-500 mt-0.5">{bike.brand} • {bike.color} • {bike.km_driven} km</p>
                            </div>

                            <div className="mt-4 pt-3 border-t border-slate-200/60 flex items-center justify-between">
                              <div>
                                <p className="text-xs text-slate-500">Rent / Day</p>
                                <p className="text-base font-extrabold text-slate-900">₹{rent}</p>
                                <p className="text-[10px] text-slate-400">Security Deposit: ₹{deposit}</p>
                              </div>

                              <button
                                onClick={() => {
                                  setSelectedBike(bike);
                                  setBookingFeedback(null);
                                }}
                                disabled={hasActiveRental}
                                className={`px-4 py-2 rounded-xl text-xs font-bold transition shadow-xs ${
                                  hasActiveRental
                                    ? 'bg-slate-200 text-slate-400 cursor-not-allowed'
                                    : 'bg-emerald-700 hover:bg-emerald-800 text-white'
                                }`}
                              >
                                {hasActiveRental ? 'Ride in Progress' : 'Book Scooty'}
                              </button>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'active_rental' && (
                /* Active Rental View */
                <div>
                  <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
                    <div>
                      <h3 className="text-base font-bold text-slate-900">Current Active Rental</h3>
                      <p className="text-xs text-slate-500 mt-0.5">Live database assignment and return notification</p>
                    </div>
                  </div>

                  {activeRental ? (
                    <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 space-y-6">
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-200">
                        <div className="flex items-center gap-4">
                          <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold">
                            <BikeIcon className="w-6 h-6" />
                          </div>
                          <div>
                            <h4 className="text-base font-bold text-slate-900">{activeRental.bike_name || 'Scooty'}</h4>
                            <p className="text-xs text-slate-500">{activeRental.registration_number}</p>
                          </div>
                        </div>
                        <span className="px-3 py-1 bg-emerald-100 text-emerald-900 text-xs font-bold rounded-full w-fit">
                          ● Rental Active
                        </span>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="p-3 bg-white rounded-xl border border-slate-200">
                          <p className="text-[11px] text-slate-400 font-semibold uppercase">Rental Duration</p>
                          <p className="text-sm font-bold text-slate-900 mt-1">{activeRental.rental_hours || 24} Hours</p>
                        </div>
                        <div className="p-3 bg-white rounded-xl border border-slate-200">
                          <p className="text-[11px] text-slate-400 font-semibold uppercase">Total Rent</p>
                          <p className="text-base font-bold text-slate-900">₹{activeRental.total_rent_amount || activeRental.daily_rent_amount}</p>
                        </div>
                        <div className="p-3 bg-white rounded-xl border border-slate-200">
                          <p className="text-[11px] text-slate-400 font-semibold uppercase">Payment Method</p>
                          <p className="text-xs font-bold text-slate-900 mt-1 uppercase">
                            {(activeRental.payment_method || 'cod') === 'cod' ? '💵 Cash on Delivery' : '⚡ UPI Online'}
                          </p>
                        </div>
                        <div className="p-3 bg-white rounded-xl border border-slate-200">
                          <p className="text-[11px] text-slate-400 font-semibold uppercase">Return Status</p>
                          <p className={`text-xs font-bold mt-1 ${returnRequested ? 'text-amber-600' : 'text-slate-700'}`}>
                            {returnRequested ? 'Inspection Pending' : 'Ride Ongoing'}
                          </p>
                        </div>
                      </div>

                      {/* Cash on Delivery Status Banner */}
                      {(activeRental.payment_method || 'cod').toLowerCase() === 'cod' && (
                        activeRental.cash_received ? (
                          <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <CheckCircle2 className="w-5 h-5 text-emerald-700 shrink-0" />
                              <div>
                                <p className="text-xs font-bold text-emerald-950">Cash Payment Confirmed by Owner</p>
                                <p className="text-[11px] text-emerald-800">Payment of ₹{activeRental.total_rent_amount || activeRental.daily_rent_amount} verified in database. Ride active and insured.</p>
                              </div>
                            </div>
                            <span className="text-[10px] font-bold bg-emerald-200 text-emerald-950 px-2.5 py-1 rounded-full">
                              ✓ PAID
                            </span>
                          </div>
                        ) : (
                          <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl space-y-3">
                            <div className="flex items-start justify-between gap-4">
                              <div className="flex items-start gap-3">
                                <Clock className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
                                <div>
                                  <p className="text-xs font-bold text-amber-950">
                                    Cash on Delivery Pending: ₹{activeRental.total_rent_amount || activeRental.daily_rent_amount}
                                  </p>
                                  <p className="text-[11px] text-amber-800 mt-0.5">
                                    Please hand over ₹{activeRental.total_rent_amount || activeRental.daily_rent_amount} in cash directly to the owner. Automated reminders are dispatched every 10 minutes until owner confirms receipt.
                                  </p>
                                </div>
                              </div>
                              <span className="text-[10px] font-bold bg-amber-200 text-amber-950 px-2.5 py-1 rounded-full shrink-0">
                                ⏳ CASH PENDING
                              </span>
                            </div>

                            <div className="pt-2 border-t border-amber-200/60 flex items-center justify-between">
                              <span className="text-[11px] text-amber-800 font-medium">Already handed over cash to owner?</span>
                              <button
                                onClick={() => handleNotifyCashHanded(activeRental.id)}
                                disabled={handCashLoading}
                                className="px-3.5 py-1.5 bg-amber-700 hover:bg-amber-800 text-white rounded-lg text-xs font-bold shadow-xs transition"
                              >
                                {handCashLoading ? 'Pinging Owner...' : '✓ I Have Handed Over Cash'}
                              </button>
                            </div>

                            {handCashMsg && (
                              <p className="text-xs font-bold text-emerald-800 bg-white/90 p-2 rounded-lg border border-emerald-200">
                                {handCashMsg}
                              </p>
                            )}
                          </div>
                        )
                      )}

                      {returnMessage && (
                        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl flex items-start gap-3">
                          <CheckCircle2 className="w-5 h-5 text-emerald-700 shrink-0 mt-0.5" />
                          <p className="text-xs text-emerald-900 font-medium">{returnMessage}</p>
                        </div>
                      )}

                      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-4 border-t border-slate-200">
                        <p className="text-xs text-slate-500">
                          Ready to return? Alerts owner to inspect vehicle condition and release your deposit.
                        </p>
                        <button
                          onClick={handleRequestReturn}
                          disabled={returnRequested}
                          className={`px-5 py-2.5 rounded-xl text-xs font-bold transition shrink-0 ${
                            returnRequested
                              ? 'bg-slate-200 text-slate-400 cursor-not-allowed'
                              : 'bg-emerald-700 hover:bg-emerald-800 text-white shadow-xs'
                          }`}
                        >
                          {returnRequested ? 'Return Pending Inspection' : 'Request Vehicle Return'}
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="p-16 text-center text-slate-400 border border-dashed border-slate-200 rounded-2xl">
                      <BikeIcon className="w-10 h-10 mx-auto mb-2 text-slate-300" />
                      <p className="text-sm font-bold text-slate-700">No Active Rental Found in Database</p>
                      <p className="text-xs mt-1 text-slate-500">When an owner accepts your booking request, your active ride will appear here.</p>
                      <button
                        onClick={() => setActiveTab('browse')}
                        className="mt-4 px-4 py-2 bg-emerald-700 hover:bg-emerald-800 text-white rounded-xl text-xs font-bold"
                      >
                        Browse Catalog
                      </button>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'bookings' && (
                /* Bookings List View */
                <div>
                  <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
                    <div>
                      <h3 className="text-base font-bold text-slate-900">My Rental Requests</h3>
                      <p className="text-xs text-slate-500 mt-0.5">Booking history stored in database</p>
                    </div>
                  </div>

                  {myBookings.length === 0 ? (
                    <div className="p-16 text-center text-slate-400 border border-dashed border-slate-200 rounded-2xl">
                      <FileText className="w-10 h-10 mx-auto mb-2 text-slate-300" />
                      <p className="text-sm font-bold text-slate-700">No Booking Requests Yet</p>
                      <p className="text-xs mt-1 text-slate-500">Browse scooties and submit your first booking request.</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {myBookings.map(b => (
                        <div key={b.id} className="p-4 bg-slate-50 rounded-xl border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                          <div>
                            <div className="flex items-center gap-2">
                              <p className="text-xs font-bold text-slate-900">{b.bike_name || 'Scooty'} {b.registration_number ? `(${b.registration_number})` : ''}</p>
                              <span className="text-[10px] font-bold bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">
                                {b.rental_hours || 24}h Duration
                              </span>
                              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                                (b.payment_method || 'cod').toLowerCase() === 'cod' ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'
                              }`}>
                                {(b.payment_method || 'cod').toUpperCase() === 'COD' ? '💵 Cash on Delivery' : '⚡ UPI Online'}
                              </span>
                            </div>
                            <p className="text-[11px] text-slate-500 mt-0.5">
                              Rent: ₹{b.total_amount || b.daily_rent}
                              {(b.payment_method || 'cod').toLowerCase() !== 'cod' && ` • Deposit: ₹${b.security_deposit || 1000}`}
                              {' '}• Date: {b.created_at ? new Date(b.created_at).toLocaleDateString() : 'Recent'}
                            </p>
                            {b.message && <p className="text-xs text-slate-600 mt-1 italic">"{b.message}"</p>}
                            {b.status === 'pending' && (
                              <p className="text-[11px] text-amber-700 bg-amber-50/80 px-2 py-0.5 rounded border border-amber-200 mt-1.5 inline-block">
                                ⏳ Awaiting bike owner acceptance. Your booking becomes final once accepted.
                              </p>
                            )}
                            {b.status === 'approved' && (
                              <p className="text-[11px] text-emerald-700 bg-emerald-50/80 px-2 py-0.5 rounded border border-emerald-200 mt-1.5 inline-block font-medium">
                                ✓ Booking accepted & confirmed by owner! Your rental is active.
                              </p>
                            )}
                            {(b.status === 'rejected' || b.status === 'refunded') && (
                              <div className="mt-1.5 text-[11px]">
                                {b.rejected_reason && (
                                  <p className="text-rose-700 bg-rose-50 px-2 py-0.5 rounded border border-rose-200 inline-block font-medium">
                                    ✕ Owner rejected: {b.rejected_reason}
                                  </p>
                                )}
                                {(b.payment_method || 'cod').toLowerCase() !== 'cod' && (
                                  <p className="text-purple-700 bg-purple-50 px-2 py-0.5 rounded border border-purple-200 mt-1 inline-block font-medium ml-1">
                                    💰 ₹{(b.total_amount || 0) + (b.security_deposit || 1000)} refunded to your wallet.
                                  </p>
                                )}
                              </div>
                            )}
                            {b.status === 'cancelled' && (
                              <div className="mt-1.5 text-[11px]">
                                <p className="text-slate-600 bg-slate-100 px-2 py-0.5 rounded border border-slate-200 inline-block font-medium">
                                  ✕ Cancelled by you.
                                </p>
                                {(b.payment_method || 'cod').toLowerCase() !== 'cod' && (
                                  <p className="text-purple-700 bg-purple-50 px-2 py-0.5 rounded border border-purple-200 mt-1 inline-block font-medium ml-1">
                                    💰 ₹{(b.total_amount || 0) + (b.security_deposit || 1000)} refunded to your wallet.
                                  </p>
                                )}
                              </div>
                            )}
                          </div>

                          <div className="flex items-center gap-2">
                            {(b.payment_method || 'cod').toLowerCase() === 'cod' && (
                              <span className={`px-2 py-0.5 text-[10px] font-bold rounded-full ${
                                b.cash_received ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                              }`}>
                                {b.cash_received ? '✓ Cash Received' : '⏳ Cash Pending'}
                              </span>
                            )}
                            <span className={`px-2.5 py-1 text-xs font-bold rounded-full ${
                              b.status === 'approved' ? 'bg-emerald-100 text-emerald-800' :
                              b.status === 'rejected' ? 'bg-rose-100 text-rose-800' :
                              b.status === 'refunded' ? 'bg-purple-100 text-purple-800' :
                              b.status === 'cancelled' ? 'bg-slate-200 text-slate-700' :
                              'bg-amber-100 text-amber-800'
                            }`}>
                              {b.status === 'pending' ? 'PENDING APPROVAL' :
                               b.status === 'approved' ? 'CONFIRMED' :
                               b.status === 'rejected' ? 'REJECTED' :
                               b.status === 'refunded' ? 'REFUNDED' :
                               b.status === 'cancelled' ? 'CANCELLED' : b.status.toUpperCase()}
                            </span>
                            {b.status === 'pending' && (
                              <button
                                onClick={() => handleCancelBooking(b.id)}
                                disabled={cancellingBookingId === b.id}
                                className="px-3 py-1 bg-white hover:bg-rose-50 text-rose-700 border border-rose-200 rounded-xl text-xs font-bold transition-colors shadow-2xs"
                              >
                                {cancellingBookingId === b.id ? 'Cancelling...' : 'Cancel'}
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'wallet' && (
                /* Wallet View */
                <div>
                  <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
                    <div>
                      <h3 className="text-base font-bold text-slate-900">Driver Wallet Ledger</h3>
                      <p className="text-xs text-slate-500 mt-0.5">Live database balance and ledger history</p>
                    </div>
                    <button
                      onClick={() => setShowRechargeModal(true)}
                      className="px-4 py-2 bg-emerald-700 hover:bg-emerald-800 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 shadow-xs"
                    >
                      <Plus className="w-3.5 h-3.5" />
                      <span>Recharge (Min ₹500)</span>
                    </button>
                  </div>

                  <div className="p-6 bg-gradient-to-r from-emerald-900 to-teal-900 text-white rounded-2xl mb-6">
                    <p className="text-xs text-emerald-200 font-semibold uppercase tracking-wider">Available Wallet Balance</p>
                    <p className="text-3xl font-extrabold mt-1">₹{wallet.balance.toLocaleString()}</p>
                    <p className="text-xs text-emerald-100/80 mt-2">
                      Rent and security deposits are debited from your balance upon owner booking confirmation.
                    </p>
                  </div>

                  <h4 className="text-xs font-bold text-slate-900 mb-3">Transaction History</h4>
                  {wallet.transactions.length === 0 ? (
                    <div className="p-12 text-center text-slate-400 bg-slate-50 border border-slate-200 rounded-xl">
                      <p className="text-xs">No transactions recorded in wallet ledger yet.</p>
                    </div>
                  ) : (
                    <div className="divide-y divide-slate-100 border border-slate-200 rounded-xl overflow-hidden bg-slate-50">
                      {wallet.transactions.map(tx => (
                        <div key={tx.id} className="p-3.5 flex items-center justify-between">
                          <div>
                            <p className="text-xs font-bold text-slate-900">{tx.description || tx.txn_type}</p>
                            <p className="text-[11px] text-slate-400 mt-0.5">{new Date(tx.created_at).toLocaleDateString()}</p>
                          </div>
                          <span className={`text-xs font-bold ${tx.type === 'credit' || tx.txn_type === 'recharge' ? 'text-emerald-700' : 'text-slate-800'}`}>
                            {tx.type === 'credit' || tx.txn_type === 'recharge' ? '+' : '-'}₹{tx.amount}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'kyc' && (
                /* KYC View with Locked Submissions when Pending / Verified & Re-upload when Rejected */
                (() => {
                  const kycStatus = (kycData?.verification_status || 'draft').toLowerCase();
                  const isKycPending = kycStatus === 'pending';
                  const isKycVerified = kycStatus === 'verified';
                  const isKycRejected = kycStatus === 'rejected';
                  const isKycLocked = isKycPending || isKycVerified;

                  return (
                    <div>
                      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
                        <div>
                          <h3 className="text-base font-bold text-slate-900">KYC & Document Verification</h3>
                          <p className="text-xs text-slate-500 mt-0.5">Submit government identity proof and documents to database for Admin verification</p>
                        </div>
                        {kycData && (
                          <span className={`px-3 py-1 text-xs font-bold rounded-full uppercase tracking-wider ${
                            isKycVerified ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' :
                            isKycRejected ? 'bg-rose-100 text-rose-800 border border-rose-200' :
                            isKycPending ? 'bg-amber-100 text-amber-800 border border-amber-200' :
                            'bg-slate-100 text-slate-700 border border-slate-200'
                          }`}>
                            {kycData.verification_status}
                          </span>
                        )}
                      </div>

                      {/* Verification Status Banner */}
                      {isKycVerified ? (
                        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-2xl flex items-start gap-3 mb-6">
                          <CheckCircle className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                          <div>
                            <h4 className="text-xs font-bold text-emerald-900">Verified Driver Account</h4>
                            <p className="text-[11px] text-emerald-700 mt-0.5">
                              Your identity documents have been approved by platform administrators. You have complete access to rent any scooty.
                            </p>
                          </div>
                        </div>
                      ) : isKycPending ? (
                        <div className="p-4 bg-amber-50 border border-amber-200 rounded-2xl flex items-start gap-3 mb-6">
                          <Clock className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                          <div>
                            <h4 className="text-xs font-bold text-amber-900">KYC Under Admin Review (Submissions Locked)</h4>
                            <p className="text-[11px] text-amber-700 mt-0.5">
                              Your documents have been submitted and are currently in the Admin verification queue. Submissions are locked until verification is complete. You cannot submit further documents while pending. You will receive a notification once verified.
                            </p>
                          </div>
                        </div>
                      ) : isKycRejected ? (
                        <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl flex items-start gap-3 mb-6">
                          <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
                          <div>
                            <h4 className="text-xs font-bold text-rose-900">Verification Rejected - Re-submission Permitted</h4>
                            <p className="text-[11px] text-rose-700 mt-0.5 font-medium">
                              Reason: {kycData?.rejection_reason || 'Document images were not clear or details mismatched.'}
                            </p>
                            <p className="text-[11px] text-rose-600 mt-1">
                              Please review the issue, correct your details or upload clear documents below, and re-submit for Admin review.
                            </p>
                          </div>
                        </div>
                      ) : (
                        <div className="p-4 bg-slate-50 border border-slate-200 rounded-2xl flex items-start gap-3 mb-6">
                          <ShieldCheck className="w-5 h-5 text-slate-500 shrink-0 mt-0.5" />
                          <div>
                            <h4 className="text-xs font-bold text-slate-800">Verification Required</h4>
                            <p className="text-[11px] text-slate-500 mt-0.5">
                              Please fill out your identity numbers and upload document proofs (Driving License, Aadhaar, PAN & Photo) to enable rentals.
                            </p>
                          </div>
                        </div>
                      )}

                      {/* Previously Uploaded Document Files Link Chips */}
                      {kycData && (kycData.driving_license_file_path || kycData.aadhaar_file_path || kycData.pan_file_path || kycData.profile_picture_path) && (
                        <div className="mb-6 p-4 bg-slate-50/70 border border-slate-200 rounded-2xl">
                          <p className="text-xs font-bold text-slate-700 mb-2">Stored Documents in Database:</p>
                          <div className="flex flex-wrap gap-2">
                            {kycData.driving_license_file_path && (
                              <a
                                href={`${getBackendBaseUrl()}/${kycData.driving_license_file_path.replace(/^\//, '')}`}
                                target="_blank"
                                rel="noreferrer"
                                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 hover:text-emerald-700 hover:border-emerald-300 transition"
                              >
                                <FileText className="w-3.5 h-3.5 text-emerald-600" />
                                <span>View Driving License</span>
                                <ExternalLink className="w-3 h-3 text-slate-400" />
                              </a>
                            )}
                            {kycData.aadhaar_file_path && (
                              <a
                                href={`${getBackendBaseUrl()}/${kycData.aadhaar_file_path.replace(/^\//, '')}`}
                                target="_blank"
                                rel="noreferrer"
                                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 hover:text-emerald-700 hover:border-emerald-300 transition"
                              >
                                <FileText className="w-3.5 h-3.5 text-emerald-600" />
                                <span>View Aadhaar Card</span>
                                <ExternalLink className="w-3 h-3 text-slate-400" />
                              </a>
                            )}
                            {kycData.pan_file_path && (
                              <a
                                href={`${getBackendBaseUrl()}/${kycData.pan_file_path.replace(/^\//, '')}`}
                                target="_blank"
                                rel="noreferrer"
                                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 hover:text-emerald-700 hover:border-emerald-300 transition"
                              >
                                <FileText className="w-3.5 h-3.5 text-emerald-600" />
                                <span>View PAN Card</span>
                                <ExternalLink className="w-3 h-3 text-slate-400" />
                              </a>
                            )}
                            {kycData.profile_picture_path && (
                              <a
                                href={`${getBackendBaseUrl()}/${kycData.profile_picture_path.replace(/^\//, '')}`}
                                target="_blank"
                                rel="noreferrer"
                                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 hover:text-emerald-700 hover:border-emerald-300 transition"
                              >
                                <Camera className="w-3.5 h-3.5 text-emerald-600" />
                                <span>View Profile Photo</span>
                                <ExternalLink className="w-3 h-3 text-slate-400" />
                              </a>
                            )}
                          </div>
                        </div>
                      )}

                      {kycSuccess && (
                        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-800 font-semibold mb-4">
                          {kycSuccess}
                        </div>
                      )}
                      {kycError && (
                        <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 font-semibold mb-4">
                          {kycError}
                        </div>
                      )}

                      <form onSubmit={handleSaveKyc} className="space-y-6">
                        {/* Section 1: Driving License */}
                        <div className="p-4 bg-slate-50/50 border border-slate-200 rounded-2xl space-y-3">
                          <div className="flex items-center gap-2">
                            <FileText className="w-4 h-4 text-emerald-700" />
                            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wide">1. Driving License Verification</h4>
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <label className="block text-xs font-bold text-slate-700 mb-1">Driving License Number</label>
                              <input
                                type="text"
                                required
                                disabled={isKycLocked}
                                placeholder="e.g. DL-1420110012345"
                                value={drivingLicense}
                                onChange={(e) => setDrivingLicense(e.target.value)}
                                className={`w-full px-3.5 py-2.5 border rounded-xl text-xs transition ${
                                  isKycLocked
                                    ? 'bg-slate-100 border-slate-200 text-slate-500 cursor-not-allowed'
                                    : 'bg-white border-slate-200 text-slate-800 focus:outline-none focus:ring-1 focus:ring-emerald-500'
                                }`}
                              />
                            </div>
                            <div>
                              <label className="block text-xs font-bold text-slate-700 mb-1">
                                Upload Driving License Document {licenseFile ? `(${licenseFile.name})` : ''}
                              </label>
                              <div className="relative">
                                <input
                                  type="file"
                                  accept="image/*,application/pdf"
                                  id="license_file_input"
                                  disabled={isKycLocked}
                                  onChange={(e) => setLicenseFile(e.target.files?.[0] || null)}
                                  className="hidden"
                                />
                                <label
                                  htmlFor={isKycLocked ? undefined : "license_file_input"}
                                  className={`flex items-center justify-between px-3.5 py-2.5 border border-dashed rounded-xl text-xs transition ${
                                    isKycLocked
                                      ? 'bg-slate-100 border-slate-200 text-slate-400 cursor-not-allowed'
                                      : 'bg-white border-slate-300 hover:border-emerald-500 cursor-pointer text-slate-600'
                                  }`}
                                >
                                  <span className="truncate">{licenseFile ? licenseFile.name : (kycData?.driving_license_file_path ? 'Driving License on Record' : 'Choose Image / PDF')}</span>
                                  <FileUp className="w-4 h-4 text-slate-400 shrink-0 ml-2" />
                                </label>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Section 2: Aadhaar Card */}
                        <div className="p-4 bg-slate-50/50 border border-slate-200 rounded-2xl space-y-3">
                          <div className="flex items-center gap-2">
                            <FileText className="w-4 h-4 text-emerald-700" />
                            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wide">2. Aadhaar Card Verification</h4>
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <label className="block text-xs font-bold text-slate-700 mb-1">Aadhaar Card Number (12 Digits)</label>
                              <input
                                type="text"
                                required
                                maxLength={12}
                                disabled={isKycLocked}
                                placeholder="e.g. 987654321098"
                                value={aadhaarNumber}
                                onChange={(e) => setAadhaarNumber(e.target.value)}
                                className={`w-full px-3.5 py-2.5 border rounded-xl text-xs transition ${
                                  isKycLocked
                                    ? 'bg-slate-100 border-slate-200 text-slate-500 cursor-not-allowed'
                                    : 'bg-white border-slate-200 text-slate-800 focus:outline-none focus:ring-1 focus:ring-emerald-500'
                                }`}
                              />
                            </div>
                            <div>
                              <label className="block text-xs font-bold text-slate-700 mb-1">
                                Upload Aadhaar Card Document {aadhaarFile ? `(${aadhaarFile.name})` : ''}
                              </label>
                              <div className="relative">
                                <input
                                  type="file"
                                  accept="image/*,application/pdf"
                                  id="aadhaar_file_input"
                                  disabled={isKycLocked}
                                  onChange={(e) => setAadhaarFile(e.target.files?.[0] || null)}
                                  className="hidden"
                                />
                                <label
                                  htmlFor={isKycLocked ? undefined : "aadhaar_file_input"}
                                  className={`flex items-center justify-between px-3.5 py-2.5 border border-dashed rounded-xl text-xs transition ${
                                    isKycLocked
                                      ? 'bg-slate-100 border-slate-200 text-slate-400 cursor-not-allowed'
                                      : 'bg-white border-slate-300 hover:border-emerald-500 cursor-pointer text-slate-600'
                                  }`}
                                >
                                  <span className="truncate">{aadhaarFile ? aadhaarFile.name : (kycData?.aadhaar_file_path ? 'Aadhaar on Record' : 'Choose Image / PDF')}</span>
                                  <FileUp className="w-4 h-4 text-slate-400 shrink-0 ml-2" />
                                </label>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Section 3: PAN Card & Profile Photo */}
                        <div className="p-4 bg-slate-50/50 border border-slate-200 rounded-2xl space-y-3">
                          <div className="flex items-center gap-2">
                            <FileText className="w-4 h-4 text-emerald-700" />
                            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wide">3. PAN Card & Profile Photo</h4>
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <label className="block text-xs font-bold text-slate-700 mb-1">PAN Card Number (10 Digits)</label>
                              <input
                                type="text"
                                maxLength={10}
                                disabled={isKycLocked}
                                placeholder="e.g. ABCDE1234F"
                                value={panNumber}
                                onChange={(e) => setPanNumber(e.target.value)}
                                className={`w-full px-3.5 py-2.5 border rounded-xl text-xs transition ${
                                  isKycLocked
                                    ? 'bg-slate-100 border-slate-200 text-slate-500 cursor-not-allowed'
                                    : 'bg-white border-slate-200 text-slate-800 focus:outline-none focus:ring-1 focus:ring-emerald-500'
                                }`}
                              />
                            </div>
                            <div>
                              <label className="block text-xs font-bold text-slate-700 mb-1">
                                Upload PAN Card Document {panFile ? `(${panFile.name})` : ''}
                              </label>
                              <div className="relative">
                                <input
                                  type="file"
                                  accept="image/*,application/pdf"
                                  id="pan_file_input"
                                  disabled={isKycLocked}
                                  onChange={(e) => setPanFile(e.target.files?.[0] || null)}
                                  className="hidden"
                                />
                                <label
                                  htmlFor={isKycLocked ? undefined : "pan_file_input"}
                                  className={`flex items-center justify-between px-3.5 py-2.5 border border-dashed rounded-xl text-xs transition ${
                                    isKycLocked
                                      ? 'bg-slate-100 border-slate-200 text-slate-400 cursor-not-allowed'
                                      : 'bg-white border-slate-300 hover:border-emerald-500 cursor-pointer text-slate-600'
                                  }`}
                                >
                                  <span className="truncate">{panFile ? panFile.name : (kycData?.pan_file_path ? 'PAN on Record' : 'Choose Image / PDF')}</span>
                                  <FileUp className="w-4 h-4 text-slate-400 shrink-0 ml-2" />
                                </label>
                              </div>
                            </div>
                            <div className="md:col-span-2">
                              <label className="block text-xs font-bold text-slate-700 mb-1">
                                Upload Driver Profile Picture / Headshot {profilePicFile ? `(${profilePicFile.name})` : ''}
                              </label>
                              <div className="relative">
                                <input
                                  type="file"
                                  accept="image/*"
                                  id="profile_pic_input"
                                  disabled={isKycLocked}
                                  onChange={(e) => setProfilePicFile(e.target.files?.[0] || null)}
                                  className="hidden"
                                />
                                <label
                                  htmlFor={isKycLocked ? undefined : "profile_pic_input"}
                                  className={`flex items-center justify-between px-3.5 py-2.5 border border-dashed rounded-xl text-xs transition ${
                                    isKycLocked
                                      ? 'bg-slate-100 border-slate-200 text-slate-400 cursor-not-allowed'
                                      : 'bg-white border-slate-300 hover:border-emerald-500 cursor-pointer text-slate-600'
                                  }`}
                                >
                                  <span className="truncate">{profilePicFile ? profilePicFile.name : (kycData?.profile_picture_path ? 'Profile Photo on Record' : 'Choose Headshot Photo')}</span>
                                  <Camera className="w-4 h-4 text-slate-400 shrink-0 ml-2" />
                                </label>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Section 4: Address & Emergency Contacts */}
                        <div className="p-4 bg-slate-50/50 border border-slate-200 rounded-2xl space-y-3">
                          <div className="flex items-center gap-2">
                            <MapPin className="w-4 h-4 text-emerald-700" />
                            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wide">4. Residential Address & Emergency Contacts</h4>
                          </div>
                          <div className="space-y-3">
                            <div>
                              <label className="block text-xs font-bold text-slate-700 mb-1">Residential Address</label>
                              <input
                                type="text"
                                required
                                disabled={isKycLocked}
                                placeholder="e.g. Flat 4B, Greenwood Heights, Park Street, Kolkata - 700016"
                                value={address}
                                onChange={(e) => setAddress(e.target.value)}
                                className={`w-full px-3.5 py-2.5 border rounded-xl text-xs transition ${
                                  isKycLocked
                                    ? 'bg-slate-100 border-slate-200 text-slate-500 cursor-not-allowed'
                                    : 'bg-white border-slate-200 text-slate-800 focus:outline-none focus:ring-1 focus:ring-emerald-500'
                                }`}
                              />
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <div>
                                <label className="block text-xs font-bold text-slate-700 mb-1">Emergency Contact Person</label>
                                <input
                                  type="text"
                                  required
                                  disabled={isKycLocked}
                                  placeholder="e.g. Father / Mother / Spouse"
                                  value={emergencyName}
                                  onChange={(e) => setEmergencyName(e.target.value)}
                                  className={`w-full px-3.5 py-2.5 border rounded-xl text-xs transition ${
                                    isKycLocked
                                      ? 'bg-slate-100 border-slate-200 text-slate-500 cursor-not-allowed'
                                      : 'bg-white border-slate-200 text-slate-800 focus:outline-none focus:ring-1 focus:ring-emerald-500'
                                  }`}
                                />
                              </div>
                              <div>
                                <label className="block text-xs font-bold text-slate-700 mb-1">Emergency Phone Number</label>
                                <input
                                  type="tel"
                                  required
                                  disabled={isKycLocked}
                                  placeholder="e.g. 9876543210"
                                  value={emergencyPhone}
                                  onChange={(e) => setEmergencyPhone(e.target.value)}
                                  className={`w-full px-3.5 py-2.5 border rounded-xl text-xs transition ${
                                    isKycLocked
                                      ? 'bg-slate-100 border-slate-200 text-slate-500 cursor-not-allowed'
                                      : 'bg-white border-slate-200 text-slate-800 focus:outline-none focus:ring-1 focus:ring-emerald-500'
                                  }`}
                                />
                              </div>
                            </div>
                          </div>
                        </div>

                        <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                          <p className="text-[11px] text-slate-500">
                            🔒 Documents are encrypted and securely stored for Admin identity verification only.
                          </p>
                          {isKycPending ? (
                            <div className="px-5 py-2.5 bg-amber-50 border border-amber-200 rounded-xl text-xs font-bold text-amber-800 flex items-center gap-2">
                              <Lock className="w-3.5 h-3.5 text-amber-600" />
                              <span>Documents Under Admin Review (Locked)</span>
                            </div>
                          ) : isKycVerified ? (
                            <div className="px-5 py-2.5 bg-emerald-50 border border-emerald-200 rounded-xl text-xs font-bold text-emerald-800 flex items-center gap-2">
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                              <span>KYC Verified & Approved</span>
                            </div>
                          ) : (
                            <button
                              type="submit"
                              disabled={kycLoading}
                              className={`px-6 py-2.5 text-xs font-bold rounded-xl shadow-xs transition flex items-center gap-2 ${
                                isKycRejected ? 'bg-rose-700 hover:bg-rose-800 text-white' : 'bg-emerald-700 hover:bg-emerald-800 text-white'
                              }`}
                            >
                              {kycLoading ? (
                                <>
                                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                                  <span>Uploading Documents...</span>
                                </>
                              ) : isKycRejected ? (
                                <>
                                  <Upload className="w-3.5 h-3.5" />
                                  <span>Re-submit KYC Documents for Review</span>
                                </>
                              ) : (
                                <>
                                  <Upload className="w-3.5 h-3.5" />
                                  <span>Submit KYC Documents</span>
                                </>
                              )}
                            </button>
                          )}
                        </div>
                      </form>
                    </div>
                  );
                })()
              )}
            </div>
          )}
        </main>
      </div>

      {/* Booking confirmation modal */}
      {selectedBike && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-100">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="text-base font-bold text-slate-900">Confirm Scooty Booking</h3>
              <button onClick={() => setSelectedBike(null)} className="text-slate-400 hover:text-slate-700">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="mt-4 space-y-4">
              <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
                <p className="text-sm font-bold text-slate-900">{selectedBike.bike_name}</p>
                <p className="text-xs text-slate-500">{selectedBike.registration_number} • {selectedBike.fuel_type}</p>

                <div className="mt-2.5 pt-2 border-t border-slate-200/60 grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-slate-400">Base Hourly Rate:</span>
                    <span className="font-bold text-slate-900 ml-1">₹{selectedBike.pricing?.hourly_rate || 100}/hr</span>
                  </div>
                  <div>
                    <span className="text-slate-400">Daily (24h) Rent:</span>
                    <span className="font-bold text-slate-900 ml-1">₹{selectedBike.pricing?.daily_rent}</span>
                  </div>
                </div>
              </div>

              {/* Rental Duration Selection */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="block text-xs font-bold text-slate-700">Choose Rental Duration</label>
                  <span className="text-xs font-extrabold text-emerald-800">
                    ₹{calculateRentForHours(selectedBike, selectedHours)} total rent
                  </span>
                </div>

                {/* Available Tariffs Pills */}
                <div className="grid grid-cols-3 gap-1.5">
                  {(selectedBike.tariffs && selectedBike.tariffs.length > 0 ? selectedBike.tariffs : [
                    { hours: 1, price: 100 },
                    { hours: 2, price: 190 },
                    { hours: 4, price: 360 },
                    { hours: 8, price: 680 },
                    { hours: 12, price: 950 },
                    { hours: 24, price: selectedBike.pricing?.daily_rent || 1800 }
                  ]).map(t => (
                    <button
                      key={t.hours}
                      type="button"
                      onClick={() => setSelectedHours(t.hours)}
                      className={`px-2.5 py-1.5 rounded-xl text-xs font-bold transition border text-center ${
                        selectedHours === t.hours
                          ? 'bg-emerald-800 text-white border-emerald-800 shadow-xs'
                          : 'bg-slate-50 hover:bg-slate-100 text-slate-700 border-slate-200'
                      }`}
                    >
                      <span className="block">{t.hours} hr{t.hours > 1 ? 's' : ''}</span>
                      <span className="text-[10px] opacity-90">₹{t.price}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Payment Method Selector */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">Select Payment Option</label>
                <div className="grid grid-cols-2 gap-2">
                  <div
                    onClick={() => setSelectedPaymentMethod('cod')}
                    className={`p-3 rounded-xl border cursor-pointer transition flex flex-col justify-between ${
                      selectedPaymentMethod === 'cod'
                        ? 'bg-emerald-50/80 border-emerald-600 ring-1 ring-emerald-600'
                        : 'bg-slate-50 border-slate-200 hover:bg-slate-100'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-extrabold text-slate-900">💵 Cash on Delivery</span>
                      {selectedPaymentMethod === 'cod' && <span className="w-2 h-2 rounded-full bg-emerald-600"></span>}
                    </div>
                    <p className="text-[10px] text-slate-500 leading-tight">Pay cash in hand to owner on vehicle handover</p>
                  </div>

                  <div
                    onClick={() => setSelectedPaymentMethod('razorpay')}
                    className={`p-3 rounded-xl border cursor-pointer transition flex flex-col justify-between ${
                      selectedPaymentMethod === 'razorpay'
                        ? 'bg-emerald-50/80 border-emerald-600 ring-1 ring-emerald-600'
                        : 'bg-slate-50 border-slate-200 hover:bg-slate-100'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-extrabold text-slate-900">⚡ UPI / Razorpay</span>
                      {selectedPaymentMethod === 'razorpay' && <span className="w-2 h-2 rounded-full bg-emerald-600"></span>}
                    </div>
                    <p className="text-[10px] text-slate-500 leading-tight">Instant prepay via UPI or Driver Wallet</p>
                  </div>
                </div>
              </div>

              {/* Calculation Summary */}
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-1">
                <div className="flex justify-between text-slate-600">
                  <span>Selected Duration:</span>
                  <span className="font-bold text-slate-900">{selectedHours} Hour(s)</span>
                </div>
                <div className="flex justify-between text-slate-600">
                  <span>Rent Amount:</span>
                  <span className="font-bold text-slate-900">₹{calculateRentForHours(selectedBike, selectedHours)}</span>
                </div>
                <div className="flex justify-between text-slate-600">
                  <span>Security Deposit:</span>
                  <span className="font-bold text-slate-900">
                    {selectedPaymentMethod === 'cod' ? '₹0 (COD Handover)' : `₹${selectedBike.pricing?.security_deposit || 0}`}
                  </span>
                </div>
                <div className="pt-1.5 border-t border-slate-200 flex justify-between text-sm font-extrabold text-emerald-950">
                  <span>Total Payable:</span>
                  <span>
                    ₹{selectedPaymentMethod === 'cod'
                      ? calculateRentForHours(selectedBike, selectedHours)
                      : calculateRentForHours(selectedBike, selectedHours) + (selectedBike.pricing?.security_deposit || 0)}
                  </span>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Message to Owner (Optional)</label>
                <textarea
                  value={bookingMsg}
                  onChange={(e) => setBookingMsg(e.target.value)}
                  placeholder="e.g. Commute to office from 9am to 6pm"
                  rows={2}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                ></textarea>
              </div>

              {bookingFeedback && (
                <div className={`p-3 rounded-xl text-xs font-semibold ${
                  bookingFeedback.type === 'success' ? 'bg-emerald-50 text-emerald-800' : 'bg-rose-50 text-rose-800'
                }`}>
                  {bookingFeedback.text}
                </div>
              )}

              <div className="flex gap-2 justify-end pt-2">
                <button
                  type="button"
                  onClick={() => setSelectedBike(null)}
                  className="px-4 py-2 border border-slate-200 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleBookScooty}
                  disabled={bookingLoading}
                  className="px-5 py-2 bg-emerald-700 hover:bg-emerald-800 text-white rounded-xl text-xs font-bold shadow-xs"
                >
                  {bookingLoading ? 'Submitting to Database...' : `Book (${selectedPaymentMethod.toUpperCase()})`}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Wallet Recharge Modal */}
      {showRechargeModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-sm w-full p-6 shadow-2xl border border-slate-100">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="text-base font-bold text-slate-900">Recharge Driver Wallet</h3>
              <button onClick={() => setShowRechargeModal(false)} className="text-slate-400 hover:text-slate-700">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleRecharge} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Enter Amount (Min ₹500)</label>
                <input
                  type="number"
                  min="500"
                  step="100"
                  value={rechargeAmount}
                  onChange={(e) => setRechargeAmount(Number(e.target.value))}
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-bold text-slate-900 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                />
              </div>

              <div className="flex gap-2">
                {[500, 1000, 2000].map(amt => (
                  <button
                    key={amt}
                    type="button"
                    onClick={() => setRechargeAmount(amt)}
                    className={`flex-1 py-1.5 rounded-lg text-xs font-bold border ${
                      rechargeAmount === amt
                        ? 'bg-emerald-50 border-emerald-500 text-emerald-800'
                        : 'border-slate-200 text-slate-600'
                    }`}
                  >
                    ₹{amt}
                  </button>
                ))}
              </div>

              {rechargeMsg && (
                <div className={`p-3 rounded-xl text-xs font-semibold ${
                  rechargeMsg.type === 'success' ? 'bg-emerald-50 text-emerald-800' : 'bg-rose-50 text-rose-800'
                }`}>
                  {rechargeMsg.text}
                </div>
              )}

              <div className="flex gap-2 justify-end pt-2">
                <button
                  type="button"
                  onClick={() => setShowRechargeModal(false)}
                  className="px-4 py-2 border border-slate-200 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-50"
                >
                  Close
                </button>
                <button
                  type="submit"
                  disabled={rechargeLoading}
                  className="px-5 py-2 bg-emerald-700 hover:bg-emerald-800 text-white rounded-xl text-xs font-bold shadow-xs"
                >
                  {rechargeLoading ? 'Processing...' : 'Pay via Razorpay'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
