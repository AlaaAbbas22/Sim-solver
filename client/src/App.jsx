import React, { useState } from 'react'
import Six from './6'

function App() {
  // I was intending to do a flexible game for dynamic number of dots but it is very time consuming
  const [type, setType] = useState(6)
  
  return (
    <>
      <div className='w-[100vw]'>
        {type == 6&&<Six/>}   
      </div>
    </>
  )
}

export default App
