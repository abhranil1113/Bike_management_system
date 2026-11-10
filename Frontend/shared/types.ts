// Frontend/shared/types.ts

export type UserRole = 'driver' | 'owner' | 'admin' | string;
export type VerificationStatus = 'draft' | 'pending' | 'verified' | 'rejected' | string;
export type UserStatus = 'active' | 'blocked' | 'deleted' | string;
export type BikeStatus = 'available' | 'assigned' | 'rented' | 'maintenance' | 'inactive';
export type FuelType = 'petrol' | 'diesel' | 'electric' | 'cng' | string;

export interface User {
  id: string;
  full_name?: string;
  email: string;
  phone?: string;
  role: UserRole;
  is_active: boolean;
  is_verified?: boolean;
  wallet_balance?: number;
  created_at?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface BikePricing {
  daily_rent: number;
  hourly_rate?: number;
  weekly_rent?: number | null;
  monthly_rent?: number | null;
  security_deposit: number;
  late_fee_per_day?: number;
  late_fee_per_hour?: number;
  damage_protection_fee?: number;
}

export interface BikeTariff {
  id?: string;
  bike_id?: string;
  hours: number;
  price: number;
}

export interface BikeDocuments {
  rc?: string | null;
  insurance?: string | null;
  pollution?: string | null;
  permit?: string | null;
}

export interface BikeImageItem {
  id?: string;
  image_url: string;
  is_primary?: boolean;
}

export interface Bike {
  id: string;
  owner_user_id: string;
  owner_email?: string;
  bike_name: string;
  brand: string;
  model: string;
  registration_number: string;
  color?: string | null;
  fuel_type: FuelType;
  ownership_type: string;
  km_driven: number;
  year_of_purchase?: number | null;
  status: BikeStatus;
  verification_status: VerificationStatus;
  is_active: boolean;
  pricing?: BikePricing | null;
  tariffs?: BikeTariff[];
  documents?: BikeDocuments | null;
  images?: (string | BikeImageItem)[];
  created_at?: string | null;
}

export interface BookingRequest {
  id: string;
  bike_id: string;
  bike_name?: string;
  registration_number?: string;
  driver_user_id: string;
  driver_name?: string;
  driver_phone?: string;
  status: 'pending' | 'approved' | 'rejected' | 'cancelled' | 'refunded' | string;
  message?: string | null;
  rental_hours?: number;
  total_amount?: number;
  payment_method?: 'cod' | 'razorpay' | 'upi' | string;
  cash_received?: boolean;
  cash_received_at?: string | null;
  approved_at?: string | null;
  rejected_reason?: string | null;
  created_at?: string | null;
  daily_rent?: number;
  security_deposit?: number;
  bike?: Bike;
}

export interface ActiveAssignment {
  id: string;
  bike_id: string;
  bike_name?: string;
  registration_number?: string;
  driver_user_id?: string;
  owner_user_id?: string;
  driver_name?: string;
  driver_phone?: string;
  assigned_at: string;
  daily_rent_amount: number;
  total_rent_amount?: number;
  rental_hours?: number;
  payment_method?: 'cod' | 'razorpay' | 'upi' | string;
  cash_received?: boolean;
  cash_received_at?: string | null;
  cod_admin_escalated?: boolean;
  security_deposit_amount: number;
  status: string;
  bike?: Bike;
}

export interface WalletTransaction {
  id: string;
  amount: number;
  type?: 'credit' | 'debit' | string;
  txn_type?: 'recharge' | 'debit' | 'credit' | 'refund' | 'admin_adjustment';
  status: 'pending' | 'success' | 'completed' | 'failed' | string;
  reference_id?: string | null;
  description?: string | null;
  created_at: string;
}

export interface WalletData {
  wallet_id: string;
  balance: number;
  transactions: WalletTransaction[];
}

export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  is_read?: boolean;
  read_at?: string | null;
  created_at?: string | null;
}

export interface AdminStats {
  total_users: number;
  total_owners?: number;
  total_drivers?: number;
  active_drivers?: number;
  active_owners?: number;
  total_bikes: number;
  available_bikes?: number;
  assigned_bikes?: number;
  active_rentals?: number;
  pending_owner_verifications?: number;
  pending_driver_verifications?: number;
  pending_bike_verifications?: number;
  total_revenue?: number;
  total_platform_commission?: number;
  cod_unpaid_count?: number;
  cod_escalations_count?: number;
  gross_revenue: number;
  platform_commission: number;
}

export interface CodEscalationItem {
  assignment_id: string;
  bike_name: string;
  registration_number: string;
  driver_name: string;
  driver_email: string;
  driver_phone: string;
  owner_name: string;
  owner_email: string;
  owner_phone: string;
  rent_amount: number;
  rental_hours: number;
  assigned_at: string;
  elapsed_hours: number;
  is_escalated: boolean;
}

export interface DriverKycData {
  user_id: string;
  full_name: string;
  email: string;
  phone: string;
  address?: string;
  driving_license_number?: string;
  driving_license_file_path?: string;
  aadhaar_number?: string;
  aadhaar_file_path?: string;
  pan_number?: string;
  pan_file_path?: string;
  profile_picture_path?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  verification_status: 'draft' | 'pending' | 'verified' | 'rejected' | string;
  verification_requested_at?: string;
  reviewed_at?: string;
  rejection_reason?: string;
}

export interface AdminDriverItem {
  user_id: string;
  email: string;
  phone?: string;
  role: string;
  is_active: boolean;
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
  verification_status: 'draft' | 'pending' | 'verified' | 'rejected' | string;
  rejection_reason?: string;
  reviewed_at?: string;
  created_at?: string;
}
