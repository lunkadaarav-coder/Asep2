import { useState } from 'react'
import { Users, UserPlus, FileText, Search, MapPin, Phone } from 'lucide-react'

const initialPatients = [
    { id: 1, name: 'Ramesh Kumar', age: 45, gender: 'Male', blood_group: 'B+', village: 'Chandpur', report_count: 3, risk: 78 },
    { id: 2, name: 'Sunita Devi', age: 38, gender: 'Female', blood_group: 'O+', village: 'Chandpur', report_count: 2, risk: 35 },
    { id: 3, name: 'Mohan Lal', age: 62, gender: 'Male', blood_group: 'A+', village: 'Ramgarh', report_count: 5, risk: 65 },
    { id: 4, name: 'Geeta Bai', age: 55, gender: 'Female', blood_group: 'B-', village: 'Ramgarh', report_count: 1, risk: 42 },
    { id: 5, name: 'Raju Singh', age: 28, gender: 'Male', blood_group: 'AB+', village: 'Devpur', report_count: 1, risk: 15 },
]

export default function RuralMode() {
    const [patients, setPatients] = useState(initialPatients)
    const [search, setSearch] = useState('')
    const [showAdd, setShowAdd] = useState(false)
    const [selectedPatient, setSelectedPatient] = useState(null)
    const [newPatient, setNewPatient] = useState({ name: '', age: '', gender: 'male', blood_group: '', village: '', phone: '' })

    const filtered = patients.filter(p => p.name.toLowerCase().includes(search.toLowerCase()) || p.village.toLowerCase().includes(search.toLowerCase()))

    const handleAdd = async () => {
        if (!newPatient.name) return
        try {
            const res = await fetch('/api/patients/create', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ...newPatient, asha_worker_id: 'ASHA001' })
            })
            const data = await res.json()
            setPatients(prev => [{ ...data, report_count: 0, risk: 0 }, ...prev])
        } catch {
            setPatients(prev => [{ id: Date.now(), ...newPatient, age: +newPatient.age, report_count: 0, risk: 0 }, ...prev])
        }
        setNewPatient({ name: '', age: '', gender: 'male', blood_group: '', village: '', phone: '' })
        setShowAdd(false)
    }

    const getRiskColor = (r) => r >= 60 ? '#ef4444' : r >= 30 ? '#f59e0b' : '#10b981'

    return (
        <div>
            <div className="page-header">
                <h2>🏥 Rural ASHA Worker Mode</h2>
                <p>Manage multiple patient profiles for village health camps and door-to-door visits</p>
            </div>

            {/* Stats bar */}
            <div className="grid-4 animate-in" style={{ marginBottom: 20 }}>
                {[
                    { icon: '👥', label: 'Total Patients', value: patients.length, color: '#06b6d4' },
                    { icon: '🏘️', label: 'Villages', value: [...new Set(patients.map(p => p.village))].length, color: '#10b981' },
                    { icon: '📄', label: 'Total Reports', value: patients.reduce((a, p) => a + p.report_count, 0), color: '#8b5cf6' },
                    { icon: '⚠️', label: 'High Risk', value: patients.filter(p => p.risk >= 60).length, color: '#ef4444' },
                ].map((s, i) => (
                    <div key={i} className="glass-card stat-card" style={{ padding: 16 }}>
                        <div style={{ fontSize: 18 }}>{s.icon}</div>
                        <div className="stat-value" style={{ color: s.color, fontSize: 22 }}>{s.value}</div>
                        <div className="stat-label">{s.label}</div>
                    </div>
                ))}
            </div>

            {/* Search + Add */}
            <div className="animate-in" style={{ display: 'flex', gap: 12, marginBottom: 20 }}>
                <div style={{ flex: 1, position: 'relative' }}>
                    <Search size={16} style={{ position: 'absolute', left: 12, top: 12, color: 'var(--text-muted)' }} />
                    <input className="form-input" placeholder="Search patients by name or village..."
                        style={{ paddingLeft: 36, width: '100%' }} value={search} onChange={e => setSearch(e.target.value)} />
                </div>
                <button className="btn btn-primary" onClick={() => setShowAdd(!showAdd)}>
                    <UserPlus size={16} /> Add Patient
                </button>
            </div>

            {/* Add Form */}
            {showAdd && (
                <div className="glass-card animate-in" style={{ marginBottom: 20 }}>
                    <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 16 }}>➕ Register New Patient</h3>
                    <div className="grid-3" style={{ gap: 12, marginBottom: 12 }}>
                        <div className="form-group">
                            <label className="form-label">Full Name *</label>
                            <input className="form-input" placeholder="Patient name" value={newPatient.name} onChange={e => setNewPatient({ ...newPatient, name: e.target.value })} />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Age</label>
                            <input type="number" className="form-input" placeholder="Age" value={newPatient.age} onChange={e => setNewPatient({ ...newPatient, age: e.target.value })} />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Gender</label>
                            <select className="form-select" value={newPatient.gender} onChange={e => setNewPatient({ ...newPatient, gender: e.target.value })}>
                                <option value="male">Male</option>
                                <option value="female">Female</option>
                            </select>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Blood Group</label>
                            <input className="form-input" placeholder="e.g. B+" value={newPatient.blood_group} onChange={e => setNewPatient({ ...newPatient, blood_group: e.target.value })} />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Village</label>
                            <input className="form-input" placeholder="Village name" value={newPatient.village} onChange={e => setNewPatient({ ...newPatient, village: e.target.value })} />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Phone</label>
                            <input className="form-input" placeholder="Phone number" value={newPatient.phone} onChange={e => setNewPatient({ ...newPatient, phone: e.target.value })} />
                        </div>
                    </div>
                    <div style={{ display: 'flex', gap: 8 }}>
                        <button className="btn btn-primary" onClick={handleAdd}>✅ Register Patient</button>
                        <button className="btn btn-outline" onClick={() => setShowAdd(false)}>Cancel</button>
                    </div>
                </div>
            )}

            {/* Patient List */}
            <div className="glass-card animate-in">
                <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 16 }}>📋 Patient Registry ({filtered.length})</h3>
                <table className="nutrition-table" style={{ width: '100%' }}>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Age/Gender</th>
                            <th>Village</th>
                            <th>Blood Group</th>
                            <th>Reports</th>
                            <th>Risk</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filtered.map(p => (
                            <tr key={p.id}>
                                <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{p.name}</td>
                                <td>{p.age} / {p.gender}</td>
                                <td><MapPin size={12} style={{ display: 'inline', verticalAlign: 'middle' }} /> {p.village}</td>
                                <td>{p.blood_group}</td>
                                <td>{p.report_count}</td>
                                <td>
                                    <span style={{ padding: '3px 10px', borderRadius: 10, fontSize: 12, fontWeight: 600, background: `${getRiskColor(p.risk)}18`, color: getRiskColor(p.risk) }}>
                                        {p.risk}%
                                    </span>
                                </td>
                                <td>
                                    <button className="btn btn-outline btn-sm" onClick={() => setSelectedPatient(p)}>
                                        <FileText size={12} /> View
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Patient Detail Modal */}
            {selectedPatient && (
                <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 200 }}
                    onClick={() => setSelectedPatient(null)}>
                    <div className="glass-card" style={{ maxWidth: 480, width: '90%' }} onClick={e => e.stopPropagation()}>
                        <h3 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16 }}>👤 {selectedPatient.name}</h3>
                        <div className="grid-2" style={{ gap: 12, marginBottom: 16 }}>
                            <div><span style={{ color: 'var(--text-muted)', fontSize: 12 }}>Age:</span> {selectedPatient.age}</div>
                            <div><span style={{ color: 'var(--text-muted)', fontSize: 12 }}>Gender:</span> {selectedPatient.gender}</div>
                            <div><span style={{ color: 'var(--text-muted)', fontSize: 12 }}>Blood Group:</span> {selectedPatient.blood_group}</div>
                            <div><span style={{ color: 'var(--text-muted)', fontSize: 12 }}>Village:</span> {selectedPatient.village}</div>
                        </div>
                        <div style={{ display: 'flex', gap: 8 }}>
                            <button className="btn btn-primary btn-sm" onClick={() => { setSelectedPatient(null); }}>📄 Scan Report</button>
                            <button className="btn btn-outline btn-sm" onClick={() => setSelectedPatient(null)}>Close</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
