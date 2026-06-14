import {React,useState} from 'react'
import { fetchStatus } from '../api/get/status'

export default function healthStatus() {
  const [status, setStatus] = useState(null)

  const handleFetchStatus = async () => {
    const data = await fetchStatus()
    setStatus(data)
  }

  return (
    <div className='container '>
      <h1 className='text-2xl font-bold mb-4'>Health Status</h1>
      <button
        className='bg-blue-500 text-white px-4 py-2 rounded'
        onClick={handleFetchStatus}
      >
        Fetch Status
      </button>
      {status && (
        <div className='mt-4'>
          <h2 className='text-xl font-semibold'>Current Status:</h2>
          <p>{JSON.stringify(status)}</p>
        </div>
      )}

        
    </div>
  )
}
