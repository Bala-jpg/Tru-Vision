import { AudioPlayer } from './audio-player'

const player = new AudioPlayer()

type IncomingMessage = {
  type: string
  payload?: Record<string, unknown>
}

chrome.runtime.onMessage.addListener(
  (
    message: IncomingMessage,
    _sender: chrome.runtime.MessageSender,
    sendResponse: (r: unknown) => void
  ) => {
    const { type, payload } = message

    switch (type) {
      case 'PLAY_AUDIO_SRC':
        if (payload?.audioBase64) {
          player.playBase64Audio(payload.audioBase64 as string).then(() => {
            sendResponse({ status: 'playing' })
          })
          return true
        }
        break

      case 'START_TAB_CAPTURE':
        if (payload?.streamId) {
          startAudioCapture(payload.streamId as string)
        }
        break
    }
  }
)

function startAudioCapture(streamId: string) {
  ;(
    navigator.mediaDevices as MediaDevices & {
      getUserMedia(constraints: Record<string, unknown>): Promise<MediaStream>
    }
  )
    .getUserMedia({
      audio: {
        mandatory: {
          chromeMediaSource: 'tab',
          chromeMediaSourceId: streamId,
        },
      },
      video: false,
    })
    .then((stream: MediaStream) => {
      const audioCtx = new AudioContext({ sampleRate: 16000 })
      const source = audioCtx.createMediaStreamSource(stream)
      // ScriptProcessor is deprecated but still the only MV3 offscreen option
      const processor = audioCtx.createScriptProcessor(4096, 1, 1)

      source.connect(processor)
      processor.connect(audioCtx.destination)

      processor.onaudioprocess = (e: AudioProcessingEvent) => {
        const inputData = e.inputBuffer.getChannelData(0)
        const len = inputData.length
        const buffer = new Int16Array(len)
        for (let i = 0; i < len; i++) {
          const s = Math.max(-1, Math.min(1, inputData[i]))
          buffer[i] = s < 0 ? s * 0x8000 : s * 0x7fff
        }
        chrome.runtime.sendMessage({
          type: 'STREAM_AUDIO_CHUNK',
          payload: { chunk: buffer.buffer },
        })
      }
    })
    .catch((err: unknown) => {
      console.error('Tab audio capture failed:', err)
    })
}
