import { StrictMode, useContext, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { ValidationContext, type Session, type ImportedData } from './service/Context.tsx'
import { ValidationProvider } from './service/ValidationProvider.tsx'

// Set API endpoint for desktop app
const isDevelopment = import.meta.env.DEV;
(window as any).__APIURL__ = isDevelopment ? 'http://localhost:8000' : 'http://localhost:8000';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ValidationProvider>
      <App />
    </ValidationProvider>
  </StrictMode>,
)
