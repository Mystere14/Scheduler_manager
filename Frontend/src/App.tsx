import './App.css'
import { useState } from 'react'
import { WelcomePage } from './page/WelcomePage/WelcomePage'
import { SchedulerPage } from './page/SchedulerPage/SchedulerPage'
import { ValidatyPage } from './page/ValidatyPage/ValidationPage'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

function App() {
  const [currentPage, setCurrentPage] = useState<'welcome' | 'scheduler' | 'validation'>('welcome')

  const handleNavigateToScheduler = () => {
    setCurrentPage('scheduler')
  }

  const handleNavigateToValidaty = () => {
    setCurrentPage('validation')
  }

  return (    
  <BrowserRouter>
      <Routes>
        <Route path="/" element={<WelcomePage />} />
        <Route path="/scheduler" element={<SchedulerPage />} />
        <Route path="/validation" element={<ValidatyPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
