export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  created_at: string;
}

export type UserRole = 'admin' | 'operator' | 'courier';

export interface Category {
  id: number;
  name: string;
  description?: string;
  image_url?: string;
  sort_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Product {
  id: number;
  category_id: number;
  name: string;
  description?: string;
  price: number;
  image_url?: string;
  is_available: boolean;
  preparation_time_minutes: number;
  created_at: string;
  updated_at: string;
  category?: Category;
}

export interface ProductOption {
  id: number;
  product_id: number;
  name: string;
  price_modifier: number;
  is_required: boolean;
}

export interface OrderItem {
  id: number;
  order_id: number;
  product_id: number;
  quantity: number;
  unit_price: number;
  options?: OrderItemOption[];
  product?: Product;
}

export interface OrderItemOption {
  id: number;
  order_item_id: number;
  option_name: string;
  price_modifier: number;
}

export type OrderStatus = 
  | 'pending'
  | 'confirmed'
  | 'preparing'
  | 'ready'
  | 'on_delivery'
  | 'delivered'
  | 'cancelled';

export type DeliveryType = 'pickup' | 'delivery';

export interface Order {
  id: number;
  user_id: number;
  status: OrderStatus;
  delivery_type: DeliveryType;
  total_amount: number;
  items: OrderItem[];
  
  // Delivery info
  delivery_address?: string;
  delivery_latitude?: number;
  delivery_longitude?: number;
  delivery_phone?: string;
  
  // Pickup info
  pickup_time?: string;
  
  // Customer info (for guest orders)
  customer_name?: string;
  customer_phone?: string;
  customer_telegram_id?: number;
  
  notes?: string;
  paid: boolean;
  payment_method?: 'card' | 'cash';
  
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export interface DeliveryZone {
  id: number;
  name: string;
  polygon_coordinates: [number, number][]; // [[lat, lng], ...]
  delivery_fee: number;
  min_order_amount: number;
  is_active: boolean;
}

export interface DashboardStats {
  total_orders_today: number;
  total_revenue_today: number;
  pending_orders: number;
  active_deliveries: number;
  popular_products: Array<{
    product_id: number;
    product_name: string;
    orders_count: number;
  }>;
}
