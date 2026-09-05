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
    <aside className="fixed left-0 top-0 h-screen w-64 flex flex-col bg-white border-r border-slate-200 z-30">
      {/* Logo */}
      <div className="px-6 py-6 border-b border-slate-200">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center text-lg shadow-lg shadow-brand-500/30 text-white">
            🛒
          </div>
          <div>
            <h1 className="font-bold text-slate-900 text-sm leading-tight">AgentCart</h1>
            <p className="text-xs text-brand-600 font-medium">Safe Agentic Commerce</p>
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
    </aside>
  )
}
