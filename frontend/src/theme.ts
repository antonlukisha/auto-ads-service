import { extendTheme } from '@mui/joy/styles';

const theme = extendTheme({
    colorSchemes: {
        light: {
            palette: {
                primary: {
                    50: '#f0f9ff',
                    100: '#e0f2fe',
                    200: '#bae6fd',
                    300: '#7dd3fc',
                    400: '#38bdf8',
                    500: '#0ea5e9',
                    600: '#0284c7',
                    700: '#0369a1',
                    800: '#075985',
                    900: '#0c4a6e',
                },
                danger: {
                    500: '#e11d48',
                },
                success: {
                    500: '#10b981',
                },
                warning: {
                    500: '#f59e0b',
                },
                background: {
                    body: '#f5f5f5',
                    level1: '#fff',
                    level2: '#f5f5f5',
                    level3: '#eee',
                },
                text: {
                    primary: '#1e293b',
                    secondary: '#64748b',
                },
            },
        },
        dark: {
            palette: {
                primary: {
                    500: '#60a5fa',
                    600: '#3b82f6',
                },
                background: {
                    body: '#0f172a',
                    level1: '#1e293b',
                    level2: '#334155',
                },
                text: {
                    primary: '#f1f5f9',
                    secondary: '#cbd5e1',
                },
            },
        },
    },
    fontFamily: {
        body: 'Roboto, system-ui, sans-serif',
        display: 'Roboto, system-ui, sans-serif',
    },
    radius: {
        xs: '4px',
        sm: '6px',
        md: '8px',
        lg: '12px',
        xl: '16px',
    },
});

export default theme;