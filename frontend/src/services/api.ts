import axios from 'axios';
import type { 
  Order, 
  Product, 
  Category, 
  DashboardStats, 
  User,
  DeliveryZone 
} from '../types';

const api = axios.create({
  baseURL: '/api/v1',
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: (email: string, password: string) =>
    api.post<{ access_token: string }>('/auth/login', { email, password }),
  
  getMe: () => api.get<User>('/auth/me'),
};

export const ordersApi = {
  getAll: (params?: { status?: string; page?: number; limit?: number }) =>
    api.get<{ items: Order[]; total: number }>('/orders', { params }),
  
  getById: (id: number) => api.get<Order>(`/orders/${id}`),
  
  updateStatus: (id: number, status: Order['status']) =>
    api.patch<Order>(`/orders/${id}/status`, { status }),
  
  assignCourier: (orderId: number, courierId: number) =>
    api.patch<Order>(`/orders/${orderId}/assign-courier`, { courier_id: courierId }),
};

export const productsApi = {
  getAll: (params?: { category_id?: number; is_available?: boolean }) =>
    api.get<Product[]>('/products', { params }),
  
  getById: (id: number) => api.get<Product>(`/products/${id}`),
  
  create: (data: Partial<Product>) => api.post<Product>('/products', data),
  
  update: (id: number, data: Partial<Product>) =>
    api.patch<Product>(`/products/${id}`, data),
  
  delete: (id: number) => api.delete(`/products/${id}`),
};

export const categoriesApi = {
  getAll: () => api.get<Category[]>('/categories'),
  
  getById: (id: number) => api.get<Category>(`/categories/${id}`),
  
  create: (data: Partial<Category>) => api.post<Category>('/categories', data),
  
  update: (id: number, data: Partial<Category>) =>
    api.patch<Category>(`/categories/${id}`, data),
  
  delete: (id: number) => api.delete(`/categories/${id}`),
};

export const usersApi = {
  getAll: () => api.get<User[]>('/users'),
  
  getById: (id: number) => api.get<User>(`/users/${id}`),
  
  create: (data: Partial<User> & { password: string }) =>
    api.post<User>('/users', data),
  
  update: (id: number, data: Partial<User>) =>
    api.patch<User>(`/users/${id}`, data),
  
  delete: (id: number) => api.delete(`/users/${id}`),
};

export const dashboardApi = {
  getStats: () => api.get<DashboardStats>('/dashboard/stats'),
};

export const deliveryZonesApi = {
  getAll: () => api.get<DeliveryZone[]>('/delivery-zones'),
  
  create: (data: Partial<DeliveryZone>) =>
    api.post<DeliveryZone>('/delivery-zones', data),
  
  update: (id: number, data: Partial<DeliveryZone>) =>
    api.patch<DeliveryZone>(`/delivery-zones/${id}`, data),
  
  delete: (id: number) => api.delete(`/delivery-zones/${id}`),
};
