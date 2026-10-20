import { WebSocketRecoveryManager } from './websocket-recovery'

const BACKEND_HOST = 'localhost:8000'
const signWsUrl = `ws://${BACKEND_HOST}/ws/sign`
const speechWsUrl = `ws://${BACKEND_HOST}/ws/speech`

let signWs: WebSocketRecoveryManager<Record<string, unknown>> | null = null
let speechWs: WebSocketRecoveryManager<Record<string, unknown>> | null = null
let hasOffscreen = false

function initWebSockets() {
  if (!signWs) signWs = new WebSocketRecoveryManager<Record<string, unknown>>(signWsUrl)
  if (!speechWs) speechWs = new WebSocketRecoveryManager<Record<string, unknown>>(speechWsUrl)
}

// ─── Offscreen Document Management ──────────────────────────────────────────

async function createOffscreenDocument() {
  const offscreenUrl = chrome.runtime.getURL('src/offscreen/index.html')
  const contexts = await chrome.runtime.getContexts({
    contextTypes: [chrome.runtime.ContextType.OFFSCREEN_DOCUMENT],
  })
  if (contexts.length > 0) {
    hasOffscreen = true
    return
  }
  try {
    await chrome.offscreen.createDocument({
      url: offscreenUrl,
      reasons: [chrome.offscreen.Reason.AUDIO_PLAYBACK, chrome.offscreen.Reason.USER_MEDIA],
      justification: 'Play TTS audio and capture tab audio for speech transcription.',
    })
    hasOffscreen = true
  } catch (e) {
    console.error('Failed to create offscreen document:', e)
  }
}

async function destroyOffscreenDocument() {
  if (!hasOffscreen) return
  try {
    await chrome.offscreen.closeDocument()
    hasOffscreen = false
  } catch (e) {
    console.error('Failed to destroy offscreen document:', e)
  }
}

// ─── Lifecycle ───────────────────────────────────────────────────────────────

chrome.runtime.onInstalled.addListener(() => {
  console.log('TruVision service worker installed.')
  initWebSockets()
})

chrome.runtime.onStartup.addListener(() => {
  console.log('TruVision service worker starting up.')
  initWebSockets()
})

// ─── Message Handler ─────────────────────────────────────────────────────────

type IncomingMessage = {
  type: string
  payload?: Record<string, unknown>
}

chrome.runtime.onMessage.addListener(
  (
    message: IncomingMessage,
    sender: chrome.runtime.MessageSender,
    sendResponse: (response: Record<string, string>) => void
  ) => {
    const { type, payload } = message
    initWebSockets()

    switch (type) {
      case 'START_SESSION':
        createOffscreenDocument().then(() => {
          signWs?.connect((prediction: Record<string, unknown>) => {
            if (sender.tab?.id) {
              chrome.tabs.sendMessage(sender.tab.id, {
                type: 'SIGN_RECOGNIZED',
                payload: prediction,
              })
            }
          })
          speechWs?.connect((transcript: Record<string, unknown>) => {
            if (sender.tab?.id) {
              chrome.tabs.sendMessage(sender.tab.id, {
                type: 'SPEECH_TRANSCRIBED',
                payload: transcript,
              })
            }
          })
          sendResponse({ status: 'session_initialized' })
        })
        return true

      case 'STOP_SESSION':
        destroyOffscreenDocument().then(() => {
          signWs?.disconnect()
          speechWs?.disconnect()
          sendResponse({ status: 'session_stopped' })
        })
        return true

      case 'STREAM_LANDMARKS':
        signWs?.send(JSON.stringify({ landmarks: payload?.landmarks, timestamp: Date.now() }))
        break

      case 'STREAM_AUDIO_CHUNK':
        if (payload?.chunk) {
          speechWs?.send(payload.chunk as ArrayBuffer)
        }
        break

      case 'PLAY_TTS_AUDIO':
        if (hasOffscreen) {
          chrome.runtime.sendMessage({ type: 'PLAY_AUDIO_SRC', payload })
        }
        break
    }
  }
)
