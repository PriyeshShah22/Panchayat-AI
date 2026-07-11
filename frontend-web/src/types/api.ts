export interface Role {
  id: number;
  name: string;
  description?: string | null;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  is_superuser: boolean;
  status: string;
  society_id: number | null;
  phone?: string | null;
  roles: Role[];
  created_at: string;
  last_login_at?: string | null;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface Bill {
  id: number;
  society_id: number;
  flat_id: number;
  resident_id: number | null;
  bill_number: string;
  title: string;
  description?: string | null;
  amount: number;
  late_fee: number;
  total_amount: number;
  paid_amount: number;
  status: string;
  issue_date: string;
  due_date: string;
  paid_at?: string | null;
  created_at: string;
}

export interface Complaint {
  id: number;
  title: string;
  description: string;
  society_id: number;
  flat_id?: number | null;
  reporter_id: number;
  assignee_id?: number | null;
  category_id?: number | null;
  status: string;
  priority: string;
  photo_url?: string | null;
  ai_suggested_category?: string | null;
  created_at: string;
  updated_at: string;
  resolved_at?: string | null;
}

export interface Visitor {
  id: number;
  society_id: number;
  flat_id: number;
  host_id: number;
  name: string;
  phone?: string | null;
  purpose?: string | null;
  status: string;
  vehicle_number?: string | null;
  qr_code?: string | null;
  created_at: string;
}

export interface Notice {
  id: number;
  society_id: number;
  author_id: number;
  title: string;
  body: string;
  is_pinned: boolean;
  audience: string;
  published_at: string;
  expires_at?: string | null;
}

export interface Society {
  id: number;
  name: string;
  address: string;
  city?: string | null;
  state?: string | null;
  pincode?: string | null;
  created_at: string;
}

export interface Flat {
  id: number;
  society_id: number;
  block_id: number;
  number: string;
  floor: number;
  area_sqft?: number | null;
  bedrooms: number;
  bathrooms: number;
}

export interface AdminStats {
  users_total: number;
  users_active: number;
  complaints_total: number;
  complaints_open: number;
  bills_overdue: number;
  outstanding_amount: number;
}
