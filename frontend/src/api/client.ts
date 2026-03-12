import axios from "axios";
import type { AxiosInstance, InternalAxiosRequestConfig } from "axios";
import type { Car, FilterParams } from "../types/car";
import type { LoginRequest, LoginResponse } from "../types/user";

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: '/api',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
      },
      timeout: 10000,
      withCredentials: true,
    })

    this.client.interceptors.response.use((response) => response, (error) => {
        if (error.response?.status === 401 && !window.location.pathname.includes('/login')) {
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await this.client.post<LoginResponse>('/login', data)
    return response.data
  }

  async getCars(params: FilterParams = {}): Promise<Car[]> {
    const queryParams = new URLSearchParams()

    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, String(value))
      }
    })

    const response = await this.client.get<Car[]>(`/cars?${queryParams.toString()}`)
    return response.data
  }

}

export const api = new ApiClient()