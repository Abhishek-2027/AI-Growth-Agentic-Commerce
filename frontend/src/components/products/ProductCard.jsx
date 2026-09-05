const CATEGORY_ICONS = {
  headphones: '🎧',
  earbuds: '🎵',
  electronics: '💻',
  accessories: '🔌',
  default: '📦',
}

import { logInteraction } from '../../api/recommendationApi';
import { v4 as uuidv4 } from 'uuid';

export default function ProductCard({ product, isSelected, onSelect }) {
  const icon = CATEGORY_ICONS[product.category?.toLowerCase()] || CATEGORY_ICONS.default
  const inStock = product.stock > 0

  const handleSelect = (p) => {
    let sid = localStorage.getItem('agent_session_id');
    if (!sid) {
      sid = uuidv4();
      localStorage.setItem('agent_session_id', sid);
    }
    logInteraction('PRODUCT_CLICK', p._id, null, sid);
    onSelect?.(p);
  };

  return (
    <div
      onClick={() => handleSelect(product)}
      className={`glass-card p-5 cursor-pointer transition-all duration-200 hover:border-brand-300 hover:shadow-lg hover:-translate-y-0.5 animate-fade-in
        ${isSelected ? 'border-brand-400 bg-brand-50 shadow-lg' : ''}`}
    >
      {/* Product icon/image area */}
      <div className="w-full h-28 rounded-xl bg-gradient-to-br from-brand-50 to-brand-100 flex items-center justify-center mb-4 text-5xl border border-brand-200 shadow-inner">
        {icon}
      </div>

      {/* Info */}
      <div className="space-y-2">
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-semibold text-slate-900 text-sm leading-tight line-clamp-2">{product.name}</h3>
          {isSelected && (
            <span className="flex-shrink-0 w-5 h-5 rounded-full bg-brand-500 text-white flex items-center justify-center text-xs">✓</span>
          )}
        </div>

        {product.brand && (
          <p className="text-xs text-slate-500">{product.brand}</p>
        )}

        <div className="flex items-center justify-between">
          <span className="text-lg font-bold text-slate-900">₹{product.price?.toLocaleString('en-IN')}</span>
          <span className={inStock ? 'badge-success' : 'badge-error'}>
            {inStock ? `${product.stock} in stock` : 'Out of stock'}
          </span>
        </div>

        {/* Features */}
        {product.features?.length > 0 && (
          <div className="flex flex-wrap gap-1 pt-1">
            {product.features.slice(0, 3).map((f) => (
              <span key={f} className="text-xs bg-slate-100 border border-slate-200 text-slate-600 px-2 py-0.5 rounded-full capitalize">
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
              onClick={(e) => { e.stopPropagation(); handleSelect(product); }}
              className="w-full bg-brand-50 hover:bg-brand-600 text-brand-700 hover:text-white border border-brand-200 text-xs font-semibold py-2 rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              <span>🤖</span> Buy with AI Agent
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
