import React, { useState } from 'react';
import type { Bike } from '../types';
import { MOCK_BIKES } from '../services/api';
import { 
  PlusCircle, ShieldCheck, CheckCircle2, Wrench, 
  DollarSign, Upload, ArrowUpRight, Bike as BikeIcon 
} from 'lucide-react';

export const OwnerView: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<'fleet' | 'requests' | 'add_bike' | 'inspection'>('fleet');
  const [ownerBikes, setOwnerBikes] = useState<Bike[]>(MOCK_BIKES.filter(b => b.owner_user_id === 'owner-1'));
  
  // New Bike Form
  const [bikeName, setBikeName] = useState('');
  const [brand, setBrand] = useState('Yamaha');
  const [model, setModel] = useState('');
  const [regNo, setRegNo] = useState('');
  const [color, setColor] = useState('Black');
  const [fuelType, setFuelType] = useState('petrol');
  const [dailyRent, setDailyRent] = useState('700');
  const [deposit, setDeposit] = useState('1800');
  const [addBikeSuccess, setAddBikeSuccess] = useState<string | null>(null);

  // Return Inspection Modal State
  const [showInspectionModal, setShowInspectionModal] = useState(false);
  const [selectedInspectionBike, setSelectedInspectionBike] = useState<Bike | null>(null);
  const [isDamaged, setIsDamaged] = useState(false);
  const [damageCharge, setDamageCharge] = useState('0');
  const [inspectionNotes, setInspectionNotes] = useState('');
  const [refundResult, setRefundResult] = useState<string | null>(null);

  const handleCreateBike = (e: React.FormEvent) => {
    e.preventDefault();
    if (!bikeName || !model || !regNo) return;

    const newBike: Bike = {
      id: `bike-${Date.now()}`,
      owner_user_id: 'owner-1',
      bike_name: bikeName,
      brand,
      model,
      registration_number: regNo,
      color,
      fuel_type: fuelType as any,
      ownership_type: 'self',
      status: 'inactive',
      verification_status: 'draft',
      is_active: true,
      city: 'Kolkata',
      pricing: {
        daily_rent: Number(dailyRent),
        security_deposit: Number(deposit),
        late_fee_per_day: 150,
      },
      image_urls: ['https://images.unsplash.com/photo-1558981806-ec527fa84c39?auto=format&fit=crop&w=800&q=80'],
      created_at: new Date().toISOString(),
    };

    setOwnerBikes([newBike, ...ownerBikes]);
    setAddBikeSuccess(`Bike "${bikeName}" submitted as Draft! Admin will verify RC & Insurance documents.`);
    
    setTimeout(() => {
      setAddBikeSuccess(null);
      setActiveSubTab('fleet');
      setBikeName('');
      setRegNo('');
      setModel('');
    }, 1500);
  };

  const handleReturnInspection = () => {
    if (!selectedInspectionBike) return;
    const damage = Number(damageCharge) || 0;
    const depositAmt = selectedInspectionBike.pricing?.security_deposit || 1500;
    const netRefund = Math.max(0, depositAmt - damage);

    setRefundResult(
      `Return Inspection Completed! Security Deposit ₹${depositAmt} - Damage Fee ₹${damage} = Net Refund ₹${netRefund} credited back to driver's wallet. Bike status set to AVAILABLE.`
    );

    setTimeout(() => {
      setRefundResult(null);
      setShowInspectionModal(false);
      setSelectedInspectionBike(null);
    }, 2000);
  };

  return (
    <div className="space-y-6">
      
      {/* Owner Header KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div className="glass-panel rounded-2xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Fleet Total</p>
            <p className="text-2xl font-black text-white mt-1">{ownerBikes.length} Bikes</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
            <BikeIcon className="w-5 h-5" />
          </div>
        </div>

        <div className="glass-panel rounded-2xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Monthly Payouts</p>
            <p className="text-2xl font-black text-emerald-400 mt-1">₹42,500</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <DollarSign className="w-5 h-5" />
          </div>
        </div>

        <div className="glass-panel rounded-2xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Active Rentals</p>
            <p className="text-2xl font-black text-indigo-400 mt-1">
              {ownerBikes.filter(b => b.status === 'assigned').length} Bikes
            </p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <ArrowUpRight className="w-5 h-5" />
          </div>
        </div>

        <div className="glass-panel rounded-2xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">KYC Status</p>
            <p className="text-sm font-bold text-emerald-400 mt-1 flex items-center space-x-1">
              <ShieldCheck className="w-4 h-4" />
              <span>Owner Verified</span>
            </p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <ShieldCheck className="w-5 h-5" />
          </div>
        </div>

      </div>

      {/* Navigation Sub-Tabs */}
      <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
        <button
          onClick={() => setActiveSubTab('fleet')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
            activeSubTab === 'fleet'
              ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 glow-cyan'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          My Fleet ({ownerBikes.length})
        </button>

        <button
          onClick={() => setActiveSubTab('add_bike')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-1 cursor-pointer ${
            activeSubTab === 'add_bike'
              ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 glow-cyan'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <PlusCircle className="w-4 h-4" />
          <span>Add New Bike</span>
        </button>

        <button
          onClick={() => setActiveSubTab('requests')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
            activeSubTab === 'requests'
              ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 glow-cyan'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          Incoming Booking Requests (1)
        </button>
      </div>

      {/* SUBTAB 1: FLEET LIST */}
      {activeSubTab === 'fleet' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {ownerBikes.map((bike) => (
            <div key={bike.id} className="glass-card rounded-2xl p-5 space-y-4 relative">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-base font-bold text-white">{bike.bike_name}</h4>
                  <p className="text-xs text-slate-400">{bike.registration_number}</p>
                </div>
                <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase ${
                  bike.verification_status === 'verified'
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                }`}>
                  {bike.verification_status}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                  <p className="text-[10px] text-slate-500 uppercase">Daily Rent</p>
                  <p className="text-sm font-bold text-cyan-400">₹{bike.pricing?.daily_rent}</p>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                  <p className="text-[10px] text-slate-500 uppercase">Deposit</p>
                  <p className="text-sm font-bold text-slate-200">₹{bike.pricing?.security_deposit}</p>
                </div>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-slate-800">
                <span className="text-xs text-slate-400">Status: <b className="text-white capitalize">{bike.status}</b></span>
                {bike.status === 'assigned' && (
                  <button
                    onClick={() => {
                      setSelectedInspectionBike(bike);
                      setShowInspectionModal(true);
                    }}
                    className="px-3 py-1.5 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/30 text-xs font-bold hover:bg-amber-500/20 transition-all cursor-pointer flex items-center space-x-1"
                  >
                    <Wrench className="w-3.5 h-3.5" />
                    <span>Return Inspection</span>
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* SUBTAB 2: ADD BIKE */}
      {activeSubTab === 'add_bike' && (
        <form onSubmit={handleCreateBike} className="glass-panel rounded-3xl p-6 max-w-2xl mx-auto space-y-5">
          <div className="pb-4 border-b border-slate-800">
            <h3 className="text-base font-bold text-white">Add New Bike to Fleet</h3>
            <p className="text-xs text-slate-400">Listing starts as Draft until Admin verifies RC & Insurance</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block text-slate-300 mb-1 font-semibold">Bike Name</label>
              <input
                type="text"
                required
                value={bikeName}
                onChange={(e) => setBikeName(e.target.value)}
                placeholder="Yamaha FZ 25"
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-white focus:outline-none focus:border-cyan-500"
              />
            </div>

            <div>
              <label className="block text-slate-300 mb-1 font-semibold">Brand</label>
              <select
                value={brand}
                onChange={(e) => setBrand(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-white focus:outline-none focus:border-cyan-500"
              >
                <option value="Yamaha">Yamaha</option>
                <option value="Royal Enfield">Royal Enfield</option>
                <option value="Ather">Ather Electric</option>
                <option value="KTM">KTM</option>
                <option value="Honda">Honda</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-300 mb-1 font-semibold">Model</label>
              <input
                type="text"
                required
                value={model}
                onChange={(e) => setModel(e.target.value)}
                placeholder="FZ 25 BS6"
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-white focus:outline-none focus:border-cyan-500"
              />
            </div>

            <div>
              <label className="block text-slate-300 mb-1 font-semibold">Color</label>
              <input
                type="text"
                value={color}
                onChange={(e) => setColor(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-white focus:outline-none focus:border-cyan-500"
              />
            </div>

            <div>
              <label className="block text-slate-300 mb-1 font-semibold">Fuel Type</label>
              <select
                value={fuelType}
                onChange={(e) => setFuelType(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-white focus:outline-none focus:border-cyan-500"
              >
                <option value="petrol">Petrol</option>
                <option value="electric">Electric EV</option>
                <option value="diesel">Diesel</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-300 mb-1 font-semibold">Daily Rent (INR)</label>
              <input
                type="number"
                required
                value={dailyRent}
                onChange={(e) => setDailyRent(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-white focus:outline-none focus:border-cyan-500"
              />
            </div>

            <div>
              <label className="block text-slate-300 mb-1 font-semibold">Security Deposit (INR)</label>
              <input
                type="number"
                required
                value={deposit}
                onChange={(e) => setDeposit(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-white focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          {/* Document File Uploader Placeholders */}
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-dashed border-slate-800 space-y-2">
            <p className="text-xs font-semibold text-slate-300 flex items-center space-x-2">
              <Upload className="w-4 h-4 text-cyan-400" />
              <span>Upload RC, Insurance & Pollution Documents</span>
            </p>
            <p className="text-[10px] text-slate-500">Supports PDF, PNG, JPEG formats up to 10MB.</p>
          </div>

          {addBikeSuccess && (
            <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-400 flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <p>{addBikeSuccess}</p>
            </div>
          )}

          <button
            type="submit"
            className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold text-xs uppercase tracking-wider shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 transition-all cursor-pointer"
          >
            Submit Bike for Verification
          </button>
        </form>
      )}

      {/* RETURN INSPECTION MODAL */}
      {showInspectionModal && selectedInspectionBike && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in">
          <div className="relative w-full max-w-md glass-panel rounded-3xl p-6 border border-slate-800 shadow-2xl space-y-5">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <h3 className="text-base font-bold text-white">Return Inspection & Deposit Refund</h3>
              <button onClick={() => setShowInspectionModal(false)} className="text-slate-400 hover:text-white">✕</button>
            </div>

            <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs">
              <p className="font-bold text-white">{selectedInspectionBike.bike_name}</p>
              <p className="text-slate-400">Security Deposit Held: ₹{selectedInspectionBike.pricing?.security_deposit}</p>
            </div>

            <div className="space-y-3 text-xs">
              <label className="flex items-center space-x-2 text-slate-300 font-semibold cursor-pointer">
                <input
                  type="checkbox"
                  checked={isDamaged}
                  onChange={(e) => setIsDamaged(e.target.checked)}
                  className="rounded bg-slate-900 border-slate-800 text-cyan-500 focus:ring-0"
                />
                <span>Bike has damage / scratch</span>
              </label>

              {isDamaged && (
                <div>
                  <label className="block text-slate-400 mb-1">Damage Deduction Amount (INR)</label>
                  <input
                    type="number"
                    value={damageCharge}
                    onChange={(e) => setDamageCharge(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-white"
                  />
                </div>
              )}

              <div>
                <label className="block text-slate-400 mb-1">Inspection Notes</label>
                <textarea
                  value={inspectionNotes}
                  onChange={(e) => setInspectionNotes(e.target.value)}
                  placeholder="Returned on time, battery intact, minor scratches..."
                  className="w-full p-3 rounded-xl bg-slate-900 border border-slate-800 text-white h-16 text-xs resize-none"
                />
              </div>
            </div>

            {refundResult && (
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-400">
                {refundResult}
              </div>
            )}

            <button
              onClick={handleReturnInspection}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 text-slate-950 font-bold text-xs uppercase tracking-wider shadow-lg shadow-emerald-500/25 cursor-pointer"
            >
              Complete Inspection & Issue Refund
            </button>
          </div>
        </div>
      )}

    </div>
  );
};
