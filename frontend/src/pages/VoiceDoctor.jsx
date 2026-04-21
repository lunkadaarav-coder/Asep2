import { useState, useRef } from 'react'
import { Mic, MicOff, Send, Volume2, Languages } from 'lucide-react'

export default function VoiceDoctor() {
    const [isRecording, setIsRecording] = useState(false)
    const [textInput, setTextInput] = useState('')
    const [language, setLanguage] = useState('en')
    const [loading, setLoading] = useState(false)
    const [conversations, setConversations] = useState([])
    const [recordingTime, setRecordingTime] = useState(0)
    const mediaRecorderRef = useRef(null)
    const chunksRef = useRef([])
    const timerRef = useRef(null)
    const streamRef = useRef(null)

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    channelCount: 1,
                    sampleRate: 16000,
                    echoCancellation: true,
                    noiseSuppression: true
                }
            })
            streamRef.current = stream
            chunksRef.current = []

            const mediaRecorder = new MediaRecorder(stream, {
                mimeType: MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
                    ? 'audio/webm;codecs=opus'
                    : 'audio/webm'
            })
            mediaRecorderRef.current = mediaRecorder

            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    chunksRef.current.push(e.data)
                }
            }

            mediaRecorder.onstop = async () => {
                const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
                await sendAudioToBackend(blob)
            }

            mediaRecorder.start(250) // collect data every 250ms
            setIsRecording(true)
            setRecordingTime(0)

            // Recording timer
            timerRef.current = setInterval(() => {
                setRecordingTime(prev => prev + 1)
            }, 1000)

        } catch (err) {
            console.error('Microphone access denied:', err)
            // Fallback: show error message
            setConversations(prev => [...prev, {
                type: 'ai',
                text: '🎤 Microphone access denied. Please allow microphone permission in your browser, or use the text input below to type your question.'
            }])
        }
    }

    const stopRecording = () => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
            mediaRecorderRef.current.stop()
        }
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop())
            streamRef.current = null
        }
        if (timerRef.current) {
            clearInterval(timerRef.current)
            timerRef.current = null
        }
        setIsRecording(false)
    }

    const handleVoiceToggle = () => {
        if (isRecording) {
            stopRecording()
        } else {
            startRecording()
        }
    }

    const sendAudioToBackend = async (audioBlob) => {
        setLoading(true)
        try {
            const formData = new FormData()
            formData.append('audio', audioBlob, 'recording.webm')
            formData.append('language', language)

            const res = await fetch('/api/voice/ask', { method: 'POST', body: formData })
            if (!res.ok) throw new Error(`Server error: ${res.status}`)
            const data = await res.json()

            setConversations(prev => [...prev,
            { type: 'user', text: `🎤 ${data.transcript || '(audio sent)'}` },
            { type: 'ai', text: data.ai_response }
            ])
        } catch (err) {
            console.error('Voice request failed:', err)
            setConversations(prev => [...prev,
            { type: 'user', text: '🎤 (voice recording sent)' },
            { type: 'ai', text: '⚠️ Could not process audio. Make sure the backend is running and ffmpeg is installed for Whisper. Try using text input instead.' }
            ])
        }
        setLoading(false)
    }

    const handleTextSubmit = async () => {
        if (!textInput.trim()) return
        setLoading(true)
        const question = textInput
        setTextInput('')

        try {
            const formData = new FormData()
            formData.append('question', question)
            formData.append('language', language)
            const res = await fetch('/api/voice/text-ask', { method: 'POST', body: formData })
            if (!res.ok) throw new Error(`Server error: ${res.status}`)
            const data = await res.json()
            setConversations(prev => [...prev, { type: 'user', text: question }, { type: 'ai', text: data.ai_response }])
        } catch (err) {
            console.error('Text query failed:', err)
            setConversations(prev => [...prev,
            { type: 'user', text: question },
            { type: 'ai', text: '⚠️ Could not reach the backend. Make sure the server is running on port 8000.\n\n_Tip: Use the text input when voice is unavailable._' }
            ])
        }
        setLoading(false)
    }

    const formatTime = (seconds) => {
        const m = Math.floor(seconds / 60)
        const s = seconds % 60
        return `${m}:${s.toString().padStart(2, '0')}`
    }

    return (
        <div>
            <div className="page-header">
                <h2>🎤 Voice AI Doctor</h2>
                <p>Ask health questions using your real voice or text – get instant AI-powered medical guidance</p>
            </div>

            <div style={{ display: 'flex', gap: 24 }}>
                {/* Left: Controls */}
                <div style={{ width: 280, flexShrink: 0 }}>
                    <div className="glass-card animate-in" style={{ textAlign: 'center', marginBottom: 16 }}>
                        <div className="tabs" style={{ justifyContent: 'center', marginBottom: 20 }}>
                            <button className={`tab ${language === 'en' ? 'active' : ''}`} onClick={() => setLanguage('en')}>English</button>
                            <button className={`tab ${language === 'hi' ? 'active' : ''}`} onClick={() => setLanguage('hi')}>हिंदी</button>
                        </div>

                        <div className={`voice-circle ${isRecording ? 'recording' : ''}`} onClick={handleVoiceToggle}>
                            {isRecording ? <MicOff size={40} color="#ef4444" /> : <Mic size={40} color="#06b6d4" />}
                        </div>
                        <p style={{ marginTop: 16, fontSize: 13, color: 'var(--text-secondary)' }}>
                            {isRecording
                                ? `🔴 Recording... ${formatTime(recordingTime)} – Click to stop & send`
                                : 'Click to start voice recording'}
                        </p>
                        {isRecording && (
                            <div style={{ marginTop: 8, fontSize: 11, color: 'var(--text-muted)' }}>
                                Speak your health question clearly
                            </div>
                        )}
                    </div>

                    <div className="glass-card animate-in" style={{ padding: 16 }}>
                        <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>💡 Try asking:</p>
                        {[
                            language === 'en' ? 'What foods reduce cholesterol?' : 'कोलेस्ट्रॉल कम करने के लिए क्या खाएं?',
                            language === 'en' ? 'My sugar level is 200, is it dangerous?' : 'मेरा शुगर 200 है, क्या खतरनाक है?',
                            language === 'en' ? 'Home remedies for joint pain' : 'जोड़ों के दर्द का घरेलू इलाज',
                        ].map((q, i) => (
                            <button key={i} className="btn btn-outline btn-sm" style={{ width: '100%', marginBottom: 6, fontSize: 11, justifyContent: 'flex-start' }}
                                onClick={() => { setTextInput(q) }}>
                                {q}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Right: Chat */}
                <div className="glass-card animate-in" style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 500 }}>
                    <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                        💬 Conversation
                        {loading && <span className="spinner" style={{ width: 16, height: 16 }} />}
                    </h3>

                    <div style={{ flex: 1, overflowY: 'auto', marginBottom: 16 }}>
                        {conversations.length === 0 ? (
                            <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-muted)' }}>
                                <span style={{ fontSize: 48, display: 'block', marginBottom: 12 }}>🩺</span>
                                <p>Start a conversation with your AI health assistant</p>
                                <p style={{ fontSize: 12, marginTop: 4 }}>Click the mic button to record your voice, or type below</p>
                            </div>
                        ) : (
                            conversations.map((msg, i) => (
                                <div key={i} className={`chat-bubble ${msg.type}`} style={{ whiteSpace: 'pre-wrap' }}>
                                    {msg.type === 'ai' && <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 6 }}>🤖 HealthMitra AI</div>}
                                    {msg.text}
                                </div>
                            ))
                        )}
                    </div>

                    {/* Text Input */}
                    <div style={{ display: 'flex', gap: 8 }}>
                        <input
                            className="form-input"
                            style={{ flex: 1 }}
                            placeholder={language === 'en' ? 'Type your health question...' : 'अपना स्वास्थ्य सवाल यहां लिखें...'}
                            value={textInput}
                            onChange={e => setTextInput(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && handleTextSubmit()}
                        />
                        <button className="btn btn-primary" onClick={handleTextSubmit} disabled={!textInput.trim() || loading}>
                            <Send size={18} />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    )
}
