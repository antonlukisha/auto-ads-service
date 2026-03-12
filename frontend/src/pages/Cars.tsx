import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
    Sheet, Table, Typography, Button, Chip,
    CircularProgress, Box, IconButton, Input,
    Select, Option, Stack, Avatar, Dropdown, Menu, MenuButton, MenuItem
} from '@mui/joy'
import { RefreshRounded, OpenInNewRounded, LogoutRounded, PersonRounded } from '@mui/icons-material'
import { api } from '../api/client'
import type { Car, FilterParams } from "../types/car";

const MOCK_CARS: Car[] = [
    {
        id: '1',
        brand: 'Toyota',
        model: 'Camry',
        year: 2022,
        price: 3500000,
        color: 'Black',
        url: 'https://example.com/camry',
        created_at: '2024-01-15T10:30:00Z',
        updated_at: '2024-01-15T10:30:00Z'
    },
    {
        id: '2',
        brand: 'Honda',
        model: 'Accord',
        year: 2023,
        price: 3800000,
        color: 'White',
        url: 'https://example.com/accord',
        created_at: '2024-01-14T15:45:00Z',
        updated_at: '2024-01-14T15:45:00Z'
    },
    {
        id: '3',
        brand: 'Nissan',
        model: 'X-Trail',
        year: 2023,
        price: 4200000,
        color: 'Silver',
        url: 'https://example.com/xtrail',
        created_at: '2024-01-13T09:20:00Z',
        updated_at: '2024-01-13T09:20:00Z'
    },
    {
        id: '4',
        brand: 'Mazda',
        model: 'CX-5',
        year: 2022,
        price: 3100000,
        color: 'Red',
        url: 'https://example.com/cx5',
        created_at: '2024-01-12T14:10:00Z',
        updated_at: '2024-01-12T14:10:00Z'
    },
    {
        id: '5',
        brand: 'Subaru',
        model: 'Outback',
        year: 2023,
        price: 4000000,
        color: 'Blue',
        url: 'https://example.com/outback',
        created_at: '2024-01-11T11:55:00Z',
        updated_at: '2024-01-11T11:55:00Z'
    },
    {
        id: '6',
        brand: 'Mitsubishi',
        model: 'Outlander',
        year: 2022,
        price: 3300000,
        color: 'Gray',
        url: 'https://example.com/outlander',
        created_at: '2024-01-10T16:30:00Z',
        updated_at: '2024-01-10T16:30:00Z'
    },
    {
        id: '7',
        brand: 'Suzuki',
        model: 'Vitara',
        year: 2023,
        price: 2800000,
        color: 'Green',
        url: 'https://example.com/vitara',
        created_at: '2024-01-09T13:25:00Z',
        updated_at: '2024-01-09T13:25:00Z'
    },
    {
        id: '8',
        brand: 'Lexus',
        model: 'RX',
        year: 2024,
        price: 7500000,
        color: 'Black',
        url: 'https://example.com/rx',
        created_at: '2024-01-08T12:15:00Z',
        updated_at: '2024-01-08T12:15:00Z'
    },
    {
        id: '9',
        brand: 'Toyota',
        model: 'RAV4',
        year: 2023,
        price: 3900000,
        color: 'белый',
        url: 'https://example.com/rav4',
        created_at: '2024-01-07T10:45:00Z',
        updated_at: '2024-01-07T10:45:00Z'
    },
    {
        id: '10',
        brand: 'Honda',
        model: 'CR-V',
        year: 2023,
        price: 4100000,
        color: 'Silver',
        url: 'https://example.com/crv',
        created_at: '2024-01-06T09:30:00Z',
        updated_at: '2024-01-06T09:30:00Z'
    }
];

