import './App.css'
import { useState } from 'react'
import { WelcomePage } from './page/WelcomePage/WelcomePage'
import { SchedulerPage } from './page/SchedulerPage/SchedulerPage'

function App() {
  const [currentPage, setCurrentPage] = useState<'welcome' | 'scheduler'>('welcome')

  const handleNavigateToScheduler = () => {
    setCurrentPage('scheduler')
  }

  return (
    <>
      {currentPage === 'welcome' && (
        <WelcomePage onNavigateToScheduler={handleNavigateToScheduler} />
      )}
      {currentPage === 'scheduler' && (
        <SchedulerPage />
      )}
    </>
  )
}

export default App
