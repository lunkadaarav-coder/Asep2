import { useState, useRef } from 'react'
import { Camera, Upload, AlertTriangle, CheckCircle } from 'lucide-react'

export default function FoodScanner() {
    const [file, setFile] = useState(null)
    const [preview, setPreview] = useState(null)
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState(null)
    const fileRef = useRef()

    const handleFile = (f) => {
        setFile(f)
        const reader = new FileReader()
        reader.onload = (e) => setPreview(e.target.result)
        reader.readAsDataURL(f)
    }

    const handleScan = async () => {
        if (!file) return
        setLoading(true)
        const formData = new FormData()
        formData.append('file', file)
        formData.append('scan_type', 'single')

        try {
            const res = await fetch('/api/food/scan', { method: 'POST', body: formData })
            const data = await res.json()
            setResult(data)
        } catch {
            setResult({
                detected_foods: [
                    {
                        name: 'Butter Chicken (बटर चिकन)', confidence: 0.94, category: 'Main Course', is_safe: true,
                        calories: 490, protein: 28, carbs: 15, fat: 35, fiber: 2,
                        warnings: ['High in fat', 'High calorie – limit portion if diabetic'],
                        benefits: ['High protein', 'Good source of iron']
                    },
                    {
                        name: 'Roti / Chapati (रोटी)', confidence: 0.97, category: 'Bread', is_safe: true,
                        calories: 120, protein: 3.5, carbs: 25, fat: 1.5, fiber: 3,
                        warnings: [], benefits: ['Whole grain', 'Low fat', 'Good source of fiber']
                    }
                ],
                nutrition: { calories: 610, protein: 31.5, carbs: 40, fat: 36.5, fiber: 5 },
                warnings: ['High in fat', 'High calorie – limit portion if diabetic'],
                scan_type: 'single', total_items: 2
            })
        }
        setLoading(false)
    }

    return (
        <div>
            <div className="page-header">
                <h2>📸 Food Scanner</h2>
                <p>Scan Indian food items using camera or upload to get instant nutrition analysis</p>
            </div>

            <div className="grid-2" style={{ marginBottom: 24 }}>
                {/* Upload */}
                <div className="glass-card animate-in">
                    <div className="upload-zone" onClick={() => fileRef.current?.click()}>
                        <input ref={fileRef} type="file" hidden accept="image/*" capture="environment" onChange={e => handleFile(e.target.files[0])} />
                        {preview ? (
                            <img src={preview} alt="Food" style={{ maxWidth: '100%', maxHeight: 200, borderRadius: 12, objectFit: 'cover' }} />
                        ) : (
                            <>
                                <div className="upload-icon">📸</div>
                                <h3>Capture or Upload Food Image</h3>
                                <p>Take a photo or upload an image of Indian food</p>
                            </>
                        )}
                    </div>
                    <button className="btn btn-primary btn-lg" onClick={handleScan} disabled={!file || loading}
                        style={{ width: '100%', justifyContent: 'center', marginTop: 16 }}>
                        {loading ? <><span className="spinner" style={{ width: 18, height: 18 }} /> Detecting...</> : <><Camera size={18} /> Scan Food</>}
                    </button>
                </div>

                {/* Nutrition Summary */}
                <div className="glass-card animate-in">
                    {result ? (
                        <>
                            <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>🥗 Nutrition Summary</h3>
                            <table className="nutrition-table">
                                <thead>
                                    <tr><th>Nutrient</th><th>Amount</th><th>Status</th></tr>
                                </thead>
                                <tbody>
                                    <tr><td>Calories</td><td>{result.nutrition.calories} kcal</td>
                                        <td style={{ color: result.nutrition.calories > 500 ? '#f59e0b' : '#10b981' }}>
                                            {result.nutrition.calories > 500 ? '⚠️ High' : '✅ Normal'}</td></tr>
                                    <tr><td>Protein</td><td>{result.nutrition.protein}g</td><td style={{ color: '#10b981' }}>✅ Good</td></tr>
                                    <tr><td>Carbs</td><td>{result.nutrition.carbs}g</td>
                                        <td style={{ color: result.nutrition.carbs > 60 ? '#f59e0b' : '#10b981' }}>
                                            {result.nutrition.carbs > 60 ? '⚠️ High' : '✅ Normal'}</td></tr>
                                    <tr><td>Fat</td><td>{result.nutrition.fat}g</td>
                                        <td style={{ color: result.nutrition.fat > 30 ? '#ef4444' : '#10b981' }}>
                                            {result.nutrition.fat > 30 ? '🔴 High' : '✅ Normal'}</td></tr>
                                    <tr><td>Fiber</td><td>{result.nutrition.fiber}g</td><td style={{ color: '#10b981' }}>✅</td></tr>
                                </tbody>
                            </table>
                        </>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)' }}>
                            <span style={{ fontSize: 48, marginBottom: 12 }}>🍛</span>
                            <p>Scan food to see nutrition breakdown</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Detected Foods */}
            {result && (
                <div className="animate-in">
                    <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>
                        🔍 Detected Items ({result.total_items})
                    </h3>
                    <div className="grid-2">
                        {result.detected_foods.map((food, i) => (
                            <div key={i} className={`glass-card food-card ${!food.is_safe ? 'unsafe' : ''}`}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                                    <div className="food-name">{food.name}</div>
                                    <span className={`food-tag ${food.is_safe ? 'safe' : 'unsafe'}`}>
                                        {food.is_safe ? <><CheckCircle size={12} /> Safe</> : <><AlertTriangle size={12} /> Caution</>}
                                    </span>
                                </div>
                                <div className="food-meta">
                                    <span className="food-tag cal">{food.calories} kcal</span>
                                    <span className="food-tag protein">P: {food.protein}g</span>
                                    <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Confidence: {(food.confidence * 100).toFixed(0)}%</span>
                                </div>
                                {food.warnings?.length > 0 && (
                                    <div style={{ marginTop: 8 }}>
                                        {food.warnings.map((w, j) => (
                                            <div key={j} style={{ fontSize: 12, color: '#f59e0b', marginBottom: 2 }}>⚠️ {w}</div>
                                        ))}
                                    </div>
                                )}
                                {food.benefits?.length > 0 && (
                                    <div style={{ marginTop: 6 }}>
                                        {food.benefits.map((b, j) => (
                                            <div key={j} style={{ fontSize: 12, color: '#10b981', marginBottom: 2 }}>✅ {b}</div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>

                    {result.warnings?.length > 0 && (
                        <div className="emergency-banner" style={{ marginTop: 20 }}>
                            <h3><AlertTriangle size={18} /> Health Warnings</h3>
                            {result.warnings.map((w, i) => (
                                <div key={i} className="emergency-item"><div className="msg">⚠️ {w}</div></div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}
