export interface Car {
    id: string;
    brand: string;
    model: string;
    year: number;
    price: number;
    color: string;
    url: string;
    created_at: string;
    updated_at: string;
}

export interface FilterParams {
    brand?: string;
    model?: string;
    min_price?: number;
    max_price?: number;
    color?: string;
    min_year?: number;
    max_year?: number;
    sort_by?: 'price' | 'year' | 'created_at' | 'brand';
    sort_order?: 'asc' | 'desc';
    limit?: number;
    skip?: number;
}