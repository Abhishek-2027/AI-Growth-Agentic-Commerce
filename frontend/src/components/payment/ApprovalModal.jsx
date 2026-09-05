import { useState } from 'react'
import { approveProposal, rejectProposal } from '../../api/orderApi'
import { createPaymentOrder, verifyPayment, cancelOrder } from '../../api/paymentApi'

const RAZORPAY_KEY = import.meta.env.VITE_RAZORPAY_KEY_ID

function loadRazorpayScript() {
  return new Promise((resolve) => {
    if (document.getElementById('razorpay-script')) return resolve(true)
    const s = document.createElement('script')
    s.id = 'razorpay-script'
    s.src = 'https://checkout.razorpay.com/v1/checkout.js'
    s.onload = () => resolve(true)
    s.onerror = () => resolve(false)
    document.body.appendChild(s)
  })
}

export default function ApprovalModal({ proposal, sessionId, onApproved, onRejected, onClose }) {
  const [loading, setLoading] = useState(false)
  const [paymentStatus, setPaymentStatus] = useState(null)
  const [error, setError] = useState(null)
  const [orderId, setOrderId] = useState(null)

  if (!proposal) return null

  const policy = proposal.policy_result || {}
  const policyPassed = policy.approved

  const handleApprove = async () => {
    setLoading(true)
    setError(null)
    try {
      // 1. Record user approval in backend
      await approveProposal(proposal._id, sessionId)

      // 2. Create Razorpay order (backend reads price from MongoDB)
      const checkout = await createPaymentOrder(proposal._id, sessionId)
      setOrderId(checkout.order_id)

      // 3. Load Razorpay SDK
      const loaded = await loadRazorpayScript()
      if (!loaded) throw new Error('Failed to load Razorpay SDK')

      // 4. Open Razorpay Checkout
      const rzp = new window.Razorpay({
        key: checkout.razorpay_key_id, // backend returns public key only
        amount: checkout.amount,
        currency: checkout.currency,
        name: 'AgentCart',
        description: checkout.product_name,
        order_id: checkout.razorpay_order_id,
        handler: async (response) => {
          // 5. Send to backend for HMAC verification — never trust frontend callback alone
          try {
            await verifyPayment({
              order_id: checkout.order_id,
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            })
            setPaymentStatus('success')
            onApproved?.(checkout.order_id)
          } catch (verifyErr) {
            setPaymentStatus('failed')
            setError(verifyErr.message)
          }
          setLoading(false)
        },
        prefill: { name: 'Demo User', email: 'demo@agentcart.ai' },
        theme: { color: '#6366f1' },
        modal: {
          ondismiss: () => {
            setPaymentStatus('cancelled')
            setLoading(false)
          },
        },
      })
      rzp.open()
    } catch (err) {
      setError(err.message)
      setPaymentStatus('failed')
      setLoading(false)
    }
  }

  const handleReject = async () => {
    try {
      await rejectProposal(proposal._id, sessionId)
      onRejected?.()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleRetry = async () => {
    if (!orderId) return
    setPaymentStatus(null)
    setError(null)
    await handleApprove()
  }

  const handleCancel = async () => {
    if (orderId) await cancelOrder(orderId).catch(() => {})
    const msg = paymentStatus === 'failed'
      ? '❌ Payment failed. Let me know if you want to try again or search for something else.'
      : '❌ Payment cancelled. Let me know if you want to try again or search for something else.'
    onRejected?.(msg)
  }

  // Payment result screens
  if (paymentStatus === 'success') {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm px-4 animate-fade-in">
        <div className="glass-card w-full max-w-md p-8 text-center animate-slide-up">
          <div className="text-6xl mb-4">🎉</div>
          <h2 className="text-2xl font-bold text-emerald-600 mb-2">Payment Successful!</h2>
          <p className="text-slate-600 mb-2">Your order has been placed and verified by the backend.</p>
          <p className="text-xs text-slate-500 mb-6">Order ID: {orderId}</p>
          <button className="btn-success w-full" onClick={onClose}>View Audit Trail</button>
        </div>
      </div>
    )
  }

  if (paymentStatus === 'failed' || paymentStatus === 'cancelled') {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm px-4 animate-fade-in">
        <div className="glass-card w-full max-w-md p-8 animate-slide-up">
          <div className="text-center mb-6">
            <div className="text-5xl mb-4">❌</div>
            <h2 className="text-xl font-bold text-red-600 mb-2">
              {paymentStatus === 'cancelled' ? 'Payment Cancelled' : 'Payment Failed'}
            </h2>
            <p className="text-slate-600 text-sm mb-2">
              The order was <strong>not completed</strong>. No duplicate payment was created.
            </p>
            {error && <p className="text-red-600 text-xs p-3 bg-red-50 rounded-lg border border-red-200">{error}</p>}
          </div>
          <div className="space-y-3">
            <button className="btn-primary w-full" onClick={handleRetry} disabled={loading}>
              {loading ? 'Processing...' : '🔄 Retry Payment'}
            </button>
            <button className="btn-danger w-full" onClick={handleCancel}>Cancel Order</button>
          </div>
        </div>
      </div>
    )
  }

  // Main approval modal
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm px-4 animate-fade-in">
      <div className="glass-card w-full max-w-md p-7 animate-slide-up">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center text-xl">💳</div>
          <div>
            <h2 className="text-lg font-bold text-slate-900">Payment Approval Required</h2>
            <p className="text-xs text-slate-500">Review and confirm your purchase</p>
          </div>
        </div>

        {/* Product info */}
        <div className="bg-slate-100 rounded-xl p-4 mb-4 border border-slate-200">
          <p className="text-xs text-slate-500 mb-1">Product</p>
          <p className="font-semibold text-slate-900">{proposal.product_name}</p>
          <div className="flex items-center justify-between mt-2">
            <span className="text-2xl font-bold text-slate-900">₹{proposal.expected_amount?.toLocaleString('en-IN')}</span>
            <span className="badge-info">×{proposal.quantity}</span>
          </div>
        </div>

        {/* Reason */}
        {proposal.reason && (
          <div className="mb-4">
            <p className="text-xs text-slate-500 mb-1">Why this product</p>
            <p className="text-sm text-slate-600">{proposal.reason}</p>
          </div>
        )}

        {/* Safety checks */}
        <div className="mb-6">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Safety Checks</p>
          {policyPassed ? (
            <div className="space-y-1.5">
              {['Budget validated', 'Stock confirmed', 'Policy approved', 'Approval required'].map((c) => (
                <div key={c} className="flex items-center gap-2 text-sm text-emerald-600">
                  <span>✓</span><span>{c}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600 font-semibold">Policy Check Failed</p>
              {policy.blocked_reasons?.map((r, i) => (
                <p key={i} className="text-xs text-red-600 mt-1">• {r}</p>
              ))}
            </div>
          )}
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-xs text-red-600">{error}</p>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3">
          <button className="btn-secondary flex-1" onClick={handleReject} disabled={loading}>
            ✗ Cancel
          </button>
          <button
            className="btn-success flex-1"
            onClick={handleApprove}
            disabled={loading || !policyPassed}
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                </svg>
                Processing...
              </span>
            ) : (
              `✓ Approve ₹${proposal.expected_amount?.toLocaleString('en-IN')}`
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
