import ProductCard from './ProductCard'

export default function ProductList({ products = [], selectedId, onSelect, emptyMessage = 'No products found.' }) {
  if (!products.length) {
    return (
      <div className="text-center py-12 text-slate-500">
        <div className="text-4xl mb-3">🛍️</div>
        <p>{emptyMessage}</p>
      </div>
    )
  }
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {products.map((p) => (
        <ProductCard
          key={p._id}
          product={p}
          isSelected={p._id === selectedId}
          onSelect={onSelect}
        />
      ))}
    </div>
  )
}
