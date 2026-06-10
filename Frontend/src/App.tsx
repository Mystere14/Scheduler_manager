import './App.css'
import { useState } from 'react'
import { ValidatyPage } from './page/ValidatyPage/ValidationPage'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

function App() {
  const [currentPage, setCurrentPage] = useState<'welcome' | 'validation'>('welcome')

  const handleNavigateToValidaty = () => {
    setCurrentPage('validation')
  }

  return (    
  <BrowserRouter>
      <Routes>
        <Route path="/validation" element={<ValidatyPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
