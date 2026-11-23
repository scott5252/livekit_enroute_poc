import { useCallback, useEffect, useRef, useState } from 'react'
import { Room, RoomEvent, Track } from 'livekit-client'

export type CallStatus = 'idle' | 'connecting' | 'waiting' | 'live' | 'error'

interface SessionResponse {
  server_url: string
  participant_token: string
}

// Ask the server to start a briefing. The server chooses the mock visit.
async function createSession(): Promise<SessionResponse> {
  const res = await fetch('/api/briefing-session', { method: 'POST' })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.error ?? `Server returned ${res.status}`)
  }
  return res.json()
}

export function useBriefingCall() {
  const roomRef = useRef<Room | null>(null)
  const [status, setStatus] = useState<CallStatus>('idle')
  const [error, setError] = useState<string | null>(null)

  const launch = useCallback(async () => {
    if (roomRef.current) return // one briefing at a time

    const room = new Room()
    roomRef.current = room
    setError(null)
    setStatus('connecting')

    // Play the agent's voice when its audio track arrives.
    room.on(RoomEvent.TrackSubscribed, (track) => {
      if (track.kind === Track.Kind.Audio) {
        document.body.appendChild(track.attach())
      }
    })
    room.on(RoomEvent.TrackUnsubscribed, (track) => {
      track.detach().forEach((el) => el.remove())
    })
    room.on(RoomEvent.ParticipantConnected, () => setStatus('live'))
    room.on(RoomEvent.Disconnected, () => {
      roomRef.current = null
      setStatus((current) => (current === 'error' ? current : 'idle'))
    })

    try {
      const session = await createSession()
      await room.connect(session.server_url, session.participant_token)
      await room.startAudio()
      await room.localParticipant.setMicrophoneEnabled(true)
      setStatus(room.remoteParticipants.size > 0 ? 'live' : 'waiting')
    } catch (err) {
      console.error(err)
      setError(err instanceof Error ? err.message : String(err))
      setStatus('error')
      await room.disconnect()
      roomRef.current = null
    }
  }, [])

  const end = useCallback(() => {
    void roomRef.current?.disconnect()
  }, [])

  // Hang up if the page is closed or the component goes away.
  useEffect(() => {
    return () => {
      void roomRef.current?.disconnect()
    }
  }, [])

  return { status, error, launch, end }
}
