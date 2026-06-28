import { StrictMode, useContext, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { ValidationContext, type Session, type ImportedData } from './services/context'
import { ValidationProvider } from './services/validationProvider.tsx'

// Set API endpoint for desktop app
const isDevelopment = import.meta.env.DEV;
(window as any).__API_URL__ = isDevelopment ? 'http://localhost:8000' : 'http://localhost:8000';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ValidationProvider>
      <App />
    </ValidationProvider>
  </StrictMode>,
)
