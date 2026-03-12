import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Sheet, Table, Typography, Button, Chip,
  CircularProgress, Box, IconButton, Input,
  Select, Option, Stack, Avatar, Dropdown, Menu, MenuButton, MenuItem
} from '@mui/joy'
import { RefreshRounded, OpenInNewRounded, LogoutRounded, PersonRounded } from '@mui/icons-material'
import { api } from '../api/client'
import { Car, FilterParams } from '../types'

export default function Cars() {
  const navigate = useNavigate()
  const [carList, setCarList] = useState<Car[]>([])
  const [loading, setLoading] = useState(true)
  const [user, setUser] = useState<any>(null)
  const [filters, setFilters] = useState<FilterParams>({
    limit: 10,
    sort_by: 'created_at',
    sort_order: 'desc'
  })

  useEffect(() => {
    loadCars()
  }, [])

  const loadCars = async () => {
    setLoading(true)
    try {
      //const data = await api.getList(filters)
      //setCarList(data)
    } catch (error) {
      console.error('Failed to load cars:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user) loadCars()
  }, [filters])

  const handleLogout = async () => {
    //await api.logout()
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'JPY',
      minimumFractionDigits: 0
    }).format(price)
  }

  if (!user) return null

  return (
    <Sheet sx={{ minHeight: '100vh' }}>
      <Sheet variant="solid" color="primary" sx={{ px: 3, py: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography level="h4" textColor="white">
          Cервис автообъявлений
        </Typography>

        <Dropdown>
          <MenuButton slots={{ root: IconButton }} sx={{ color: 'white' }}>
            <Avatar size="sm"><PersonRounded /></Avatar>
          </MenuButton>
          <Menu>
            <MenuItem>
              <Typography level="body-sm">{user.email}</Typography>
            </MenuItem>
            <MenuItem onClick={handleLogout}>
              <LogoutRounded /> Выйти
            </MenuItem>
          </Menu>
        </Dropdown>
      </Sheet>

      <Box sx={{ p: 3 }}>
        <Stack direction="row" spacing={2} sx={{ mb: 3, flexWrap: 'wrap', gap: 1 }}>
          <Input
            placeholder="Бренд"
            value={filters.brand || ''}
            onChange={(e) => setFilters(f => ({ ...f, brand: e.target.value }))}
            sx={{ width: 150 }}
          />
          <Input
            placeholder="Модель"
            value={filters.model || ''}
            onChange={(e) => setFilters(f => ({ ...f, model: e.target.value }))}
            sx={{ width: 150 }}
          />
          <Input
            placeholder="Мин. стоимость"
            type="number"
            value={filters.min_price || ''}
            onChange={(e) => setFilters(f => ({ ...f, min_price: Number(e.target.value) || undefined }))}
            sx={{ width: 120 }}
          />
          <Input
            placeholder="Макс. стоимость"
            type="number"
            value={filters.max_price || ''}
            onChange={(e) => setFilters(f => ({ ...f, max_price: Number(e.target.value) || undefined }))}
            sx={{ width: 120 }}
          />
          <Select
            value={filters.sort_by}
            onChange={(_, v) => setFilters(f => ({ ...f, sort_by: v || 'created_at' }))}
            sx={{ width: 120 }}
          >
            <Option value="created_at">Дата</Option>
            <Option value="price">Стоимость</Option>
            <Option value="year">Год</Option>
          </Select>
          <Button
            onClick={loadCars}
            loading={loading}
            startDecorator={<RefreshRounded />}
          >
            Refresh
          </Button>
        </Stack>

        <Sheet variant="outlined" sx={{ borderRadius: 'md', overflow: 'auto' }}>
          <Table hoverRow>
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
                  </td>
                </tr>
              ) : carList.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', padding: '40px' }}>
                    <Typography>No cars found</Typography>
                  </td>
                </tr>
              ) : (
                carList.map((car) => (
                  <tr key={car.id}>
                    <td><Chip size="sm" variant="soft" color="primary">{car.brand}</Chip></td>
                    <td>{car.model}</td>
                    <td>{car.year}</td>
                    <td><Typography fontWeight="bold" color="primary">{formatPrice(car.price)}</Typography></td>
                    <td><Chip size="sm" variant="outlined">{car.color}</Chip></td>
                    <td>
                      <IconButton size="sm" component="a" href={car.url} target="_blank">
                        <OpenInNewRounded />
                      </IconButton>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </Table>
        </Sheet>

        <Typography level="body-sm" sx={{ mt: 2, color: 'text.secondary' }}>
          Показано {carList.length} машин
        </Typography>
      </Box>
    </Sheet>
  )
}