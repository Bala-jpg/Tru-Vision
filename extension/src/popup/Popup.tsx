import { useState, useEffect } from 'react'

type Preferences = {
  tts_enabled: boolean
  tts_voice: string
  tts_speed: number
  captions_enabled: boolean
  caption_font_size: string
  sign_detection_enabled: boolean
  overlay_position: string
  overlay_opacity: number
}

const defaultPrefs: Preferences = {
  tts_enabled: true,
  tts_voice: 'en-IN-Wavenet-B',
  tts_speed: 1.0,
  captions_enabled: true,
  caption_font_size: 'medium',
  sign_detection_enabled: true,
  overlay_position: 'bottom-right',
  overlay_opacity: 0.9,
}

const statusColors: Record<string, string> = {
  connected: '#4CAF50',
  connecting: '#FFC107',
  disconnected: '#F44336',
  failed: '#F44336',
}

export function Popup() {
  const [prefs, setPrefs] = useState<Preferences>(defaultPrefs)
  const [wsStatus, setWsStatus] = useState('disconnected')

  useEffect(() => {
    if (typeof chrome === 'undefined' || !chrome.storage?.local) return

    chrome.storage.local.get(['user_preferences', 'ws_connection_status'], (res) => {
      if (res['user_preferences']) setPrefs(res['user_preferences'] as Preferences)
      if (res['ws_connection_status']) setWsStatus(res['ws_connection_status'] as string)
    })

    const listener = (changes: Record<string, chrome.storage.StorageChange>) => {
      if (changes['ws_connection_status']?.newValue) {
        setWsStatus(changes['ws_connection_status'].newValue as string)
      }
    }
    chrome.storage.onChanged.addListener(listener)
    return () => chrome.storage.onChanged.removeListener(listener)
  }, [])

  const togglePref = (key: keyof Preferences) => {
    const updated = { ...prefs, [key]: !prefs[key] }
    setPrefs(updated)
    if (typeof chrome !== 'undefined' && chrome.storage?.local) {
      chrome.storage.local.set({ user_preferences: updated })
    }
  }

  return (
    <div className="w-80 bg-[#0f0f0f] text-[#e8e8e8] font-sans p-4 select-none">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-white/10 pb-3 mb-4">
        <div className="flex items-center gap-2">
          <span className="text-lg font-semibold text-[#64B5F6]">TruVision</span>
          <span className="text-xs text-[#888] uppercase tracking-widest">v0.1</span>
        </div>
        <div className="flex items-center gap-2">
          <span
            className="w-2 h-2 rounded-full inline-block transition-all"
            style={{ background: statusColors[wsStatus] ?? '#F44336' }}
          />
          <span className="text-xs text-[#888] capitalize">{wsStatus}</span>
        </div>
      </header>

      {/* Toggle Controls */}
      <div className="flex flex-col gap-3">
        <ToggleRow
          label="Sign Recognition"
          description="Real-time ISL gesture detection"
          checked={prefs.sign_detection_enabled}
          onToggle={() => togglePref('sign_detection_enabled')}
          id="toggle-sign"
        />
        <ToggleRow
          label="Speech Synthesizer"
          description="TTS voice for recognized signs"
          checked={prefs.tts_enabled}
          onToggle={() => togglePref('tts_enabled')}
          id="toggle-tts"
        />
        <ToggleRow
          label="Live Captions"
          description="Transcribe participant speech"
          checked={prefs.captions_enabled}
          onToggle={() => togglePref('captions_enabled')}
          id="toggle-captions"
        />
      </div>

      {/* Notice */}
      <p className="mt-4 text-[11px] text-[#666] bg-white/5 rounded-lg p-2.5 border border-white/[0.06] leading-relaxed">
        <strong className="text-[#888]">Audio tip:</strong> Share your Chrome tab audio so other
        participants can hear synthesized speech.
      </p>
    </div>
  )
}

type ToggleRowProps = {
  label: string
  description: string
  checked: boolean
  onToggle: () => void
  id: string
}

function ToggleRow({ label, description, checked, onToggle, id }: ToggleRowProps) {
  return (
    <div className="flex items-center justify-between gap-3">
      <label htmlFor={id} className="flex flex-col cursor-pointer">
        <span className="text-sm font-medium text-[#e8e8e8]">{label}</span>
        <span className="text-[11px] text-[#666]">{description}</span>
      </label>
      <button
        id={id}
        role="switch"
        aria-checked={checked}
        onClick={onToggle}
        className={`relative w-10 h-5 rounded-full transition-colors duration-200 flex-shrink-0 ${
          checked ? 'bg-[#64B5F6]' : 'bg-white/20'
        }`}
      >
        <span
          className={`absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform duration-200 ${
            checked ? 'translate-x-5' : 'translate-x-0'
          }`}
        />
      </button>
    </div>
  )
}
