const EVENT_CONFIG = {
  USER_REQUEST_RECEIVED:    { icon: '💬', color: 'text-brand-600', bg: 'bg-brand-50 border-brand-200' },
  GUARDRAIL_INPUT_CHECK:    { icon: '🛡️', color: 'text-slate-600', bg: 'bg-slate-50 border-slate-200' },
  GUARDRAIL_INPUT_BLOCKED:  { icon: '🚫', color: 'text-red-600', bg: 'bg-red-50 border-red-200' },
  INTENT_EXTRACTED:         { icon: '🧠', color: 'text-violet-600', bg: 'bg-violet-50 border-violet-200' },
  CATALOG_SEARCHED:         { icon: '🔍', color: 'text-cyan-600', bg: 'bg-cyan-50 border-cyan-200' },
  PRODUCTS_ANALYZED:        { icon: '📊', color: 'text-cyan-600', bg: 'bg-cyan-50 border-cyan-200' },
  PRODUCT_SELECTED:         { icon: '✨', color: 'text-amber-600', bg: 'bg-amber-50 border-amber-200' },
  RECOMMENDATION_CREATED:   { icon: '🤖', color: 'text-amber-600', bg: 'bg-amber-50 border-amber-200' },
  PURCHASE_PROPOSAL_CREATED:{ icon: '📋', color: 'text-blue-600', bg: 'bg-blue-50 border-blue-200' },
  POLICY_CHECK_PASSED:      { icon: '✅', color: 'text-emerald-600', bg: 'bg-emerald-50 border-emerald-200' },
  POLICY_CHECK_FAILED:      { icon: '🚫', color: 'text-red-600', bg: 'bg-red-50 border-red-200' },
  USER_APPROVAL_REQUESTED:  { icon: '👤', color: 'text-amber-600', bg: 'bg-amber-50 border-amber-200' },
  USER_APPROVED:            { icon: '✅', color: 'text-emerald-600', bg: 'bg-emerald-50 border-emerald-200' },
  USER_REJECTED:            { icon: '❌', color: 'text-red-600', bg: 'bg-red-50 border-red-200' },
  RAZORPAY_ORDER_CREATED:   { icon: '💳', color: 'text-brand-600', bg: 'bg-brand-50 border-brand-200' },
  PAYMENT_PENDING:          { icon: '⏳', color: 'text-amber-600', bg: 'bg-amber-50 border-amber-200' },
  PAYMENT_VERIFIED:         { icon: '🎉', color: 'text-emerald-600', bg: 'bg-emerald-50 border-emerald-200' },
  PAYMENT_FAILED:           { icon: '❌', color: 'text-red-600', bg: 'bg-red-50 border-red-200' },
  ORDER_COMPLETED:          { icon: '🏆', color: 'text-emerald-600', bg: 'bg-emerald-50 border-emerald-200' },
  ORDER_CANCELLED:          { icon: '🚫', color: 'text-slate-600', bg: 'bg-slate-50 border-slate-200' },
}

function formatTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  return d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

function formatEventName(action) {
  return action.replace(/_/g, ' ')
}

const ACTOR_LABELS = { agent: '🤖 Agent', policy: '⚖️ Policy', user: '👤 User', payment: '💳 Payment', guardrail: '🛡️ Guardrail', system: '⚙️ System' }

export default function AuditTimeline({ events = [], loading, emptyMessage = 'No audit events yet.' }) {
  if (loading) {
    return (
      <div className="space-y-3">
        {[1,2,3].map(i => (
          <div key={i} className="glass-card p-4 animate-pulse h-16" />
        ))}
      </div>
    )
  }

  if (!events.length) {
    return (
      <div className="text-center py-16 text-slate-500">
        <div className="text-5xl mb-3">📋</div>
        <p className="text-sm">{emptyMessage}</p>
      </div>
    )
  }

  return (
    <div className="relative">
      {/* Timeline line */}
      <div className="absolute left-5 top-0 bottom-0 w-0.5 bg-gradient-to-b from-brand-300 via-slate-300 to-transparent" />

      <div className="space-y-3 pl-12">
        {events.map((ev, i) => {
          const cfg = EVENT_CONFIG[ev.action] || { icon: '⚡', color: 'text-slate-600', bg: 'bg-slate-50 border-slate-200' }
          const isSuccess = ev.status === 'SUCCESS'
          const isFailed = ev.status === 'FAILED' || ev.status === 'BLOCKED'

          return (
            <div key={ev._id || i} className={`relative glass-card p-4 border animate-fade-in ${cfg.bg}`}>
              {/* Timeline dot */}
              <div className={`absolute -left-9 top-4 w-7 h-7 rounded-full flex items-center justify-center text-base border-2 bg-white ${
                isSuccess ? 'border-emerald-500' : isFailed ? 'border-red-500' : 'border-brand-500'
              }`}>
                {cfg.icon}
              </div>

              <div className="flex items-start justify-between gap-2 flex-wrap">
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={`font-semibold text-sm ${cfg.color}`}>
                      {formatEventName(ev.action)}
                    </span>
                    <span className="text-xs text-slate-500">{ACTOR_LABELS[ev.actor] || ev.actor}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full border ${
                      isSuccess ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                      isFailed ? 'bg-red-50 text-red-700 border-red-200' :
                      'bg-amber-50 text-amber-700 border-amber-200'
                    }`}>
                      {ev.status}
                    </span>
                  </div>
                  <p className="text-sm text-slate-700 mt-1">{ev.reason}</p>
                </div>
                <span className="text-xs text-slate-500 font-mono flex-shrink-0">
                  {formatTime(ev.timestamp)}
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
