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
            const data = await api.getCars(filters)
            setCarList(data)
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
                        Показано {carList.length} из {carList.length} машин
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