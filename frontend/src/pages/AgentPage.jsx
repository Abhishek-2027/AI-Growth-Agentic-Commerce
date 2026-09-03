import Header from '../components/layout/Header'
import AgentChat from '../components/agent/AgentChat'

export default function AgentPage() {
  return (
    <div>
      <Header
        title="AI Shopping Agent"
        subtitle="Tell the agent what you want — it searches the catalog, recommends a product, runs policy checks, and guides you through secure payment."
      />
      <AgentChat />
    </div>
  )
}
