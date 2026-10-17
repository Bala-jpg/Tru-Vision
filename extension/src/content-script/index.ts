import { MeetDOMAdapter } from './meet-dom-adapter'

console.log('TruVision content script initialized.')

const domAdapter = MeetDOMAdapter.getInstance()

let isSessionActive = false
let webcamStream: MediaStream | null = null
let captureInterval: ReturnType<typeof setInterval> | null = null

// ─── Session Lifecycle ──────────────────────────────────────────────────────

function checkSession() {
  const insideCall = domAdapter.isInsideCall()
  if (insideCall && !isSessionActive) {
    console.log('Google Meet call detected. Initializing TruVision session...')
    startSession()
  } else if (!insideCall && isSessionActive) {
    console.log('Left Google Meet call. Stopping TruVision session.')
    stopSession()
  }
}

function startSession() {
  isSessionActive = true

  // Inject overlay if not already present
  if (!document.getElementById('truvision-overlay-root')) {
    const parent = domAdapter.getOverlayAnchor()
    if (parent) {
      const anchor = document.createElement('div')
      anchor.id = 'truvision-overlay-root'

      // Shadow DOM isolates our CSS from Google Meet's stylesheet
      const shadow = anchor.attachShadow({ mode: 'open' })
      const container = document.createElement('div')
      container.id = 'truvision-container'
      container.innerHTML = `
        <div style="
          position: fixed;
          bottom: 80px;
          right: 20px;
          background: rgba(18, 18, 18, 0.96);
          color: #e8e8e8;
          padding: 16px 20px;
          border-radius: 14px;
          font-family: 'Outfit', 'Inter', sans-serif;
          font-size: 13px;
          box-shadow: 0 8px 32px rgba(0,0,0,0.5);
          border: 1px solid rgba(255,255,255,0.08);
          z-index: 9999;
          width: 300px;
          backdrop-filter: blur(12px);
        ">
          <div style="display:flex; align-items:center; gap:8px; margin-bottom:10px;">
            <span style="width:8px;height:8px;background:#4CAF50;border-radius:50%;display:inline-block;"></span>
            <strong style="font-size:14px; color:#64B5F6;">TruVision</strong>
          </div>
          <div id="truvision-signs-panel" style="color:#ccc; margin-bottom:6px;">
            Sign: <strong style="color:#64B5F6;">—</strong>
          </div>
          <div id="truvision-captions-panel" style="color:#ccc; font-style:italic;">
            Waiting for audio...
          </div>
        </div>
      `
      shadow.appendChild(container)
      parent.appendChild(anchor)
    }
  }

  // Signal background worker to start WS connections + offscreen document
  chrome.runtime.sendMessage({ type: 'START_SESSION' }, (response: unknown) => {
    console.log('Session init response:', response)
  })

  startWebcamCapture()
}

function stopSession() {
  isSessionActive = false
  document.getElementById('truvision-overlay-root')?.remove()
  chrome.runtime.sendMessage({ type: 'STOP_SESSION' })
  stopWebcamCapture()
}

// ─── Webcam Capture (Landmark stub — MediaPipe wired in later) ───────────────

function startWebcamCapture() {
  navigator.mediaDevices
    .getUserMedia({ video: { width: 640, height: 480 }, audio: false })
    .then((stream) => {
      webcamStream = stream
      // 10 FPS mock landmark stream — replaced by real MediaPipe extraction in Phase 3
      captureInterval = setInterval(() => {
        const mockLandmarks = Array.from({ length: 126 }, () => Math.random() * 0.1)
        chrome.runtime.sendMessage({
          type: 'STREAM_LANDMARKS',
          payload: { landmarks: mockLandmarks },
        })
      }, 100)
    })
    .catch((err: unknown) => {
      console.warn('Failed to open webcam for gesture capture:', err)
    })
}

function stopWebcamCapture() {
  if (captureInterval) {
    clearInterval(captureInterval)
    captureInterval = null
  }
  webcamStream?.getTracks().forEach((t) => t.stop())
  webcamStream = null
}

// ─── Message Receiver ────────────────────────────────────────────────────────

chrome.runtime.onMessage.addListener(
  (message: { type: string; payload: Record<string, unknown> }) => {
    const { type, payload } = message
    const anchor = document.getElementById('truvision-overlay-root')
    if (!anchor?.shadowRoot) return

    const shadow = anchor.shadowRoot

    if (type === 'SIGN_RECOGNIZED') {
      const panel = shadow.getElementById('truvision-signs-panel')
      if (panel) {
        const sign = payload.sign as string
        const confidence = Math.round((payload.confidence as number) * 100)
        panel.innerHTML = `Sign: <strong style="color:#64B5F6;">${sign}</strong> <span style="color:#888;">(${confidence}%)</span>`

        // Phase 1: Request TTS audio synthesis for this sign
        chrome.runtime.sendMessage({ type: 'PLAY_TTS_AUDIO', payload: { audioBase64: '' } })
      }
    } else if (type === 'SPEECH_TRANSCRIBED') {
      const panel = shadow.getElementById('truvision-captions-panel')
      if (panel) {
        panel.innerHTML = `<span style="font-style:normal; color:#e8e8e8;">${payload.text as string}</span>`
      }
    }
  }
)

// ─── Bootstrap ───────────────────────────────────────────────────────────────

setInterval(checkSession, 2000)

domAdapter.onMuteChange((muted: boolean) => {
  console.log(`Mic state: ${muted ? 'MUTED' : 'LIVE'}`)
})
