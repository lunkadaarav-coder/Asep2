import { useRef, useState } from 'react'
import { AlertTriangle, CheckCircle2, Upload } from 'lucide-react'

export default function MealScanner() {
    const [file, setFile] = useState(null)
    const [preview, setPreview] = useState(null)
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState(null)
    const [error, setError] = useState('')
    const fileRef = useRef()

    const handleFile = (selected) => {
        if (!selected) return
        setResult(null)
        setError('')
        setFile(selected)

        const reader = new FileReader()
        reader.onload = (e) => setPreview(e.target.result)
        reader.readAsDataURL(selected)
    }

    const handleAnalyze = async () => {
        if (!file) {
            setError('Please upload an image first.')
            return
        }

        setLoading(true)
        setError('')
        setResult(null)

        const formData = new FormData()
        formData.append('file', file)

        try {
            const response = await fetch('/api/scan-meal', {
                method: 'POST',
                body: formData,
            })
            const data = await response.json()

            if (!response.ok) {
                throw new Error(data.detail || 'Meal analysis failed')
            }

            setResult(data)
        } catch (err) {
            setError(err.message || 'Unable to analyze meal right now.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div>
            <div className="page-header">
                <h2>🍽️ Meal Scanner</h2>
                <p>Upload a meal photo to identify food using offline EfficientNet AI.</p>
            </div>

            <div className="grid-2" style={{ marginBottom: 20 }}>
                <div className="glass-card animate-in">
                    <div className="upload-zone" onClick={() => fileRef.current?.click()}>
                        <input
                            ref={fileRef}
                            type="file"
                            hidden
                            accept="image/*"
                            capture="environment"
                            onChange={(e) => handleFile(e.target.files?.[0])}
                        />
                        {preview ? (
                            <img src={preview} alt="Meal preview" style={{ maxWidth: '100%', maxHeight: 240, borderRadius: 12, objectFit: 'cover' }} />
                        ) : (
                            <>
                                <div className="upload-icon">🍛</div>
                                <h3>Upload Meal Photo</h3>
                                <p>Tap to capture or upload from gallery</p>
                            </>
                        )}
                    </div>

                    <button
                        className="btn btn-primary btn-lg"
                        style={{ width: '100%', justifyContent: 'center', marginTop: 16 }}
                        onClick={handleAnalyze}
                        disabled={!file || loading}
                    >
                        {loading ? <><span className="spinner" style={{ width: 18, height: 18 }} /> Analyzing Meal...</> : <><Upload size={18} /> Analyze Meal</>}
                    </button>

                    {error && (
                        <div className="emergency-item" style={{ marginTop: 12 }}>
                            <div className="msg">⚠️ {error}</div>
                        </div>
                    )}
                </div>

                <div className="glass-card animate-in">
                    {!result ? (
                        <div style={{ textAlign: 'center', color: 'var(--text-muted)', paddingTop: 28 }}>
                            <div style={{ fontSize: 54 }}>🤖</div>
                            <p style={{ marginTop: 10 }}>Prediction results will appear here.</p>
                        </div>
                    ) : (
                        <>
                            <h3 style={{ marginBottom: 12 }}>Meal Analysis Result</h3>
                            <div style={{ fontSize: 22, fontWeight: 700, marginBottom: 8 }}>
                                🍽 Predicted Food: <span style={{ color: 'var(--primary)' }}>{result.predicted_food}</span>
                            </div>
                            <div style={{ marginBottom: 8, fontSize: 16 }}>🟢 Confidence: {result.confidence}%</div>
                            <div style={{ marginBottom: 12 }}>
                                <span
                                    className="food-tag"
                                    style={{
                                        background: result.status === 'Confident' ? 'rgba(16,185,129,0.12)' : 'rgba(245,158,11,0.15)',
                                        color: result.status === 'Confident' ? '#10b981' : '#f59e0b',
                                        border: `1px solid ${result.status === 'Confident' ? 'rgba(16,185,129,0.4)' : 'rgba(245,158,11,0.4)'}`,
                                    }}
                                >
                                    {result.status === 'Confident' ? <CheckCircle2 size={13} /> : <AlertTriangle size={13} />}
                                    ⚠ Status: {result.status}
                                </span>
                            </div>

                            {result.status === 'Uncertain' && (
                                <div className="emergency-item" style={{ marginBottom: 12, borderColor: 'rgba(245,158,11,0.5)' }}>
                                    <div className="msg" style={{ color: '#f59e0b' }}>Food could not be confidently identified.</div>
                                </div>
                            )}

                            <h4 style={{ marginBottom: 8 }}>📊 Top 3 Predictions</h4>
                            <div>
                                {result.top_3?.map((item, idx) => (
                                    <div key={item.label} style={{ padding: '8px 10px', borderRadius: 8, background: 'rgba(148,163,184,0.08)', marginBottom: 8, fontSize: 14 }}>
                                        #{idx + 1} {item.label} — {item.confidence}%
                                    </div>
                                ))}
                            </div>

                            {result.health_flags?.length > 0 && (
                                <>
                                    <h4 style={{ marginTop: 10, marginBottom: 8 }}>🚨 Health Flags</h4>
                                    {result.health_flags.map((flag) => (
                                        <div key={flag} style={{ fontSize: 14, color: '#ef4444', marginBottom: 6 }}>
                                            • {flag}
                                        </div>
                                    ))}
                                </>
                            )}
                        </>
                    )}
                </div>
            </div>
        </div>
    )
}
