import { useEffect, useState } from 'react'
import Header from '../components/layout/Header'
import AuditTimeline from '../components/audit/AuditTimeline'
import { getAllAudits } from '../api/auditApi'

export default function AuditPage() {
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(false)

  const load = async () => {
    try {
      const data = await getAllAudits(200)
      setEvents(data.events || [])
    } catch {}
    setLoading(false)
  }

  useEffect(() => { load() }, [])
  useEffect(() => {
    if (!autoRefresh) return
    const t = setInterval(load, 3000)
    return () => clearInterval(t)
  }, [autoRefresh])

  return (
    <div>
      <Header title="Audit Trail" subtitle="Complete explainable record of every AI decision, policy check, and payment event." />

      <div className="flex items-center justify-between mb-6">
        <p className="text-slate-400 text-sm">{events.length} events recorded</p>
        <div className="flex gap-2">
          <button
            className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${autoRefresh ? 'bg-emerald-500/20 border-emerald-500/30 text-emerald-400' : 'glass-card text-slate-400'}`}
            onClick={() => setAutoRefresh((p) => !p)}
          >
            {autoRefresh ? '⏸ Auto Refresh On' : '▶ Auto Refresh'}
          </button>
          <button className="btn-secondary text-xs" onClick={load}>↻ Refresh</button>
        </div>
      </div>

      {/* Legend */}
      <div className="glass-card p-4 mb-6">
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Actor Legend</p>
        <div className="flex flex-wrap gap-4">
          {[
            { label: '🤖 Agent', desc: 'LangGraph AI decisions' },
            { label: '⚖️ Policy', desc: 'Deterministic validation' },
            { label: '👤 User', desc: 'Human approvals' },
            { label: '💳 Payment', desc: 'Razorpay operations' },
            { label: '🛡️ Guardrail', desc: 'Safety filters' },
            { label: '⚙️ System', desc: 'Platform events' },
          ].map(({ label, desc }) => (
            <div key={label} className="flex items-center gap-2">
              <span className="text-sm">{label}</span>
              <span className="text-xs text-slate-500">{desc}</span>
            </div>
          ))}
        </div>
      </div>

      <AuditTimeline events={events} loading={loading} emptyMessage="No audit events yet. Run the AI Shopping Agent to see events appear here." />
    </div>
  )
}
