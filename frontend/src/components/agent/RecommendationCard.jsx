export default function RecommendationCard({ selectedProduct, reasons = [], policyResult }) {
  if (!selectedProduct) return null

  const policyChecks = [
    { label: 'Budget within limit', passed: policyResult?.budget_check },
    { label: 'Product in stock', passed: policyResult?.stock_check },
    { label: 'Quantity valid', passed: policyResult?.quantity_check },
    { label: 'Currency accepted', passed: policyResult?.currency_check },
    { label: 'Product active', passed: policyResult?.product_active_check },
  ]

  return (
    <div className="glass-card p-6 border-brand-200 bg-brand-50 animate-slide-up">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <div className="w-7 h-7 rounded-lg bg-brand-100 flex items-center justify-center text-sm">🤖</div>
        <h3 className="font-bold text-brand-700 text-sm tracking-wide uppercase">AI Recommendation</h3>
      </div>

      {/* Product */}
      <div className="mb-4">
        <h2 className="text-xl font-bold text-slate-900">{selectedProduct.name}</h2>
        {selectedProduct.brand && <p className="text-slate-500 text-sm">{selectedProduct.brand}</p>}
        <div className="mt-2 flex items-center gap-3">
          <span className="text-3xl font-bold text-slate-900">₹{selectedProduct.price?.toLocaleString('en-IN')}</span>
          <span className="badge-success">{selectedProduct.currency || 'INR'}</span>
        </div>
      </div>

      {/* Why selected */}
      {reasons.length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Why Selected</p>
          <ul className="space-y-1.5">
            {reasons.map((r, i) => (
              <li key={i} className="text-sm text-emerald-600 flex items-start gap-2">
                <span className="flex-shrink-0 mt-0.5">✓</span>
                <span>{r.replace(/^✓\s*/, '')}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Policy checks */}
      {policyResult && (
        <div className="border-t border-slate-200 pt-4">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Safety Policy</p>
          <ul className="space-y-1.5">
            {policyChecks.map(({ label, passed }) => (
              <li key={label} className="flex items-center gap-2 text-sm">
                <span className={passed ? 'text-emerald-500' : 'text-red-500'}>{passed ? '✓' : '✗'}</span>
                <span className={passed ? 'text-slate-700' : 'text-red-600'}>{label}</span>
              </li>
            ))}
          </ul>
          {!policyResult.approved && policyResult.blocked_reasons?.length > 0 && (
            <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-xs text-red-700 font-semibold mb-1">Policy Blocked:</p>
              {policyResult.blocked_reasons.map((r, i) => (
                <p key={i} className="text-xs text-red-600">• {r}</p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
