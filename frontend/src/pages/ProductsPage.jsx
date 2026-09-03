import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from '../components/layout/Header'
import ProductList from '../components/products/ProductList'
import { getProducts, searchProducts } from '../api/productApi'

export default function ProductsPage() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')
  const [maxPrice, setMaxPrice] = useState('')
  const navigate = useNavigate()

  const load = async () => {
    setLoading(true)
    try {
      if (query || maxPrice) {
        const data = await searchProducts({ query, max_price: maxPrice ? parseFloat(maxPrice) : undefined, limit: 50 })
        setProducts(data.products || [])
      } else {
        const data = await getProducts(50)
        setProducts(data.products || [])
      }
    } catch {}
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  const handleBuy = (product) => {
    navigate('/agent', { state: { autoPrompt: `I want to buy the ${product.name}` } })
  }

  return (
    <div>
      <Header title="Product Catalog" subtitle="AI-readable merchant catalog — all products available for the agent to search and recommend." />

      {/* Search bar */}
      <div className="glass-card p-4 mb-6 flex gap-3 flex-wrap">
        <input
          id="product-search-input"
          className="input-field flex-1 py-2.5 text-sm min-w-0"
          placeholder="Search products..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && load()}
        />
        <input
          className="input-field w-36 py-2.5 text-sm"
          placeholder="Max price ₹"
          type="number"
          value={maxPrice}
          onChange={(e) => setMaxPrice(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && load()}
        />
        <button className="btn-primary" onClick={load} disabled={loading}>
          {loading ? '...' : 'Search'}
        </button>
        <button className="btn-secondary" onClick={() => { setQuery(''); setMaxPrice(''); }}>
          Clear
        </button>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[1,2,3,4].map(i => <div key={i} className="glass-card h-52 animate-pulse" />)}
        </div>
      ) : (
        <ProductList products={products} onSelect={handleBuy} emptyMessage="No products found. Try a different search." />
      )}
    </div>
  )
}
