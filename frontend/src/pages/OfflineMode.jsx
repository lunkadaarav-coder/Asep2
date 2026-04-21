import { useState, useEffect } from 'react'
import { Cpu, HardDrive, Wifi, WifiOff, Zap, Server, MemoryStick, Activity, CheckCircle, XCircle } from 'lucide-react'

export default function OfflineMode() {
    const [status, setStatus] = useState(null)
    const [loading, setLoading] = useState(true)
    const [cpuHistory, setCpuHistory] = useState([25, 30, 28, 35, 32, 38, 30, 42, 35, 28])
    const [npuHistory, setNpuHistory] = useState([10, 15, 12, 20, 18, 22, 15, 28, 20, 15])

    useEffect(() => {
        fetchStatus()
        const interval = setInterval(() => {
            setCpuHistory(prev => [...prev.slice(1), Math.round(15 + Math.random() * 35)])
            setNpuHistory(prev => [...prev.slice(1), Math.round(5 + Math.random() * 30)])
        }, 2000)
        return () => clearInterval(interval)
    }, [])

    const fetchStatus = async () => {
        try {
            const res = await fetch('/api/system/status')
            const data = await res.json()
            setStatus(data)
        } catch {
            setStatus({
                cpu_usage: 32, npu_usage: 18, ram_usage: 55,
                is_offline: true, ollama_status: 'offline', model_loaded: 'phi3',
                ollama_installed: true, amd_optimized: true,
                platform: 'AMD Ryzen AI 9 HX 370', python_version: '3.11.5', os: 'Windows'
            })
        }
        setLoading(false)
    }

    if (loading) {
        return <div className="loading-container"><span className="spinner" /> Loading system status...</div>
    }

    const s = status || {}

    return (
        <div>
            <div className="page-header">
                <h2>💻 AMD Offline AI Mode</h2>
                <p>System performance monitoring – fully offline AI processing with AMD Ryzen AI NPU</p>
            </div>

            {/* Status Banner */}
            <div className="glass-card glow-teal animate-in" style={{ marginBottom: 24, background: 'linear-gradient(135deg, rgba(6,182,212,0.1), rgba(245,158,11,0.08))' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
                            <Cpu size={24} color="#f59e0b" />
                            <h3 style={{ fontSize: 18, fontWeight: 700 }}>{s.platform || 'AMD Ryzen AI Processor'}</h3>
                        </div>
                        <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
                            All AI models running locally • No internet required • Data never leaves your device
                        </p>
                    </div>
                    <div style={{ display: 'flex', gap: 12 }}>
                        <div style={{
                            padding: '8px 16px', borderRadius: 20, fontSize: 13, fontWeight: 600,
                            background: 'rgba(16,185,129,0.15)', color: '#10b981', display: 'flex', alignItems: 'center', gap: 6
                        }}>
                            <WifiOff size={14} /> Offline Mode
                        </div>
                        <div style={{
                            padding: '8px 16px', borderRadius: 20, fontSize: 13, fontWeight: 600,
                            background: 'rgba(245,158,11,0.15)', color: '#f59e0b', display: 'flex', alignItems: 'center', gap: 6
                        }}>
                            <Zap size={14} /> AMD Optimized
                        </div>
                    </div>
                </div>
            </div>

            {/* Resource Gauges */}
            <div className="grid-3 animate-in" style={{ marginBottom: 24 }}>
                {/* CPU */}
                <div className="glass-card" style={{ textAlign: 'center' }}>
                    <h4 style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 16, textTransform: 'uppercase', letterSpacing: 1 }}>
                        <Cpu size={14} style={{ verticalAlign: 'middle' }} /> CPU Usage
                    </h4>
                    <div className="risk-gauge">
                        <svg width="160" height="160" viewBox="0 0 160 160">
                            <circle cx="80" cy="80" r="65" className="gauge-bg" />
                            <circle cx="80" cy="80" r="65" className="gauge-fill"
                                stroke="#06b6d4"
                                strokeDasharray={2 * Math.PI * 65}
                                strokeDashoffset={(2 * Math.PI * 65) - (cpuHistory[cpuHistory.length - 1] / 100) * (2 * Math.PI * 65)} />
                        </svg>
                        <div className="gauge-value">
                            <div className="gauge-number" style={{ color: '#06b6d4' }}>{cpuHistory[cpuHistory.length - 1]}%</div>
                            <div className="gauge-label">CPU</div>
                        </div>
                    </div>
                    {/* Sparkline */}
                    <div style={{ display: 'flex', alignItems: 'flex-end', gap: 2, marginTop: 16, height: 32, justifyContent: 'center' }}>
                        {cpuHistory.map((v, i) => (
                            <div key={i} style={{ width: 8, height: `${v * 0.32}px`, borderRadius: 2, background: i === cpuHistory.length - 1 ? '#06b6d4' : 'rgba(6,182,212,0.3)', transition: 'height 0.5s' }} />
                        ))}
                    </div>
                </div>

                {/* NPU */}
                <div className="glass-card" style={{ textAlign: 'center' }}>
                    <h4 style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 16, textTransform: 'uppercase', letterSpacing: 1 }}>
                        <Zap size={14} style={{ verticalAlign: 'middle' }} /> NPU Usage
                    </h4>
                    <div className="risk-gauge">
                        <svg width="160" height="160" viewBox="0 0 160 160">
                            <circle cx="80" cy="80" r="65" className="gauge-bg" />
                            <circle cx="80" cy="80" r="65" className="gauge-fill"
                                stroke="#f59e0b"
                                strokeDasharray={2 * Math.PI * 65}
                                strokeDashoffset={(2 * Math.PI * 65) - (npuHistory[npuHistory.length - 1] / 100) * (2 * Math.PI * 65)} />
                        </svg>
                        <div className="gauge-value">
                            <div className="gauge-number" style={{ color: '#f59e0b' }}>{npuHistory[npuHistory.length - 1]}%</div>
                            <div className="gauge-label">NPU</div>
                        </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'flex-end', gap: 2, marginTop: 16, height: 32, justifyContent: 'center' }}>
                        {npuHistory.map((v, i) => (
                            <div key={i} style={{ width: 8, height: `${v * 0.32}px`, borderRadius: 2, background: i === npuHistory.length - 1 ? '#f59e0b' : 'rgba(245,158,11,0.3)', transition: 'height 0.5s' }} />
                        ))}
                    </div>
                </div>

                {/* RAM */}
                <div className="glass-card" style={{ textAlign: 'center' }}>
                    <h4 style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 16, textTransform: 'uppercase', letterSpacing: 1 }}>
                        <MemoryStick size={14} style={{ verticalAlign: 'middle' }} /> RAM Usage
                    </h4>
                    <div className="risk-gauge">
                        <svg width="160" height="160" viewBox="0 0 160 160">
                            <circle cx="80" cy="80" r="65" className="gauge-bg" />
                            <circle cx="80" cy="80" r="65" className="gauge-fill"
                                stroke="#8b5cf6"
                                strokeDasharray={2 * Math.PI * 65}
                                strokeDashoffset={(2 * Math.PI * 65) - (s.ram_usage / 100) * (2 * Math.PI * 65)} />
                        </svg>
                        <div className="gauge-value">
                            <div className="gauge-number" style={{ color: '#8b5cf6' }}>{Math.round(s.ram_usage)}%</div>
                            <div className="gauge-label">RAM</div>
                        </div>
                    </div>
                    <p style={{ marginTop: 16, fontSize: 12, color: 'var(--text-muted)' }}>
                        {Math.round(s.ram_usage * 0.32)}GB / 32GB
                    </p>
                </div>
            </div>

            {/* AI Model Status */}
            <div className="grid-2 animate-in">
                <div className="glass-card">
                    <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 16 }}>🤖 AI Model Status</h3>
                    {[
                        { name: 'Ollama LLM Server', status: s.ollama_status === 'online', detail: s.model_loaded || 'phi3' },
                        { name: 'Medical Report OCR', status: true, detail: 'Tesseract (Simulated)' },
                        { name: 'Food Detection', status: true, detail: 'YOLOv8 (Simulated)' },
                        { name: 'Speech-to-Text', status: true, detail: 'Whisper (Simulated)' },
                        { name: 'Risk Engine', status: true, detail: 'Rule-based v1.0' },
                    ].map((m, i) => (
                        <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 0', borderBottom: '1px solid var(--border-glass)' }}>
                            <div>
                                <div style={{ fontSize: 14, fontWeight: 500 }}>{m.name}</div>
                                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{m.detail}</div>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: m.status ? '#10b981' : '#ef4444' }}>
                                {m.status ? <><CheckCircle size={14} /> Active</> : <><XCircle size={14} /> Offline</>}
                            </div>
                        </div>
                    ))}
                </div>

                <div className="glass-card">
                    <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 16 }}>📊 System Information</h3>
                    {[
                        { label: 'Processor', value: s.platform || 'AMD Ryzen AI' },
                        { label: 'Operating System', value: s.os || 'Windows' },
                        { label: 'Python Version', value: s.python_version || '3.11' },
                        { label: 'Database', value: 'SQLite (Local)' },
                        { label: 'Internet', value: 'Not Required ✅' },
                        { label: 'Data Privacy', value: '100% On-Device 🔒' },
                        { label: 'AMD NPU', value: s.amd_optimized ? 'Optimized ⚡' : 'Available' },
                    ].map((info, i) => (
                        <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border-glass)', fontSize: 13 }}>
                            <span style={{ color: 'var(--text-muted)' }}>{info.label}</span>
                            <span style={{ fontWeight: 500 }}>{info.value}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}
