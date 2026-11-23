import './App.css'
import { useBriefingCall } from './useBriefingCall'

const STATUS_TEXT = {
  idle: '',
  connecting: 'Connecting...',
  waiting: 'Connected. Waiting for the agent...',
  live: 'Agent joined',
  error: '',
}

function App() {
  const call = useBriefingCall()
  const inCall =
    call.status === 'connecting' || call.status === 'waiting' || call.status === 'live'

  return (
    <main>
      <h1>En route briefing</h1>

      {inCall ? (
        <button type="button" className="danger" onClick={call.end}>
          End briefing
        </button>
      ) : (
        <button type="button" className="primary" onClick={call.launch}>
          Launch agent
        </button>
      )}

      <p role="status">{STATUS_TEXT[call.status]}</p>
      {call.status === 'error' && (
        <p className="error">Briefing failed: {call.error}</p>
      )}
    </main>
  )
}

export default App
