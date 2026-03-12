export interface Car {
  id: string
  brand: string
  model: string
  year: number
  price: number
  color: string
  url: string
  created_at: string
}

export interface FilterParams {
  brand?: string
  model?: string
  min_price?: number
  max_price?: number
  color?: string
  limit?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}