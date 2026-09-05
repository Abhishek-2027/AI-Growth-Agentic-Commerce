import { useEffect, useState } from 'react'
import Header from '../components/layout/Header'
import { getProducts } from '../api/productApi'
import { getOrders } from '../api/orderApi'
import { getAllAudits } from '../api/auditApi'
import PersonalizedRecommendations from '../components/recommendations/PersonalizedRecommendations'
import { useNavigate } from 'react-router-dom'

function StatCard({ icon, label, value, sub, color = 'brand' }) {
  return (
    <div className={`stat-card group`}>
      <div className="flex items-center justify-between">
        <span className="text-2xl">{icon}</span>
        <span className={`text-xs font-medium text-${color}-700 bg-${color}-50 px-2 py-1 rounded-full border border-${color}-200`}>Live</span>
      </div>
      <div>
        <p className="text-3xl font-bold text-slate-900">{value}</p>
        <p className="text-sm font-medium text-slate-600">{label}</p>
        {sub && <p className="text-xs text-slate-400 mt-0.5">{sub}</p>}
      </div>
    </div>
  )
}

export default function Dashboard() {
  const navigate = useNavigate()
  const [stats, setStats] = useState({ products: 0, orders: 0, completed: 0, events: 0 })
  const [recommendations, setRecommendations] = useState(null)

  useEffect(() => {
    Promise.all([getProducts(100), getOrders(), getAllAudits(200)]).then(
      ([p, o, a]) => setStats({
        products: p.count || 0,
        orders: o.count || 0,
        completed: o.orders?.filter((x) => x.status === 'COMPLETED').length || 0,
        events: a.count || 0,
      })
    ).catch(() => {})

    import('../api/recommendationApi').then(({ getDashboardRecommendations }) => {
      let sid = localStorage.getItem('agent_session_id')
      if (!sid) {
        import('uuid').then(({ v4 }) => {
          sid = v4()
          localStorage.setItem('agent_session_id', sid)
          getDashboardRecommendations(sid).then(setRecommendations)
        })
      } else {
        getDashboardRecommendations(sid).then(setRecommendations)
      }
    }).catch(console.error)
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

      {/* Recommendations */}
      <div className="space-y-8 mt-8 pb-8">
        <PersonalizedRecommendations
          products={recommendations?.recommended_for_you}
          title="Recommended For You"
          subtitle="Based on your recent activity and preferences"
          onSelectProduct={(p) => navigate('/agent')}
        />
        
        <PersonalizedRecommendations
          products={recommendations?.recent_activity}
          title="Based on Your Recent Activity"
          subtitle="Similar to what you've viewed recently"
          onSelectProduct={(p) => navigate('/agent')}
        />

        <PersonalizedRecommendations
          products={recommendations?.complements_purchases}
          title="Complements Your Recent Purchases"
          subtitle="Frequently bought together"
          onSelectProduct={(p) => navigate('/agent')}
        />
      </div>
    </div>
  )
}

