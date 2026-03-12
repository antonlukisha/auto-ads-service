import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { CssVarsProvider } from '@mui/joy/styles'
import { CssBaseline } from '@mui/joy'
import Login from './pages/Login'
import Cars from './pages/Cars'

export default function App() {
  return (
    <CssVarsProvider>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Cars />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </CssVarsProvider>
  )
}