const CATEGORY_ICONS = {
  headphones: '🎧',
  earbuds: '🎵',
  electronics: '💻',
  accessories: '🔌',
  default: '📦',
}

export default function ProductCard({ product, isSelected, onSelect }) {
  const icon = CATEGORY_ICONS[product.category?.toLowerCase()] || CATEGORY_ICONS.default
  const inStock = product.stock > 0

  return (
    <div
      onClick={() => onSelect?.(product)}
      className={`glass-card p-5 cursor-pointer transition-all duration-200 hover:border-brand-500/40 hover:shadow-lg hover:shadow-brand-500/10 hover:-translate-y-0.5 animate-fade-in
        ${isSelected ? 'border-brand-500/60 bg-brand-500/10 shadow-lg shadow-brand-500/20' : ''}`}
    >
      {/* Product icon/image area */}
      <div className="w-full h-28 rounded-xl bg-gradient-to-br from-brand-900/50 to-dark-900 flex items-center justify-center mb-4 text-5xl border border-white/5">
        {icon}
      </div>

      {/* Info */}
      <div className="space-y-2">
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-semibold text-white text-sm leading-tight line-clamp-2">{product.name}</h3>
          {isSelected && (
            <span className="flex-shrink-0 w-5 h-5 rounded-full bg-brand-500 flex items-center justify-center text-xs">✓</span>
          )}
        </div>

        {product.brand && (
          <p className="text-xs text-slate-500">{product.brand}</p>
        )}

        <div className="flex items-center justify-between">
          <span className="text-lg font-bold text-white">₹{product.price?.toLocaleString('en-IN')}</span>
          <span className={inStock ? 'badge-success' : 'badge-error'}>
            {inStock ? `${product.stock} in stock` : 'Out of stock'}
          </span>
        </div>

        {/* Features */}
        {product.features?.length > 0 && (
          <div className="flex flex-wrap gap-1 pt-1">
            {product.features.slice(0, 3).map((f) => (
              <span key={f} className="text-xs bg-white/5 border border-white/10 text-slate-400 px-2 py-0.5 rounded-full capitalize">
                {f}
              </span>
            ))}
            {product.features.length > 3 && (
              <span className="text-xs text-slate-500">+{product.features.length - 3}</span>
            )}
          </div>
        )}

        {product.rating && (
          <div className="flex items-center gap-1 pt-0.5">
            <span className="text-amber-400 text-xs">★</span>
            <span className="text-xs text-slate-400">{product.rating}</span>
          </div>
        )}
        
        {/* Buy with AI Button */}
        {onSelect && (
          <div className="pt-2">
            <button 
              onClick={(e) => { e.stopPropagation(); onSelect(product); }}
              className="w-full bg-brand-500/20 hover:bg-brand-500 text-brand-300 hover:text-white border border-brand-500/30 text-xs font-semibold py-2 rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              <span>🤖</span> Buy with AI Agent
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
