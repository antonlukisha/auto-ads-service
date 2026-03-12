import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Box, Card, Input, Button, Typography, Alert, Stack } from '@mui/joy'
import { api } from '../api/client'

export default function Login() {
    const navigate = useNavigate()
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')
        setLoading(true)

        try {
            // await client.login(username, password)
            navigate('/')
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Ошибка авторизации')
        } finally {
            setLoading(false)
        }
    }

    return (
        <Box sx={{
            minHeight: '100vh',
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            bgcolor: 'background.level1'
        }}>
            <Card sx={{ maxWidth: 400, width: '100%', p: 4 }}>
                <Typography level="h3" sx={{ mb: 3, textAlign: 'center' }}>
                    Объявления <Box component="span" sx={{ fontWeight: 'bold', color: 'primary.500' }}>carsensor.net</Box>
                </Typography>

                {error && <Alert color="danger" sx={{ mb: 2 }}>{error}</Alert>}

                <form onSubmit={handleSubmit}>
                    <Stack spacing={2}>
                        <Input
                            type="username"
                            placeholder="Логин"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                            size="lg"
                        />
                        <Input
                            type="password"
                            placeholder="Пароль"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            size="lg"
                        />
                        <Button type="submit" loading={loading} size="lg">
                            Войти
                        </Button>
                    </Stack>
                </form>

                <Typography level="body-xs" sx={{ mt: 2, textAlign: 'center', color: 'text.secondary' }}>
                    Demo: admin / admin_pass
                </Typography>
            </Card>
        </Box>
    )
}