import './App.css'
import { useState } from 'react'
import { WelcomePage } from './page/WelcomePage/WelcomePage'
import { SchedulerPage } from './page/SchedulerPage/SchedulerPage'
import { ValidatyPage } from './page/ValidatyPage/ValidatyPage'

function App() {
  const [currentPage, setCurrentPage] = useState<'welcome' | 'scheduler' | 'validaty'>('welcome')

  const handleNavigateToScheduler = () => {
    setCurrentPage('scheduler')
  }

  const handleNavigateToValidaty = () => {
    setCurrentPage('validaty')
  }

  return (
    <>
      {currentPage === 'welcome' && (
        <WelcomePage 
          onNavigateToScheduler={handleNavigateToScheduler}
          onNavigateToValidaty={handleNavigateToValidaty}
        />
      )}
      {currentPage === 'scheduler' && (
        <SchedulerPage />
      )}
      {currentPage === 'validaty' && (
        <ValidatyPage />
      )}
    </>
  )
}

export default App
