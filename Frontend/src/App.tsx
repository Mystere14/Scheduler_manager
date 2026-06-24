import './App.css'
import { useState } from 'react'
import { SchedulerList } from './page/SchedulerList/SchedulerList'
import { ValidationPage } from './page/ValidationPage/ValidationPage'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

function App() {
  const [currentPage, setCurrentPage] = useState<'validation'>('validation')
  const [schedulerList, setSchedulerList] = useState<any[]>([])

  const handleNavigateToValidation = () => {
    setCurrentPage('validation')
  }

  return (    
  <BrowserRouter>
      <Routes>
        <Route path="/validation" element={<ValidationPage schedulerList={schedulerList} setSchedulerList={setSchedulerList} />} />
        <Route path="/session/:code_sae" element={<SchedulerList schedulerList={schedulerList}  />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
