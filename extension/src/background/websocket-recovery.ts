export class WebSocketRecoveryManager<T = unknown> {
  private wsUrl: string
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectInterval = 3000 // 3 seconds
  private keepAliveInterval: ReturnType<typeof setInterval> | null = null
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private isIntentionalDisconnect = false
  private onMessageCallback: ((msg: T) => void) | null = null

  constructor(wsUrl: string) {
    this.wsUrl = wsUrl
    this.initAlarmKeepalive()
  }

  public connect(onMessage: (msg: T) => void) {
    if (
      this.ws &&
      (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)
    ) {
      return
    }

    this.onMessageCallback = onMessage
    this.isIntentionalDisconnect = false
    this.updateStatus('connecting')

    console.log(`Attempting connection to ${this.wsUrl}...`)
    try {
      this.ws = new WebSocket(this.wsUrl)
      this.ws.binaryType = 'arraybuffer'

      this.ws.onopen = () => {
        this.reconnectAttempts = 0
        this.updateStatus('connected')
        console.log('WebSocket connection established successfully.')
        this.startKeepAlive()
      }

      this.ws.onmessage = (event) => {
        if (this.onMessageCallback) {
          try {
            const parsed = JSON.parse(event.data)
            this.onMessageCallback(parsed as T)
          } catch {
            this.onMessageCallback(event.data as T)
          }
        }
      }

      this.ws.onclose = () => {
        this.updateStatus('disconnected')
        this.stopKeepAlive()
        if (!this.isIntentionalDisconnect) {
          this.handleReconnection()
        }
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
    } catch (e) {
      console.error('Failed to construct WebSocket client:', e)
      this.handleReconnection()
    }
  }

  public send(data: string | ArrayBuffer) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(data)
    } else {
      console.warn('Unable to send data: WebSocket connection is offline.')
    }
  }

  public disconnect() {
    this.isIntentionalDisconnect = true
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    this.stopKeepAlive()
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.updateStatus('disconnected')
  }

  private handleReconnection() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached. Idle.')
      this.updateStatus('failed')
      return
    }

    this.reconnectAttempts++
    const delay = this.reconnectInterval * Math.pow(1.5, this.reconnectAttempts - 1)
    console.log(
      `Reconnecting in ${delay}ms (Attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`
    )

    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null
      if (this.onMessageCallback) {
        this.connect(this.onMessageCallback)
      }
    }, delay)
  }

  private startKeepAlive() {
    this.stopKeepAlive()
    // Send a periodic heartbeat frame to prevent connection timeouts on both ends
    this.keepAliveInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }))
      }
    }, 15000) // 15 seconds
  }

  private stopKeepAlive() {
    if (this.keepAliveInterval) {
      clearInterval(this.keepAliveInterval)
      this.keepAliveInterval = null
    }
  }

  private initAlarmKeepalive() {
    // MV3 Service Worker keepalive. Sets chrome alarm to wake worker up if terminated
    if (typeof chrome !== 'undefined' && chrome.alarms) {
      chrome.alarms.create('ws-keepalive', { periodInMinutes: 0.5 })
      chrome.alarms.onAlarm.addListener((alarm: chrome.alarms.Alarm) => {
        if (alarm.name === 'ws-keepalive') {
          console.log('Waking service worker via keepalive alarm.')
          // If disconnected, try reconnecting
          if (this.ws && this.ws.readyState === WebSocket.CLOSED && this.onMessageCallback) {
            this.connect(this.onMessageCallback)
          }
        }
      })
    }
  }

  private updateStatus(status: 'connected' | 'disconnected' | 'connecting' | 'failed') {
    if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
      chrome.storage.local.set({ ws_connection_status: status })
    }
  }
}
