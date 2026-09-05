export default function Header({ title, subtitle }) {
  return (
    <header className="flex items-center justify-between mb-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{title}</h1>
        {subtitle && <p className="text-slate-500 mt-1 text-sm">{subtitle}</p>}
      </div>
      <div className="flex items-center gap-2">
        <span className="badge-success">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse-slow" />
          Live
        </span>
        <span className="badge-info">Razorpay Test Mode</span>
      </div>
    </header>
  )
}
