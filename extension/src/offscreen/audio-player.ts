export class AudioPlayer {
  private audioCtx: AudioContext | null = null
  private audioDestination: MediaStreamAudioDestinationNode | null = null

  constructor() {
    // Lazy initialize AudioContext on first playback to comply with browser user-interaction policies
  }

  private initAudio() {
    if (!this.audioCtx) {
      const AudioCtxClass =
        window.AudioContext ||
        (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext
      this.audioCtx = new AudioCtxClass()

      // Phase 2 setup: Create a MediaStream destination node so we can mix and pipe our TTS
      // output directly into Google Meet's outgoing WebRTC audio stream.
      this.audioDestination = this.audioCtx.createMediaStreamDestination()
    }
  }

  /**
   * Decodes a base64 encoded audio string and plays it through the speakers (Phase 1)
   * and/or outputs to the WebRTC destination stream (Phase 2).
   */
  public async playBase64Audio(base64Data: string): Promise<void> {
    this.initAudio()
    if (!this.audioCtx) return

    try {
      // Convert base64 to ArrayBuffer
      const binaryString = window.atob(base64Data)
      const len = binaryString.length
      const bytes = new Uint8Array(len)
      for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i)
      }

      const arrayBuffer = bytes.buffer

      // Decode the audio data asynchronously
      const audioBuffer = await this.audioCtx.decodeAudioData(arrayBuffer)

      // Create a buffer source node
      const source = this.audioCtx.createBufferSource()
      source.buffer = audioBuffer

      // --- PHASE 1 (MVP): Play audio locally to speakers ---
      source.connect(this.audioCtx.destination)

      // --- PHASE 2 (UPGRADE): Mix TTS with output stream track ---
      if (this.audioDestination) {
        source.connect(this.audioDestination)
      }

      source.start(0)
      console.log('TTS Audio playback started.')
    } catch (e) {
      console.error('Audio decoding or playback failed:', e)
    }
  }

  /**
   * Returns the MediaStream track containing synthesized TTS speech (Phase 2 helper)
   */
  public getTTSMediaStream(): MediaStream | null {
    this.initAudio()
    return this.audioDestination ? this.audioDestination.stream : null
  }
}
