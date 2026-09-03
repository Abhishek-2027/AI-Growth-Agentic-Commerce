import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Dashboard', icon: '⚡' },
  { to: '/agent', label: 'AI Shopping Agent', icon: '🤖' },
  { to: '/products', label: 'Products', icon: '🛍️' },
  { to: '/orders', label: 'Orders', icon: '📦' },
  { to: '/audit', label: 'Audit Trail', icon: '🔍' },
]

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-screen w-64 flex flex-col bg-dark-900/80 backdrop-blur-xl border-r border-white/10 z-30">
      {/* Logo */}
      <div className="px-6 py-6 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center text-lg shadow-lg shadow-brand-500/30">
            🛒
          </div>
          <div>
            <h1 className="font-bold text-white text-sm leading-tight">AgentCart</h1>
            <p className="text-xs text-brand-400 font-medium">Safe Agentic Commerce</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {links.map(({ to, label, icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `sidebar-link ${isActive ? 'active' : ''}`
            }
          >
            <span className="text-lg">{icon}</span>
            <span className="text-sm">{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-white/10">
        <div className="glass-card px-3 py-2.5">
          <p className="text-xs text-slate-500 font-medium">Safety Architecture</p>
          <div className="mt-1 space-y-0.5">
            {['AI decides', 'Policy validates', 'User approves', 'System records'].map((t) => (
              <p key={t} className="text-xs text-emerald-400 flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 flex-shrink-0" />
                {t}
              </p>
            ))}
          </div>
        </div>
      </div>
    </aside>
  )
}