export default function Cars() {
    const navigate = useNavigate()
    const [carList, setCarList] = useState<Car[]>([])
    const [loading, setLoading] = useState(true)
    const [user, setUser] = useState<any>({ email: 'demo@example.com' })
    const [filters, setFilters] = useState<FilterParams>({
        limit: 10,
        sort_by: 'created_at',
        sort_order: 'desc'
    })

    const loadCars = async () => {
        setLoading(true)
        try {
            await new Promise(resolve => setTimeout(resolve, 800))

            let filtered = [...MOCK_CARS]

            if (filters.brand) {
                filtered = filtered.filter(car =>
                    car.brand.toLowerCase().includes(filters.brand!.toLowerCase())
                )
            }

            if (filters.model) {
                filtered = filtered.filter(car =>
                    car.model.toLowerCase().includes(filters.model!.toLowerCase())
                )
            }

            if (filters.min_price) {
                filtered = filtered.filter(car => car.price >= filters.min_price!)
            }

            if (filters.max_price) {
                filtered = filtered.filter(car => car.price <= filters.max_price!)
            }

            if (filters.min_year) {
                filtered = filtered.filter(car => car.year >= filters.min_year!)
            }

            if (filters.max_year) {
                filtered = filtered.filter(car => car.year <= filters.max_year!)
            }

            if (filters.color) {
                filtered = filtered.filter(car =>
                    car.color.toLowerCase().includes(filters.color!.toLowerCase())
                )
            }

            filtered.sort((a, b) => {
                const field = filters.sort_by || 'created_at'
                const order = filters.sort_order === 'asc' ? 1 : -1

                if (field === 'price') {
                    return (a.price - b.price) * order
                } else if (field === 'year') {
                    return (a.year - b.year) * order
                } else {
                    return (new Date(b.created_at).getTime() - new Date(a.created_at).getTime()) * order
                }
            })

            if (filters.limit) {
                filtered = filtered.slice(0, filters.limit)
            }

            setCarList(filtered)
        } catch (error) {
            console.error('Failed to load cars:', error)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        loadCars()
    }, [])

    useEffect(() => {
        if (user) loadCars()
    }, [filters])

    const handleLogout = async () => {
        setUser(null)
        navigate('/login')
    }

    const formatPrice = (price: number) => {
        return new Intl.NumberFormat('ru-RU', {
            style: 'currency',
            currency: 'RUB',
            minimumFractionDigits: 0
        }).format(price)
    }

    if (!user) return null

    return (
        <Sheet sx={{ minHeight: '100vh', bgcolor: 'background.body' }}>
            <Sheet
                variant="solid"
                color="primary"
                sx={{
                    px: 3,
                    py: 2,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                }}
            >
                <Typography level="h4" sx={{ color: 'white' }}>
                    Объявления <Box component="span" sx={{ fontWeight: 'bold', color: 'white', opacity: 0.9 }}>carsensor.net</Box>
                </Typography>

                <IconButton
                    onClick={handleLogout}
                    sx={{
                        color: 'white'
                    }}
                >
                    <LogoutRounded
                        sx={{
                            color: 'white',
                            '&:hover': {
                                color: 'black'
                            }
                        }}
                    />
                </IconButton>
            </Sheet>

            <Box sx={{ p: 3 }}>
                <Stack direction="row" spacing={2} sx={{ mb: 3, flexWrap: 'wrap', gap: 1 }}>
                    <Input
                        placeholder="Бренд"
                        value={filters.brand || ''}
                        onChange={(e) => setFilters(f => ({ ...f, brand: e.target.value }))}
                        sx={{ width: 150 }}
                        size="sm"
                    />
                    <Input
                        placeholder="Модель"
                        value={filters.model || ''}
                        onChange={(e) => setFilters(f => ({ ...f, model: e.target.value }))}
                        sx={{ width: 150 }}
                        size="sm"
                    />
                    <Input
                        placeholder="Мин. стоимость"
                        type="number"
                        value={filters.min_price || ''}
                        onChange={(e) => setFilters(f => ({ ...f, min_price: e.target.value ? Number(e.target.value) : undefined }))}
                        sx={{ width: 140 }}
                        size="sm"
                    />
                    <Input
                        placeholder="Макс. стоимость"
                        type="number"
                        value={filters.max_price || ''}
                        onChange={(e) => setFilters(f => ({ ...f, max_price: e.target.value ? Number(e.target.value) : undefined }))}
                        sx={{ width: 140 }}
                        size="sm"
                    />
                    <Select
                        value={filters.sort_by || 'created_at'}
                        onChange={(_, v) => setFilters(f => ({ ...f, sort_by: v as string || 'created_at' }))}
                        sx={{ width: 120 }}
                        size="sm"
                    >
                        <Option value="created_at">По дате</Option>
                        <Option value="price">По цене</Option>
                        <Option value="year">По году</Option>
                    </Select>
                    <Button
                        onClick={loadCars}
                        startDecorator={<RefreshRounded />}
                        size="sm"
                        variant="soft"
                    >
                        Обновить
                    </Button>
                </Stack>

                <Sheet variant="outlined" sx={{ borderRadius: 'md', overflow: 'auto' }}>
                    <Table hoverRow sx={{ '& thead th': { fontWeight: 'bold', bgcolor: 'background.level1' } }}>
                        <thead>
                            <tr>
                                <th>Бренд</th>
                                <th>Модель</th>
                                <th>Год</th>
                                <th>Стоимость</th>
                                <th>Цвет</th>
                                <th>Ссылка</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr>
                                    <td colSpan={6} style={{ textAlign: 'center', padding: '40px' }}>
                                        <CircularProgress />
                                        <Typography level="body-sm" sx={{ mt: 2 }}>Загрузка...</Typography>
                                    </td>
                                </tr>
                            ) : carList.length === 0 ? (
                                <tr>
                                    <td colSpan={6} style={{ textAlign: 'center', padding: '40px' }}>
                                        <Typography level="body-lg">Нет данных</Typography>
                                        <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
                                            Попробуйте изменить параметры фильтрации
                                        </Typography>
                                    </td>
                                </tr>
                            ) : (
                                carList.map((car) => (
                                    <tr key={car.id}>
                                        <td>
                                            <Box component="span" sx={{ fontWeight: 'bold', color: 'primary.500'}}>
                                                {car.brand}
                                            </Box>
                                        </td>
                                        <td>{car.model}</td>
                                        <td>
                                            <Chip size="sm" variant="outlined" sx={{ fontWeight: 'bold'}} color="neutral">
                                                {car.year}
                                            </Chip>
                                        </td>
                                        <td>
                                            <Typography fontWeight="bold" color="primary">
                                                {formatPrice(car.price)}
                                            </Typography>
                                        </td>
                                        <td>
                                            {car.color}
                                        </td>
                                        <td>
                                            <IconButton
                                                size="sm"
                                                component="a"
                                                href={car.url}
                                                target="_blank"
                                                variant="plain"
                                                color="primary"
                                            >
                                                <OpenInNewRounded />
                                            </IconButton>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </Table>
                </Sheet>

                <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mt: 2 }}>
                    <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
                        Показано {carList.length} из {MOCK_CARS.length} машин
                    </Typography>
                    <Select
                        value={filters.limit || 10}
                        onChange={(_, v) => setFilters(f => ({ ...f, limit: v as number || 10 }))}
                        size="sm"
                        sx={{ width: 100 }}
                    >
                        <Option value={5}>5</Option>
                        <Option value={10}>10</Option>
                        <Option value={20}>20</Option>
                        <Option value={50}>50</Option>
                    </Select>
                </Stack>
            </Box>
        </Sheet>
    )
}