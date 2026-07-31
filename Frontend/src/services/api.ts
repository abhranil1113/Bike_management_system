import axios from 'axios';
import type { Bike } from '../types';

const API_BASE_URL = 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const MOCK_BIKES: Bike[] = [
  {
    id: 'bike-101',
    owner_user_id: 'owner-1',
    bike_name: 'Yamaha FZ 25',
    brand: 'Yamaha',
    model: 'FZ 25',
    registration_number: 'WB02AF9812',
    color: 'Matte Blue',
    fuel_type: 'petrol',
    ownership_type: 'self',
    status: 'available',
    verification_status: 'verified',
    is_active: true,
    city: 'Kolkata',
    pricing: {
      daily_rent: 600,
      weekly_rent: 3600,
      monthly_rent: 14000,
      security_deposit: 1500,
      late_fee_per_day: 150,
    },
    image_urls: ['https://images.unsplash.com/photo-1558981806-ec527fa84c39?auto=format&fit=crop&w=800&q=80'],
    created_at: new Date().toISOString(),
  },
  {
    id: 'bike-102',
    owner_user_id: 'owner-1',
    bike_name: 'Royal Enfield Classic 350',
    brand: 'Royal Enfield',
    model: 'Classic 350',
    registration_number: 'WB04CD4512',
    color: 'Chrome Black',
    fuel_type: 'petrol',
    ownership_type: 'self',
    status: 'available',
    verification_status: 'verified',
    is_active: true,
    city: 'Kolkata',
    pricing: {
      daily_rent: 900,
      weekly_rent: 5500,
      monthly_rent: 20000,
      security_deposit: 2500,
      late_fee_per_day: 200,
    },
    image_urls: ['https://images.unsplash.com/photo-1568772585407-9361f9bf3a87?auto=format&fit=crop&w=800&q=80'],
    created_at: new Date().toISOString(),
  },
  {
    id: 'bike-103',
    owner_user_id: 'owner-2',
    bike_name: 'Ather 450X Gen 3',
    brand: 'Ather',
    model: '450X',
    registration_number: 'WB01EV1001',
    color: 'Cosmic Black',
    fuel_type: 'electric',
    ownership_type: 'self',
    status: 'available',
    verification_status: 'verified',
    is_active: true,
    city: 'Kolkata',
    pricing: {
      daily_rent: 500,
      weekly_rent: 3000,
      monthly_rent: 11000,
      security_deposit: 1200,
      late_fee_per_day: 100,
    },
    image_urls: ['https://images.unsplash.com/photo-1609630875171-b1321377ee65?auto=format&fit=crop&w=800&q=80'],
    created_at: new Date().toISOString(),
  },
  {
    id: 'bike-104',
    owner_user_id: 'owner-2',
    bike_name: 'KTM Duke 390',
    brand: 'KTM',
    model: 'Duke 390',
    registration_number: 'WB06EX8899',
    color: 'Orange',
    fuel_type: 'petrol',
    ownership_type: 'self',
    status: 'assigned',
    verification_status: 'verified',
    is_active: true,
    city: 'Kolkata',
    pricing: {
      daily_rent: 1200,
      weekly_rent: 7500,
      monthly_rent: 28000,
      security_deposit: 3500,
      late_fee_per_day: 300,
    },
    image_urls: ['https://images.unsplash.com/photo-1558981403-c5f9899a28bc?auto=format&fit=crop&w=800&q=80'],
    created_at: new Date().toISOString(),
  }
];
