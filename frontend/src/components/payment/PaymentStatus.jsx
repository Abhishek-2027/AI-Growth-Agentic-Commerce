const STATUS_CONFIG = {
  CREATED: { color: 'badge-info', icon: '🔵', label: 'Created' },
  POLICY_APPROVED: { color: 'badge-success', icon: '✅', label: 'Policy Approved' },
  AWAITING_USER_APPROVAL: { color: 'badge-warning', icon: '⏳', label: 'Awaiting Approval' },
  APPROVED: { color: 'badge-success', icon: '✓', label: 'Approved' },
  RAZORPAY_ORDER_CREATED: { color: 'badge-info', icon: '💳', label: 'Order Created' },
  PAYMENT_PENDING: { color: 'badge-warning', icon: '⏳', label: 'Payment Pending' },
  PAYMENT_FAILED: { color: 'badge-error', icon: '❌', label: 'Payment Failed' },
  PAYMENT_VERIFIED: { color: 'badge-success', icon: '✅', label: 'Payment Verified' },
  COMPLETED: { color: 'badge-success', icon: '🎉', label: 'Completed' },
  CANCELLED: { color: 'badge-error', icon: '🚫', label: 'Cancelled' },
}

export default function PaymentStatus({ order }) {
  if (!order) return null
  const cfg = STATUS_CONFIG[order.status] || { color: 'badge-info', icon: '🔵', label: order.status }

  return (
    <div className="glass-card p-5 animate-fade-in">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-white">Payment Status</h3>
        <span className={cfg.color}>{cfg.icon} {cfg.label}</span>
      </div>
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-slate-400">Product</span>
          <span className="text-white font-medium">{order.product_name}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Amount</span>
          <span className="text-white font-bold">₹{order.amount?.toLocaleString('en-IN')}</span>
        </div>
        {order.razorpay_payment_id && (
          <div className="flex justify-between">
            <span className="text-slate-400">Payment ID</span>
            <span className="text-emerald-400 text-xs font-mono">{order.razorpay_payment_id}</span>
          </div>
        )}
        <div className="flex justify-between">
          <span className="text-slate-400">Order ID</span>
          <span className="text-slate-300 text-xs font-mono">{order._id?.slice(-8)}</span>
        </div>
      </div>
    </div>
  )
}
