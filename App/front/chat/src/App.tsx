import { useState } from 'react'
import  SimpleChat  from './components/Chat'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <SimpleChat />
    </>
  )
}

export default App
