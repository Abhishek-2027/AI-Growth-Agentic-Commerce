import ProductCard from '../products/ProductCard';

export default function PersonalizedRecommendations({ products, title, subtitle, onSelectProduct }) {
  if (!products) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-6 w-1/4 bg-slate-200 rounded"></div>
        <div className="flex gap-4 overflow-hidden">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="flex-shrink-0 w-64 h-64 bg-slate-100 rounded-xl"></div>
          ))}
        </div>
      </div>
    );
  }

  if (!products || products.length === 0) {
    return null; // Don't show empty sections
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-bold text-slate-900">{title}</h2>
        {subtitle && <p className="text-sm text-slate-500">{subtitle}</p>}
      </div>
      
      <div className="flex overflow-x-auto gap-4 pb-4 snap-x hide-scrollbar">
        {products.map((product) => (
          <div key={product._id} className="flex-shrink-0 w-64 snap-start">
            <ProductCard 
              product={product} 
              onSelect={onSelectProduct} 
              isSelected={false} 
            />
          </div>
        ))}
      </div>
    </div>
  );
}
