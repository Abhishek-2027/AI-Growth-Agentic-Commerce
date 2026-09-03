const EVENT_CONFIG = {
  USER_REQUEST_RECEIVED:    { icon: '💬', color: 'text-brand-400', bg: 'bg-brand-500/10 border-brand-500/20' },
  GUARDRAIL_INPUT_CHECK:    { icon: '🛡️', color: 'text-slate-400', bg: 'bg-slate-500/10 border-slate-500/20' },
  GUARDRAIL_INPUT_BLOCKED:  { icon: '🚫', color: 'text-red-400', bg: 'bg-red-500/10 border-red-500/20' },
  INTENT_EXTRACTED:         { icon: '🧠', color: 'text-violet-400', bg: 'bg-violet-500/10 border-violet-500/20' },
  CATALOG_SEARCHED:         { icon: '🔍', color: 'text-cyan-400', bg: 'bg-cyan-500/10 border-cyan-500/20' },
  PRODUCTS_ANALYZED:        { icon: '📊', color: 'text-cyan-400', bg: 'bg-cyan-500/10 border-cyan-500/20' },
  PRODUCT_SELECTED:         { icon: '✨', color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/20' },
  RECOMMENDATION_CREATED:   { icon: '🤖', color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/20' },
  PURCHASE_PROPOSAL_CREATED:{ icon: '📋', color: 'text-blue-400', bg: 'bg-blue-500/10 border-blue-500/20' },
  POLICY_CHECK_PASSED:      { icon: '✅', color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20' },
  POLICY_CHECK_FAILED:      { icon: '🚫', color: 'text-red-400', bg: 'bg-red-500/10 border-red-500/20' },
  USER_APPROVAL_REQUESTED:  { icon: '👤', color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/20' },
  USER_APPROVED:            { icon: '✅', color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20' },
  USER_REJECTED:            { icon: '❌', color: 'text-red-400', bg: 'bg-red-500/10 border-red-500/20' },
  RAZORPAY_ORDER_CREATED:   { icon: '💳', color: 'text-brand-400', bg: 'bg-brand-500/10 border-brand-500/20' },
  PAYMENT_PENDING:          { icon: '⏳', color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/20' },
  PAYMENT_VERIFIED:         { icon: '🎉', color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20' },
  PAYMENT_FAILED:           { icon: '❌', color: 'text-red-400', bg: 'bg-red-500/10 border-red-500/20' },
  ORDER_COMPLETED:          { icon: '🏆', color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20' },
  ORDER_CANCELLED:          { icon: '🚫', color: 'text-slate-400', bg: 'bg-slate-500/10 border-slate-500/20' },
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
      <div className="absolute left-5 top-0 bottom-0 w-0.5 bg-gradient-to-b from-brand-500/50 via-slate-700 to-transparent" />

      <div className="space-y-3 pl-12">
        {events.map((ev, i) => {
          const cfg = EVENT_CONFIG[ev.action] || { icon: '⚡', color: 'text-slate-400', bg: 'bg-slate-500/10 border-slate-500/20' }
          const isSuccess = ev.status === 'SUCCESS'
          const isFailed = ev.status === 'FAILED' || ev.status === 'BLOCKED'

          return (
            <div key={ev._id || i} className={`relative glass-card p-4 border animate-fade-in ${cfg.bg}`}>
              {/* Timeline dot */}
              <div className={`absolute -left-9 top-4 w-7 h-7 rounded-full flex items-center justify-center text-base border-2 bg-dark-900 ${
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
                      isSuccess ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                      isFailed ? 'bg-red-500/10 text-red-400 border-red-500/20' :
                      'bg-amber-500/10 text-amber-400 border-amber-500/20'
                    }`}>
                      {ev.status}
                    </span>
                  </div>
                  <p className="text-sm text-slate-300 mt-1">{ev.reason}</p>
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
