import axios from "axios";
import type { AxiosInstance } from "axios";
import type { Car, FilterParams } from "../types/car";
import type { LoginRequest, LoginResponse } from "../types/user";

class ApiClient {
    private client: AxiosInstance
    private accessToken: string | null = null

    constructor() {
        this.client = axios.create({
            baseURL: 'http://localhost:4444/api',
            headers: {
                'Content-Type': 'application/json',
            },
            timeout: 10000,
            withCredentials: true,
        })

        this.client.interceptors.request.use((config) => {
            if (this.accessToken) {
                config.headers.Authorization = `Bearer ${this.accessToken}`
            }
            return config
        })

        this.client.interceptors.response.use(
            (response) => response,
            (error) => {
                if (error.response?.status === 401 && !window.location.pathname.includes('/login')) {
                    this.accessToken = null
                    window.location.href = '/login'
                }
                return Promise.reject(error)
            }
        )
    }

    async login(data: LoginRequest): Promise<LoginResponse> {
        const response = await this.client.post<LoginResponse>('/login', data)
        this.accessToken = response.data.access_token
        return response.data
    }

    async getCars(params: FilterParams = {}): Promise<Car[]> {
        const queryParams = new URLSearchParams()
        Object.entries(params).forEach(([key, value]) => {
            if (value !== undefined && value !== null && value !== '') {
                queryParams.append(key, String(value))
            }
        })
        const response = await this.client.get<Car[]>(`/cars/?${queryParams.toString()}`)
        return response.data
    }
}

export const api = new ApiClient()