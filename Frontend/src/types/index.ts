export type UserRole = 'driver' | 'owner' | 'admin';
export type VerificationStatus = 'draft' | 'pending' | 'verified' | 'rejected';
export type UserStatus = 'active' | 'blocked' | 'deleted';
export type BikeStatus = 'inactive' | 'available' | 'assigned' | 'under_maintenance';

export interface User {
  id: string;
  full_name: string;
  email: string;
  phone: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  wallet_balance?: number;
  verification_status?: VerificationStatus;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface BikePricing {
  daily_rent: number;
  weekly_rent?: number;
  monthly_rent?: number;
  security_deposit: number;
  late_fee_per_day: number;
}

export interface BikeDocuments {
  rc_file_path?: string;
  insurance_file_path?: string;
  pollution_file_path?: string;
  permit_file_path?: string;
}

export interface Bike {
  id: string;
  owner_user_id: string;
  bike_name: string;
  brand: string;
  model: string;
  registration_number: string;
  color?: string;
  fuel_type: 'petrol' | 'electric' | 'diesel' | 'cng';
  ownership_type: 'self' | 'leased' | 'financed';
  status: BikeStatus;
  verification_status: VerificationStatus;
  is_active: boolean;
  pricing?: BikePricing;
  documents?: BikeDocuments;
  image_urls?: string[];
  city?: string;
  created_at: string;
}

export interface BookingRequest {
  id: string;
  driver_user_id: string;
  bike_id: string;
  status: 'pending' | 'accepted' | 'rejected' | 'cancelled';
  message?: string;
  requested_at: string;
  bike?: Bike;
  driver_name?: string;
}

export interface Assignment {
  id: string;
  driver_user_id: string;
  owner_user_id: string;
  bike_id: string;
  daily_rent_amount: number;
  security_deposit_amount: number;
  status: 'active' | 'completed' | 'cancelled';
  start_time: string;
  end_time?: string;
  bike?: Bike;
}

export interface Wallet {
  id: string;
  user_id: string;
  balance: number;
}

export interface WalletTransaction {
  id: string;
  wallet_id: string;
  amount: number;
  txn_type: 'recharge' | 'debit' | 'credit' | 'refund' | 'admin_adjustment';
  status: 'pending' | 'success' | 'failed';
  reference_id?: string;
  description?: string;
  created_at: string;
}

export interface NotificationItem {
  id: string;
  user_id: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface SupportTicket {
  id: string;
  user_id: string;
  subject: string;
  description: string;
  status: 'open' | 'resolved' | 'rejected';
  created_at: string;
  user_name?: string;
}

export interface AdminDashboardStats {
  total_users: number;
  total_owners: number;
  total_drivers: number;
  total_bikes: number;
  active_rentals: number;
  gross_revenue: number;
  platform_commission: number;
  pending_owner_verifications: number;
  pending_bike_verifications: number;
}
