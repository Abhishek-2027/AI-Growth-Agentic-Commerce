import { useEffect, useState } from 'react'
import Header from '../components/layout/Header'
import { getOrders } from '../api/orderApi'

const STATUS_COLOR = {
  COMPLETED: 'badge-success',
  PAYMENT_VERIFIED: 'badge-success',
  PAYMENT_FAILED: 'badge-error',
  CANCELLED: 'badge-error',
  PAYMENT_PENDING: 'badge-warning',
  RAZORPAY_ORDER_CREATED: 'badge-warning',
  APPROVED: 'badge-info',
  AWAITING_USER_APPROVAL: 'badge-warning',
}

export default function OrdersPage() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getOrders().then((d) => { setOrders(d.orders || []); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="animate-pulse space-y-3">{[1,2,3].map(i => <div key={i} className="glass-card h-20" />)}</div>

  return (
    <div>
      <Header title="Orders" subtitle="All purchase orders with full state machine tracking." />

      {orders.length === 0 ? (
        <div className="text-center py-16 text-slate-500">
          <div className="text-5xl mb-3">📦</div>
          <p>No orders yet. Use the AI Shopping Agent to make a purchase!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {orders.map((o) => (
            <div key={o._id} className="glass-card p-5 flex flex-wrap items-center gap-4 animate-fade-in hover:border-brand-500/30 transition-colors">
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-slate-900 truncate">{o.product_name}</p>
                <p className="text-xs text-slate-500 font-mono mt-0.5">{o._id}</p>
              </div>
              <div className="text-center">
                <p className="text-xl font-bold text-slate-900">₹{o.amount?.toLocaleString('en-IN')}</p>
                <p className="text-xs text-slate-500">×{o.quantity}</p>
              </div>
              <span className={STATUS_COLOR[o.status] || 'badge-info'}>{o.status?.replace(/_/g, ' ')}</span>
              <div className="text-right">
                <p className="text-xs text-slate-500">{new Date(o.created_at).toLocaleDateString('en-IN')}</p>
                {o.razorpay_payment_id && (
                  <p className="text-xs text-emerald-600 font-mono">{o.razorpay_payment_id.slice(0, 12)}...</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
