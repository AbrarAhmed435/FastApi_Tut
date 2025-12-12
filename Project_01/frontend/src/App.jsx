import { useState } from 'react'
import './App.css'
import ClerkProviderWithRoutes from './Auth/ClerkProviderWithRoutes'
import { Routes,Route } from 'react-router-dom'
import { Layout } from './layout/Layout'
import { ChallengeGenerator} from './challenge/ChallengeGenerator'
import { HistoryPanel } from './history/HistoryPanel'
import { AuthenticationPage } from './Auth/AuthenticationPage'


function App() {
  const [count, setCount] = useState(0)

  return (
    <ClerkProviderWithRoutes>
      <Routes>
        <Route path='/sign-in/*' element={<AuthenticationPage/>} />
        <Route path='/sign-up' element={<AuthenticationPage/>} />
        <Route element={<Layout/>} >
         <Route path='/' element={<ChallengeGenerator/>}/>
         <Route path='/history' element={<HistoryPanel/>}/>
        </Route>
      </Routes>
    </ClerkProviderWithRoutes>
  )
}

export default App
