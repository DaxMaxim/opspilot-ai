/* Landing Page — OpsPilot AI */

export default function LandingPage() {
  return (
    <div className="page-container">
      {/* Hero */}
      <section className="hero" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        <div className="hero-glow" />
        <div className="hero-badge" style={{ marginBottom: '32px' }}>◆ Enterprise Decision Engine</div>
        <h1 style={{ maxWidth: '800px', margin: '0 auto 24px' }}>
          Autonomous, Policy-Grounded
          <br />
          <span className="gradient-text">Operational Decisions</span>
        </h1>
        <p style={{ maxWidth: '650px', fontSize: '1.125rem', color: 'var(--text-secondary)', lineHeight: 1.8, marginBottom: '16px' }}>
          Automatically reviews cases, applies policy rules, and returns structured
          decisions (approve, deny, escalate, or request more information).
        </p>
        <p style={{ maxWidth: '650px', fontSize: '0.875rem', color: 'var(--text-tertiary)', lineHeight: 1.6, marginBottom: '40px' }}>
          Used in compliance, customer support, and operational decision systems.
        </p>
        <div style={{ display: 'flex', gap: '16px' }}>
          <a href="/review" className="btn btn-primary btn-lg" style={{ padding: '16px 32px' }}>
            Launch Decision Engine →
          </a>
          <a href="/traces" className="btn btn-secondary btn-lg" style={{ padding: '16px 32px' }}>
            View Trace History
          </a>
        </div>
      </section>

      {/* Feature Cards */}
      <section className="feature-grid">
        <div className="feature-card">
          <div className="feature-icon">📋</div>
          <div className="feature-title">Policy-Grounded Decisions</div>
          <div className="feature-desc">
            Every decision is anchored in retrieved policy documents via
            vector search. Citations trace exactly which clauses drove the
            outcome.
          </div>
        </div>
        <div className="feature-card">
          <div className="feature-icon">⚙️</div>
          <div className="feature-title">Agentic Workflows</div>
          <div className="feature-desc">
            LangGraph orchestrates an 8-node decision pipeline: parse, retrieve,
            decide, call tools, generate, evaluate, improve, and trace.
          </div>
        </div>
        <div className="feature-card">
          <div className="feature-icon">✓</div>
          <div className="feature-title">Evaluation Layer</div>
          <div className="feature-desc">
            Built-in evaluator checks groundedness, policy consistency,
            escalation appropriateness, and retrieval coverage on every
            decision.
          </div>
        </div>
        <div className="feature-card">
          <div className="feature-icon">📊</div>
          <div className="feature-title">Trace Observability</div>
          <div className="feature-desc">
            Full node-by-node execution traces stored in SQLite. Inspect
            inputs, retrievals, tool calls, evaluation, and timing for every
            run.
          </div>
        </div>
      </section>

      {/* Architecture summary */}
      <section style={{ marginTop: '80px', textAlign: 'center' }}>
        <h2 className="page-title" style={{ fontSize: '1.8rem' }}>How It Works</h2>
        <p className="page-subtitle" style={{ maxWidth: 600, margin: '0 auto 40px' }}>
          Structured cases flow through a deterministic agentic pipeline. 
          No free-form outputs — every decision follows a strict JSON schema.
        </p>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
          gap: '8px',
          maxWidth: 900,
          margin: '0 auto'
        }}>
          {[
            { step: '1', label: 'Parse Case', icon: '📥' },
            { step: '2', label: 'Retrieve Policy', icon: '🔍' },
            { step: '3', label: 'Decide Action', icon: '🧠' },
            { step: '4', label: 'Call Tools', icon: '🔧' },
            { step: '5', label: 'Final Decision', icon: '⚖️' },
            { step: '6', label: 'Evaluate', icon: '✓' },
            { step: '7', label: 'Improve', icon: '💡' },
            { step: '8', label: 'Save Trace', icon: '💾' },
          ].map((s) => (
            <div key={s.step} className="card" style={{
              textAlign: 'center',
              padding: '20px 12px',
            }}>
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>{s.icon}</div>
              <div style={{
                fontFamily: 'var(--font-mono)',
                fontSize: 'var(--text-xs)',
                color: 'var(--text-accent)',
                marginBottom: '4px'
              }}>
                Node {s.step}
              </div>
              <div style={{
                fontSize: 'var(--text-sm)',
                fontWeight: 600,
                color: 'var(--text-primary)'
              }}>
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Bottom CTA */}
      <section style={{ textAlign: 'center', padding: '100px 0 60px' }}>
        <h2 style={{ fontSize: '2.5rem', fontWeight: 800, marginBottom: '24px', letterSpacing: '-0.03em' }}>
          Ready to automate <span className="gradient-text">complex ops?</span>
        </h2>
        <a href="/review" className="btn btn-primary btn-lg" style={{ padding: '16px 40px', fontSize: '1.125rem' }}>
          Run Your First Case →
        </a>
      </section>
    </div>
  );
}
