import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import type { Bike, BookingRequest } from '../types';
import { MOCK_BIKES } from '../services/api';
import { 
  Search, ShieldCheck, Fuel, MapPin, 
  Wallet, CheckCircle2, AlertTriangle, Info, Clock 
} from 'lucide-react';

interface DriverViewProps {
  onOpenWallet: () => void;
}

export const DriverView: React.FC<DriverViewProps> = ({ onOpenWallet }) => {
  const { walletBalance, updateWalletBalance } = useAuth();
  
  const [activeTab, setActiveTab] = useState<'bikes' | 'my_booking' | 'kyc' | 'ledger'>('bikes');
  const [bikes] = useState<Bike[]>(MOCK_BIKES);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedBrand, setSelectedBrand] = useState<string>('all');
  const [selectedFuel, setSelectedFuel] = useState<string>('all');
  const [maxRent, setMaxRent] = useState<number>(1500);

  // Selected Bike for Booking Modal
  const [selectedBike, setSelectedBike] = useState<Bike | null>(null);
  const [bookingMessage, setBookingMessage] = useState('');
  const [bookingError, setBookingError] = useState<string | null>(null);
  const [bookingSuccess, setBookingSuccess] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Driver Active Booking State (Rule: Max 1 active rental)
  const [activeBooking, setActiveBooking] = useState<BookingRequest | null>(null);
  const [licenseNumber, setLicenseNumber] = useState('DL-1420110012345');
  const [aadhaarNumber, setAadhaarNumber] = useState('987654321098');
  const [emergencyContact, setEmergencyContact] = useState('Jane Doe (9876543210)');
  const [kycSubmitted, setKycSubmitted] = useState(true);

  // Filtering
  const filteredBikes = bikes.filter((bike) => {
    const matchesSearch = bike.bike_name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          bike.brand.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesBrand = selectedBrand === 'all' || bike.brand.toLowerCase() === selectedBrand.toLowerCase();
    const matchesFuel = selectedFuel === 'all' || bike.fuel_type === selectedFuel;
    const matchesPrice = (bike.pricing?.daily_rent ?? 0) <= maxRent;
    return matchesSearch && matchesBrand && matchesFuel && matchesPrice;
  });

  const handleCreateBooking = () => {
    if (!selectedBike) return;
    setBookingError(null);
    setBookingSuccess(null);

    // Rule 1: Driver can only hold 1 active booking at a time
    if (activeBooking) {
      setBookingError('Booking Rejected: You already have 1 active booking. Driver constraint allows only 1 active rental at a time.');
      return;
    }

    // Rule 2: Wallet balance >= Total required (Rent + Security Deposit)
    const rent = selectedBike.pricing?.daily_rent ?? 0;
    const deposit = selectedBike.pricing?.security_deposit ?? 0;
    const totalRequired = rent + deposit;

    if (walletBalance < totalRequired) {
      setBookingError(
        `Booking Failed: Insufficient wallet balance. Total required: ₹${totalRequired.toLocaleString('en-IN')} (Daily Rent ₹${rent} + Security Deposit ₹${deposit}). Available in wallet: ₹${walletBalance.toLocaleString('en-IN')}. Please top up your wallet.`
      );
      return;
    }

    setIsSubmitting(true);

    setTimeout(() => {
      setIsSubmitting(false);
      
      // Deduct wallet balance
      const newBal = walletBalance - totalRequired;
      updateWalletBalance(newBal);

      const newBooking: BookingRequest = {
        id: `req-${Date.now()}`,
        driver_user_id: 'driver-1',
        bike_id: selectedBike.id,
        status: 'accepted',
        message: bookingMessage || 'Requesting bike for rental.',
        requested_at: new Date().toISOString(),
        bike: selectedBike,
      };

      setActiveBooking(newBooking);
      setBookingSuccess(`Booking request approved! ₹${totalRequired.toLocaleString('en-IN')} deducted from wallet and bike assigned.`);
      
      setTimeout(() => {
        setBookingSuccess(null);
        setSelectedBike(null);
        setActiveTab('my_booking');
      }, 1500);
    }, 1200);
  };

  return (
    <div className="space-y-6">
      
      {/* Sub-Navigation Tabs */}
      <div className="flex items-center space-x-2 border-b border-slate-800 pb-3 overflow-x-auto">
        <button
          onClick={() => setActiveTab('bikes')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 whitespace-nowrap cursor-pointer ${
            activeTab === 'bikes'
              ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 glow-cyan'
              : 'text-slate-400 hover:text-white hover:bg-slate-900'
          }`}
        >
          <Search className="w-4 h-4" />
          <span>Explore Fleet</span>
        </button>

        <button
          onClick={() => setActiveTab('my_booking')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 whitespace-nowrap cursor-pointer ${
            activeTab === 'my_booking'
              ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 glow-cyan'
              : 'text-slate-400 hover:text-white hover:bg-slate-900'
          }`}
        >
          <Clock className="w-4 h-4" />
          <span>My Active Rental {activeBooking && <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse ml-1"></span>}</span>
        </button>

        <button
          onClick={() => setActiveTab('kyc')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 whitespace-nowrap cursor-pointer ${
            activeTab === 'kyc'
              ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 glow-cyan'
              : 'text-slate-400 hover:text-white hover:bg-slate-900'
          }`}
        >
          <ShieldCheck className="w-4 h-4" />
          <span>Driver KYC Verification</span>
        </button>

        <button
          onClick={() => setActiveTab('ledger')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 whitespace-nowrap cursor-pointer ${
            activeTab === 'ledger'
              ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 glow-cyan'
              : 'text-slate-400 hover:text-white hover:bg-slate-900'
          }`}
        >
          <Wallet className="w-4 h-4" />
          <span>Wallet Ledger</span>
        </button>
      </div>

      {/* TAB 1: BIKES CATALOG & FILTER */}
      {activeTab === 'bikes' && (
        <div className="space-y-6">
          
          {/* Filter Bar */}
          <div className="glass-panel rounded-2xl p-4 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
              
              {/* Search input */}
              <div className="relative md:col-span-2">
                <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search bike by name, brand, or model..."
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                />
              </div>

              {/* Brand Filter */}
              <div>
                <select
                  value={selectedBrand}
                  onChange={(e) => setSelectedBrand(e.target.value)}
                  className="w-full py-2.5 px-3 rounded-xl bg-slate-900/90 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                >
                  <option value="all">All Brands</option>
                  <option value="Yamaha">Yamaha</option>
                  <option value="Royal Enfield">Royal Enfield</option>
                  <option value="Ather">Ather Electric</option>
                  <option value="KTM">KTM</option>
                </select>
              </div>

              {/* Fuel Type */}
              <div>
                <select
                  value={selectedFuel}
                  onChange={(e) => setSelectedFuel(e.target.value)}
                  className="w-full py-2.5 px-3 rounded-xl bg-slate-900/90 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                >
                  <option value="all">All Fuel Types</option>
                  <option value="petrol">Petrol</option>
                  <option value="electric">Electric EV</option>
                </select>
              </div>

            </div>

            {/* Price Slider */}
            <div className="flex items-center space-x-4 pt-2 border-t border-slate-800/80">
              <span className="text-xs font-semibold text-slate-400">Max Daily Rent: <span className="text-cyan-400 font-bold">₹{maxRent}/day</span></span>
              <input
                type="range"
                min="400"
                max="2000"
                step="50"
                value={maxRent}
                onChange={(e) => setMaxRent(Number(e.target.value))}
                className="w-full max-w-xs accent-cyan-400 h-1.5 bg-slate-800 rounded-lg cursor-pointer"
              />
            </div>
          </div>

          {/* Bike Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {filteredBikes.map((bike) => (
              <div key={bike.id} className="glass-card rounded-2xl overflow-hidden group transition-all duration-300 hover:-translate-y-1">
                
                {/* Image Banner */}
                <div className="relative h-48 w-full overflow-hidden bg-slate-900">
                  <img
                    src={bike.image_urls?.[0]}
                    alt={bike.bike_name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent opacity-80"></div>
                  
                  {/* Status Badge */}
                  <span className={`absolute top-3 left-3 px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                    bike.status === 'available'
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 backdrop-blur-md'
                      : 'bg-amber-500/20 text-amber-400 border border-amber-500/30 backdrop-blur-md'
                  }`}>
                    {bike.status}
                  </span>

                  <span className="absolute top-3 right-3 px-2 py-1 rounded-lg text-[10px] font-bold bg-slate-900/80 text-slate-300 border border-slate-700/50 backdrop-blur-md flex items-center space-x-1">
                    <MapPin className="w-3 h-3 text-cyan-400" />
                    <span>{bike.city}</span>
                  </span>

                  <div className="absolute bottom-3 left-3 right-3 flex items-end justify-between">
                    <div>
                      <h4 className="text-base font-bold text-white group-hover:text-cyan-400 transition-colors">{bike.bike_name}</h4>
                      <p className="text-xs text-slate-300">{bike.brand} • {bike.color}</p>
                    </div>
                  </div>
                </div>

                {/* Spec Badges & Rent */}
                <div className="p-4 space-y-4">
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="p-2 rounded-xl bg-slate-900/60 border border-slate-800/60 flex items-center space-x-2">
                      <Fuel className="w-3.5 h-3.5 text-cyan-400" />
                      <span className="capitalize text-slate-300">{bike.fuel_type}</span>
                    </div>
                    <div className="p-2 rounded-xl bg-slate-900/60 border border-slate-800/60 flex items-center space-x-2">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                      <span className="text-slate-300">Verified Listing</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t border-slate-800/60">
                    <div>
                      <p className="text-[10px] text-slate-400 uppercase tracking-wider">Daily Rate</p>
                      <p className="text-lg font-black text-cyan-400">
                        ₹{bike.pricing?.daily_rent} <span className="text-xs text-slate-400 font-normal">/ day</span>
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-[10px] text-slate-400 uppercase tracking-wider">Deposit</p>
                      <p className="text-xs font-bold text-slate-300">
                        ₹{bike.pricing?.security_deposit}
                      </p>
                    </div>
                  </div>

                  {/* Book CTA */}
                  <button
                    onClick={() => setSelectedBike(bike)}
                    disabled={bike.status !== 'available'}
                    className={`w-full py-2.5 rounded-xl font-bold text-xs uppercase tracking-wider transition-all flex items-center justify-center space-x-2 cursor-pointer ${
                      bike.status === 'available'
                        ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40'
                        : 'bg-slate-800 text-slate-500 cursor-not-allowed'
                    }`}
                  >
                    <span>{bike.status === 'available' ? 'Book Bike' : 'Currently Assigned'}</span>
                  </button>
                </div>

              </div>
            ))}
          </div>

        </div>
      )}

      {/* TAB 2: MY ACTIVE RENTAL */}
      {activeTab === 'my_booking' && (
        <div className="space-y-6 max-w-3xl mx-auto">
          {activeBooking ? (
            <div className="glass-panel rounded-3xl p-6 space-y-6 glow-cyan">
              <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                    <CheckCircle2 className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">Active Rental Assignment</h3>
                    <p className="text-xs text-slate-400">Booking ID: {activeBooking.id}</p>
                  </div>
                </div>
                <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-bold uppercase tracking-wider animate-pulse">
                  ACTIVE RENTAL
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
                  <p className="text-xs text-slate-400 uppercase tracking-wider">Vehicle Details</p>
                  <p className="text-base font-bold text-white">{activeBooking.bike?.bike_name}</p>
                  <p className="text-xs text-cyan-400">Reg: {activeBooking.bike?.registration_number}</p>
                  <p className="text-xs text-slate-300">Fuel: {activeBooking.bike?.fuel_type}</p>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
                  <p className="text-xs text-slate-400 uppercase tracking-wider">Financial Breakdown</p>
                  <p className="text-xs text-slate-300">Daily Rent Paid: <span className="font-bold text-white">₹{activeBooking.bike?.pricing?.daily_rent}</span></p>
                  <p className="text-xs text-slate-300">Security Deposit Held: <span className="font-bold text-emerald-400">₹{activeBooking.bike?.pricing?.security_deposit}</span></p>
                  <p className="text-[10px] text-slate-500 mt-1">*Deposit refunded upon return after owner inspection.</p>
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-xs text-cyan-300 flex items-start space-x-3">
                <Info className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
                <p>
                  Driver constraint active: You can hold a maximum of 1 active rental. To book another bike, return this vehicle to the owner for inspection and deposit release.
                </p>
              </div>
            </div>
          ) : (
            <div className="glass-panel rounded-3xl p-12 text-center space-y-4">
              <div className="w-16 h-16 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-500 mx-auto">
                <Clock className="w-8 h-8" />
              </div>
              <h3 className="text-lg font-bold text-white">No Active Bike Rental</h3>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">
                Explore our verified fleet catalog to rent a bike. Your wallet balance is ₹{walletBalance.toLocaleString('en-IN')}.
              </p>
              <button
                onClick={() => setActiveTab('bikes')}
                className="px-6 py-2.5 rounded-xl bg-cyan-500 text-slate-950 font-bold text-xs uppercase tracking-wider hover:bg-cyan-400 transition-all cursor-pointer"
              >
                Browse Fleet
              </button>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: DRIVER KYC */}
      {activeTab === 'kyc' && (
        <div className="glass-panel rounded-3xl p-6 max-w-2xl mx-auto space-y-6">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <div>
              <h3 className="text-base font-bold text-white">Driver Verification Documents</h3>
              <p className="text-xs text-slate-400">KYC verification required before booking bikes.</p>
            </div>
            <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-bold">
              VERIFIED
            </span>
          </div>

          <div className="space-y-4 text-xs">
            {kycSubmitted && (
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-bold flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4" />
                <span>Driver credentials updated and submitted for verification!</span>
              </div>
            )}
            <div>
              <label className="block text-slate-400 mb-1">Driving License Number</label>
              <input
                type="text"
                value={licenseNumber}
                onChange={(e) => setLicenseNumber(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-white font-mono"
              />
            </div>

            <div>
              <label className="block text-slate-400 mb-1">Aadhaar Number</label>
              <input
                type="text"
                value={aadhaarNumber}
                onChange={(e) => setAadhaarNumber(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-white font-mono"
              />
            </div>

            <div>
              <label className="block text-slate-400 mb-1">Emergency Contact</label>
              <input
                type="text"
                value={emergencyContact}
                onChange={(e) => setEmergencyContact(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-white"
              />
            </div>

            <button
              onClick={() => setKycSubmitted(true)}
              className="w-full py-3 rounded-xl bg-slate-800 text-cyan-400 font-bold hover:bg-slate-700 transition-colors cursor-pointer"
            >
              Update Driver Credentials
            </button>
          </div>
        </div>
      )}

      {/* TAB 4: WALLET LEDGER */}
      {activeTab === 'ledger' && (
        <div className="glass-panel rounded-3xl p-6 max-w-4xl mx-auto space-y-6">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <div>
              <h3 className="text-base font-bold text-white">Wallet Transaction Ledger</h3>
              <p className="text-xs text-slate-400">Recharge history & rental deductions</p>
            </div>
            <button
              onClick={onOpenWallet}
              className="px-4 py-2 rounded-xl bg-emerald-500 text-slate-950 font-bold text-xs hover:bg-emerald-400 transition-colors cursor-pointer"
            >
              + Top Up Wallet
            </button>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-400 uppercase tracking-wider">Current Balance</p>
              <p className="text-2xl font-black text-emerald-400">₹{walletBalance.toLocaleString('en-IN')}</p>
            </div>
            <span className="text-xs text-slate-400">Min Recharge: ₹500</span>
          </div>

          <div className="space-y-3">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Recent Ledger Entries</h4>
            <div className="space-y-2">
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between text-xs">
                <div>
                  <p className="font-semibold text-white">Razorpay Wallet Top Up</p>
                  <p className="text-[10px] text-slate-400">Txn ID: rzp_pay_998124</p>
                </div>
                <span className="font-bold text-emerald-400">+ ₹2,500</span>
              </div>
              {activeBooking && (
                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between text-xs">
                  <div>
                    <p className="font-semibold text-white">Rental Deduction ({activeBooking.bike?.bike_name})</p>
                    <p className="text-[10px] text-slate-400">Rent + Security Deposit</p>
                  </div>
                  <span className="font-bold text-rose-400">- ₹{((activeBooking.bike?.pricing?.daily_rent ?? 0) + (activeBooking.bike?.pricing?.security_deposit ?? 0)).toLocaleString('en-IN')}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* BOOKING REQUEST MODAL */}
      {selectedBike && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in">
          <div className="relative w-full max-w-lg glass-panel rounded-3xl p-6 border border-slate-800 shadow-2xl space-y-5">
            
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <h3 className="text-base font-bold text-white">Confirm Rental Request</h3>
              <button onClick={() => setSelectedBike(null)} className="text-slate-400 hover:text-white">✕</button>
            </div>

            <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 space-y-2 text-xs">
              <p className="font-bold text-white text-sm">{selectedBike.bike_name}</p>
              <p className="text-slate-400">{selectedBike.brand} • {selectedBike.color} • {selectedBike.registration_number}</p>
              <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-xs">
                <span>Daily Rent: <b className="text-white">₹{selectedBike.pricing?.daily_rent}</b></span>
                <span>Deposit: <b className="text-emerald-400">₹{selectedBike.pricing?.security_deposit}</b></span>
              </div>
              <div className="pt-2 border-t border-slate-800 text-xs font-bold text-cyan-400 flex justify-between">
                <span>Total Upfront Required:</span>
                <span>₹{(selectedBike.pricing?.daily_rent ?? 0) + (selectedBike.pricing?.security_deposit ?? 0)}</span>
              </div>
            </div>

            <div>
              <label className="block text-xs text-slate-300 mb-1">Message to Owner (Optional)</label>
              <textarea
                value={bookingMessage}
                onChange={(e) => setBookingMessage(e.target.value)}
                placeholder="e.g. Need bike for 3 days starting tomorrow morning..."
                className="w-full p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:border-cyan-500 h-20 resize-none"
              />
            </div>

            {bookingError && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-400 flex items-start space-x-2">
                <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                <p>{bookingError}</p>
              </div>
            )}

            {bookingSuccess && (
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-400 flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <p>{bookingSuccess}</p>
              </div>
            )}

            <div className="flex space-x-3">
              <button
                onClick={() => setSelectedBike(null)}
                className="w-1/3 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 font-bold text-xs hover:bg-slate-800 cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateBooking}
                disabled={isSubmitting}
                className="w-2/3 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold text-xs uppercase tracking-wider shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 cursor-pointer flex items-center justify-center"
              >
                {isSubmitting ? 'Processing Request...' : 'Confirm & Deduct Wallet'}
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};
