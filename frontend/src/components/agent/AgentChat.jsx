import { useState, useRef, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { sendMessage } from '../../api/agentApi'
import ProductList from '../products/ProductList'
import RecommendationCard from './RecommendationCard'
import ApprovalModal from '../payment/ApprovalModal'
import AuditTimeline from '../audit/AuditTimeline'
import { getSessionAudit } from '../../api/auditApi'

const DEMO_PROMPTS = [
  'I want wireless noise-cancelling headphones under ₹5,000',
  'Find me good TWS earbuds with ANC under ₹3,000',
  'I need a good power bank under ₹4,000',
]

function ChatMessage({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-slide-up`}>
      <div className={`max-w-[85%] px-4 py-3 rounded-2xl text-sm ${
        isUser
          ? 'bg-brand-600 text-white rounded-br-sm'
          : 'glass-card text-slate-200 rounded-bl-sm'
      }`}>
        {!isUser && <span className="text-brand-400 font-semibold text-xs block mb-1">🤖 AgentCart AI</span>}
        <p className="leading-relaxed">{msg.content}</p>
        {msg.step && (
          <span className="text-xs opacity-60 mt-1 block">Step: {msg.step}</span>
        )}
      </div>
    </div>
  )
}

export default function AgentChat() {
  const location = useLocation()
  const navigate = useNavigate()

  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hi! I'm your AI shopping assistant. Tell me what you're looking for — I'll search our merchant catalog, recommend the best option within your budget, run safety checks, and guide you through a secure payment.",
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(() => localStorage.getItem('agent_session_id') || null)
  const [agentResult, setAgentResult] = useState(null)
  const [showApproval, setShowApproval] = useState(false)
  const [auditEvents, setAuditEvents] = useState([])
  const [showAudit, setShowAudit] = useState(false)
  const [error, setError] = useState(null)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const fetchAudit = async (sid) => {
    if (!sid) return
    try {
      const data = await getSessionAudit(sid)
      setAuditEvents(data.events || [])
    } catch {}
  }

  const handleSend = async (text) => {
    const msg = (text || input).trim()
    if (!msg || loading) return
    setInput('')
    setError(null)
    setAgentResult(null)
    setShowApproval(false)

    setMessages((m) => [...m, { role: 'user', content: msg }])
    setLoading(true)

    setMessages((m) => [...m, { role: 'assistant', content: '⏳ Analyzing your request...', step: 'processing', id: 'thinking' }])

    try {
      const result = await sendMessage(msg, sessionId)
      if (result.session_id) {
        setSessionId(result.session_id)
        localStorage.setItem('agent_session_id', result.session_id)
      }

      // Remove thinking message
      setMessages((m) => m.filter((x) => x.id !== 'thinking'))

      if (result.error) {
        setMessages((m) => [...m, {
          role: 'assistant',
          content: `⚠️ ${result.error}`,
          step: result.step,
        }])
        setError(result.error)
      } else {
        setAgentResult(result)

        // Build agent reply message
        const selected = result.selected_product
        const policy = result.policy_result
        let reply = ''

        if (selected) {
          reply = `I found a great match: **${selected.name}** at ₹${selected.price?.toLocaleString('en-IN')}.`
          if (result.recommendation_reason) reply += ` ${result.recommendation_reason}`
          
          if (result.products && result.products.length > 1) {
            reply += `\n\nI've also found ${result.products.length - 1} other choices. You can check them below and let me know if you prefer one of those!`
          }

          if (policy?.approved) {
            reply += '\n\n✅ All safety checks passed. You can review and approve the payment below.'
          } else if (policy?.blocked_reasons?.length) {
            reply += `\n\n🚫 Policy check failed: ${policy.blocked_reasons[0]}`
          }
        } else if (result.products?.length) {
          reply = `I found ${result.products.length} products matching your requirements. Analyzing the best option...`
        } else {
          reply = 'I searched the catalog but could not find products matching your requirements. Try adjusting your budget or features.'
        }

        setMessages((m) => [...m, { role: 'assistant', content: reply, step: result.step }])

        // Fetch audit trail
        await fetchAudit(result.session_id)
        setShowAudit(true)
      }
    } catch (err) {
      setMessages((m) => m.filter((x) => x.id !== 'thinking'))
      setMessages((m) => [...m, { role: 'assistant', content: `❌ Error: ${err.message}` }])
      setError(err.message)
    }
    setLoading(false)
  }

  // Handle autoPrompt from navigation state
  useEffect(() => {
    if (location.state?.autoPrompt) {
      const prompt = location.state.autoPrompt
      // Clear state so it doesn't trigger again on refresh
      navigate('.', { replace: true, state: {} })
      handleSend(prompt)
    }
  }, [location.state])

  const handleApproved = async (orderId) => {
    setShowApproval(false)
    setMessages((m) => [...m, { role: 'assistant', content: `🎉 Payment verified! Order ID: ${orderId}. The complete audit trail is now available.` }])
    if (sessionId) await fetchAudit(sessionId)
  }

  const handleRejected = (msg) => {
    setShowApproval(false)
    const content = typeof msg === 'string' 
      ? msg 
      : '❌ Purchase cancelled. Let me know if you want to search for something else.'
    setMessages((m) => [...m, { role: 'assistant', content }])
    if (sessionId) fetchAudit(sessionId)
  }

  const canApprove = agentResult?.purchase_proposal && agentResult?.policy_result?.approved

  return (
    <div className="flex flex-col gap-6">
      {/* Chat area */}
      <div className="glass-card flex flex-col" style={{ height: '400px' }}>
        <div className="flex items-center justify-between px-5 py-4 border-b border-white/10">
          <div className="flex items-center gap-2">
            <span className="text-lg">🤖</span>
            <span className="font-semibold text-white text-sm">AI Shopping Agent</span>
            <span className="badge-success">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Active
            </span>
          </div>
          {sessionId && (
            <button
              onClick={() => setShowAudit((p) => !p)}
              className="text-xs text-brand-400 hover:text-brand-300 transition-colors"
            >
              {showAudit ? 'Hide' : 'Show'} Audit Trail ({auditEvents.length})
            </button>
          )}
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-5 space-y-3">
          {messages.map((msg, i) => <ChatMessage key={i} msg={msg} />)}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="px-4 py-4 border-t border-white/10">
          {/* Demo prompts */}
          {!agentResult && (
            <div className="flex gap-2 flex-wrap mb-3">
              {DEMO_PROMPTS.map((p) => (
                <button
                  key={p}
                  onClick={() => handleSend(p)}
                  className="text-xs bg-white/5 hover:bg-white/10 border border-white/10 text-slate-400 hover:text-white px-3 py-1.5 rounded-lg transition-colors"
                >
                  {p.length > 40 ? p.slice(0, 38) + '…' : p}
                </button>
              ))}
            </div>
          )}
          <form onSubmit={(e) => { e.preventDefault(); handleSend() }} className="flex gap-2">
            <input
              id="agent-chat-input"
              className="input-field flex-1 py-2.5 text-sm"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="E.g. I want wireless headphones under ₹5,000..."
              disabled={loading}
            />
            <button id="agent-send-btn" type="submit" className="btn-primary px-5" disabled={loading}>
              {loading ? '...' : '→'}
            </button>
          </form>
        </div>
      </div>

      {/* Products found */}
      {agentResult?.products?.length > 0 && (
        <div className="animate-fade-in">
          <h3 className="font-semibold text-white mb-3">
            Products Found ({agentResult.products.length})
          </h3>
          <ProductList
            products={agentResult.products}
            selectedId={agentResult.selected_product?._id}
            onSelect={(product) => handleSend(`I want to buy the ${product.name}`)}
          />
        </div>
      )}

      {/* Recommendation & Policy */}
      {agentResult?.selected_product && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <RecommendationCard
            selectedProduct={agentResult.selected_product}
            reasons={agentResult.recommendation_reasons_list || []}
            policyResult={agentResult.policy_result}
          />

          {/* Approval card */}
          {canApprove && (
            <div className="glass-card p-6 border-amber-500/20 bg-amber-500/5 flex flex-col justify-between animate-slide-up">
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-xl">👤</span>
                  <h3 className="font-bold text-amber-300">Human Approval Required</h3>
                </div>
                <p className="text-slate-300 text-sm mb-4">
                  The AI has proposed a purchase. You must explicitly approve before any payment is created.
                </p>
                <div className="space-y-1.5 mb-6">
                </div>
              </div>
              <button
                id="approve-payment-btn"
                className="btn-success w-full text-base py-3"
                onClick={() => setShowApproval(true)}
              >
                💳 Review & Approve Payment
              </button>
            </div>
          )}
        </div>
      )}

      {/* Audit Trail */}
      {showAudit && auditEvents.length > 0 && (
        <div className="animate-fade-in">
          <h3 className="font-semibold text-white mb-4">📋 Live Audit Trail ({auditEvents.length} events)</h3>
          <AuditTimeline events={auditEvents} />
        </div>
      )}

      {/* Approval Modal */}
      {showApproval && (
        <ApprovalModal
          proposal={agentResult?.purchase_proposal}
          sessionId={sessionId}
          onApproved={handleApproved}
          onRejected={handleRejected}
          onClose={() => setShowApproval(false)}
        />
      )}
    </div>
  )
}
