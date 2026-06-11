import './App.css'
import { useState } from 'react'
import { ValidationPage } from './page/ValidationPage/ValidationPage'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

function App() {
  const [currentPage, setCurrentPage] = useState<'welcome' | 'validation'>('welcome')

  const handleNavigateToValidation = () => {
    setCurrentPage('validation')
  }

  return (    
  <BrowserRouter>
      <Routes>
        <Route path="/validation" element={<ValidationPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
