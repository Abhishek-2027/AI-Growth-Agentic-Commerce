import { useEffect, useState } from 'react'
import Header from '../components/layout/Header'
import { getProducts } from '../api/productApi'
import { getOrders } from '../api/orderApi'
import { getAllAudits } from '../api/auditApi'

function StatCard({ icon, label, value, sub, color = 'brand' }) {
  return (
    <div className={`stat-card group`}>
      <div className="flex items-center justify-between">
        <span className="text-2xl">{icon}</span>
        <span className={`text-xs font-medium text-${color}-400 bg-${color}-500/10 px-2 py-1 rounded-full`}>Live</span>
      </div>
      <div>
        <p className="text-3xl font-bold text-white">{value}</p>
        <p className="text-sm font-medium text-slate-300">{label}</p>
        {sub && <p className="text-xs text-slate-500 mt-0.5">{sub}</p>}
      </div>
    </div>
  )
}

const PRINCIPLES = [
  { icon: '🤖', title: 'AI Decides', desc: 'Agent understands intent, searches catalog, and recommends products' },
  { icon: '⚖️', title: 'Policy Validates', desc: 'Deterministic code checks budget, stock, quantity — no LLM override' },
  { icon: '👤', title: 'Human Approves', desc: 'You must explicitly approve before any money moves' },
  { icon: '💳', title: 'Payment Executes', desc: 'Razorpay Test Mode with backend HMAC verification' },
  { icon: '📋', title: 'Audit Records', desc: 'Every event logged with actor, reason, and timestamp' },
]

export default function Dashboard() {
  const [stats, setStats] = useState({ products: 0, orders: 0, completed: 0, events: 0 })

  useEffect(() => {
    Promise.all([getProducts(100), getOrders(), getAllAudits(200)]).then(
      ([p, o, a]) => setStats({
        products: p.count || 0,
        orders: o.count || 0,
        completed: o.orders?.filter((x) => x.status === 'COMPLETED').length || 0,
        events: a.count || 0,
      })
    ).catch(() => {})
  }, [])

  return (
    <div>
      <Header
        title="AgentCart Dashboard"
        subtitle="Safe AI-powered agentic commerce platform — AI proposes, policy validates, you approve."
      />

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard icon="🛍️" label="Products" value={stats.products} sub="In catalog" />
        <StatCard icon="📦" label="Orders" value={stats.orders} sub="All time" />
        <StatCard icon="✅" label="Completed" value={stats.completed} sub="Verified payments" color="emerald" />
        <StatCard icon="📋" label="Audit Events" value={stats.events} sub="Logged actions" color="violet" />
      </div>

      {/* Architecture principles */}
      <div className="glass-card p-6 mb-6">
        <h2 className="font-bold text-white mb-4 flex items-center gap-2">
          <span>🏗️</span> Safety Architecture
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {PRINCIPLES.map(({ icon, title, desc }) => (
            <div key={title} className="bg-white/5 border border-white/10 rounded-xl p-4 hover:border-brand-500/30 transition-colors">
              <span className="text-2xl block mb-2">{icon}</span>
              <h3 className="font-semibold text-white text-sm mb-1">{title}</h3>
              <p className="text-xs text-slate-500 leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Quick start */}
      <div className="glass-card p-6 border-brand-500/20 bg-brand-500/5">
        <h2 className="font-bold text-brand-300 mb-2">🚀 Demo Flow</h2>
        <p className="text-slate-400 text-sm mb-4">Try the complete end-to-end agentic commerce experience:</p>
        <div className="flex flex-wrap gap-2">
          {[
            '1. Go to AI Shopping Agent',
            '2. Type your shopping request',
            '3. Agent searches & recommends',
            '4. Policy check runs automatically',
            '5. Review & approve payment',
            '6. Razorpay Test Mode checkout',
            '7. Backend verifies payment',
            '8. Check Audit Trail',
          ].map((step, i) => (
            <span key={i} className="text-xs bg-white/5 border border-white/10 text-slate-300 px-3 py-1.5 rounded-full">
              {step}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
