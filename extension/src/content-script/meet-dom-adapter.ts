export class MeetDOMAdapter {
  private static instance: MeetDOMAdapter
  private observer: MutationObserver | null = null
  private onMuteChangeCallbacks: ((muted: boolean) => void)[] = []

  private constructor() {
    this.initObserver()
  }

  public static getInstance(): MeetDOMAdapter {
    if (!MeetDOMAdapter.instance) {
      MeetDOMAdapter.instance = new MeetDOMAdapter()
    }
    return MeetDOMAdapter.instance
  }

  /**
   * Detects whether the user is actively inside a Google Meet call.
   */
  public isInsideCall(): boolean {
    // Buttons with aria-label containing "Leave call" or "Hang up" indicates a live session
    const leaveButton = document.querySelector(
      '[aria-label*="Leave call"], [aria-label*="End call"], [data-is-muted]'
    )
    return !!leaveButton
  }

  /**
   * Fetches the element where we can safely anchor/inject our custom React accessibility UI overlay.
   */
  public getOverlayAnchor(): HTMLElement | null {
    // Anchor to Meet's primary video grid container or main body
    const videoGrid = document.querySelector('[data-layout="video-grid"]') as HTMLElement
    return videoGrid || document.body
  }

  /**
   * Fetches Google Meet's native microphone button to check mute state or trigger mute toggle.
   */
  public getMicrophoneButton(): HTMLElement | null {
    // Google Meet mic toggle buttons are typically identified by aria-label matching 'microphone'
    return (document.querySelector('[aria-label*="microphone" i][data-is-muted]') ||
      document.querySelector('[aria-label*="mic" i]')) as HTMLElement
  }

  /**
   * Detects whether the user's microphone is muted in Google Meet.
   */
  public isMicrophoneMuted(): boolean {
    const micButton = this.getMicrophoneButton()
    if (!micButton) return true

    // Google Meet sets data-is-muted="true" on muted mic buttons
    const isMutedAttr = micButton.getAttribute('data-is-muted')
    if (isMutedAttr !== null) {
      return isMutedAttr === 'true'
    }

    // Fallback: check text label or classes
    const label = micButton.getAttribute('aria-label') || ''
    return label.toLowerCase().includes('turn on microphone')
  }

  /**
   * Registers callback to listen for Google Meet microphone state mutations (e.g. user toggles mute).
   */
  public onMuteChange(callback: (muted: boolean) => void): void {
    this.onMuteChangeCallbacks.push(callback)
  }

  private initObserver() {
    if (typeof window === 'undefined' || !window.document) return

    this.observer = new MutationObserver(() => {
      const currentMute = this.isMicrophoneMuted()
      this.onMuteChangeCallbacks.forEach((cb) => cb(currentMute))
    })

    // Observe body for changes in mute buttons attributes
    this.observer.observe(document.body, {
      attributes: true,
      subtree: true,
      attributeFilter: ['data-is-muted', 'aria-label'],
    })
  }

  public destroy(): void {
    if (this.observer) {
      this.observer.disconnect()
      this.observer = null
    }
    this.onMuteChangeCallbacks = []
  }
}
