import './App.css'
import { useContext, useEffect, useState } from 'react'
import { SchedulerList } from './page/SchedulerList/SchedulerList'
import { ValidationPage } from './page/ValidationPage/ValidationPage'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import api from './service/Api'
import { ValidationContext, type Session } from './service/Context'

function App() {
  const context = useContext(ValidationContext);


  return (    
      <BrowserRouter>
        <Routes>
            <Route path="/validation" element={<ValidationPage/>} />
            <Route path="/session/:codeSae" element={<SchedulerList/>} />
        </Routes>
      </BrowserRouter>
  )
}

export default App
