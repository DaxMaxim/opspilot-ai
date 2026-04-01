'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import type { CaseInput, DecisionOutput } from '@/lib/types';
import { reviewCase, healthCheck } from '@/lib/api';
import { SAMPLE_CASES } from '@/lib/samples';

const CASE_TYPES = [
  { value: 'refund_request', label: 'Refund Request' },
  { value: 'claim_review', label: 'Claim Review' },
  { value: 'exception_request', label: 'Exception Request' },
  { value: 'fraud_investigation', label: 'Fraud Investigation' },
  { value: 'escalation', label: 'Escalation' },
];

const PRIORITIES = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
  { value: 'critical', label: 'Critical' },
];

export default function ReviewPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Silent backend warm-up on page load to reduce cold-start latency
  useEffect(() => {
    healthCheck().catch(() => {});
  }, []);
  const [result, setResult] = useState<DecisionOutput | null>(null);
  const [form, setForm] = useState<CaseInput>({
    case_type: 'refund_request',
    customer_id: '',
    amount: 0,
    purchase_date: '',
    request_date: new Date().toISOString().split('T')[0],
    priority: 'medium',
    description: '',
  });

  const updateField = (field: keyof CaseInput, value: string | number) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const loadSample = (index: number) => {
    setForm(SAMPLE_CASES[index].data);
    setResult(null);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await reviewCase(form);
      setResult(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">OpsPilot Decision Engine</h1>
        <p className="page-subtitle">
          Submit a structured case for autonomous, policy-grounded analysis.
        </p>
      </div>

      <div className="two-col">
        {/* Left: Form */}
        <div>
          {/* Quick Demo Cases */}
          <div style={{ marginBottom: '24px' }}>
            <div className="section-title" style={{ fontSize: 'var(--text-md)', marginBottom: '12px', color: 'var(--text-secondary)' }}>
              <span className="section-icon">⚡</span> Quick Select: Demo Scenarios
            </div>
            <div className="demo-chips">
              {SAMPLE_CASES.map((sample, i) => (
                <button
                  key={i}
                  type="button"
                  className="demo-chip"
                  onClick={() => loadSample(i)}
                  title={sample.description}
                >
                  {sample.title}
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={handleSubmit} className="card" style={{ padding: '28px' }}>
            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">Case Type</label>
                <select
                  className="form-select"
                  value={form.case_type}
                  onChange={(e) => updateField('case_type', e.target.value)}
                >
                  {CASE_TYPES.map((t) => (
                    <option key={t.value} value={t.value}>{t.label}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Customer ID</label>
                <input
                  className="form-input"
                  type="text"
                  placeholder="CUST-1234"
                  value={form.customer_id}
                  onChange={(e) => updateField('customer_id', e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Amount (USD)</label>
                <input
                  className="form-input"
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="49.99"
                  value={form.amount || ''}
                  onChange={(e) => updateField('amount', parseFloat(e.target.value) || 0)}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Priority</label>
                <select
                  className="form-select"
                  value={form.priority}
                  onChange={(e) => updateField('priority', e.target.value)}
                >
                  {PRIORITIES.map((p) => (
                    <option key={p.value} value={p.value}>{p.label}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Purchase Date</label>
                <input
                  className="form-input"
                  type="date"
                  value={form.purchase_date}
                  onChange={(e) => updateField('purchase_date', e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Request Date</label>
                <input
                  className="form-input"
                  type="date"
                  value={form.request_date}
                  onChange={(e) => updateField('request_date', e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="form-group" style={{ marginTop: '16px' }}>
              <label className="form-label">Case Description</label>
              <textarea
                className="form-textarea"
                placeholder="Describe the case circumstances, customer claims, and any relevant context..."
                value={form.description}
                onChange={(e) => updateField('description', e.target.value)}
                required
                rows={3}
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-lg"
              disabled={loading}
              style={{ marginTop: '20px', width: '100%' }}
            >
              {loading ? (
                <>
                  <span className="spinner" />
                  Running decision pipeline…
                </>
              ) : (
                'Run Decision Review →'
              )}
            </button>
            <div style={{ marginTop: '12px', fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)', textAlign: 'center', lineHeight: 1.5 }}>
              ⚠️ If the backend is idle, the first request may take up to ~60 seconds due to cold start. Subsequent requests are near real-time.
            </div>
          </form>

        </div>

        {/* Right: Result */}
        <div>
          {loading && (
            <div className="card loading-overlay">
              <div className="spinner" />
              <div>Running decision pipeline…</div>
              <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)', marginTop: '8px' }}>
                parse → retrieve → decide → tools → evaluate → trace
              </div>
              <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)', marginTop: '4px', opacity: 0.7 }}>
                Initializing backend if idle…
              </div>
            </div>
          )}

          {error && (
            <div className="error-box">
              <div className="error-title">Pipeline Error</div>
              <div className="error-text">{error}</div>
              <button
                className="btn btn-secondary"
                style={{ marginTop: '16px' }}
                onClick={() => setError(null)}
              >
                Dismiss
              </button>
            </div>
          )}

          {result && !loading && <DecisionResult result={result} />}

          {!result && !loading && !error && (
            <div className="card empty-state">
              <div className="empty-state-icon">⬡</div>
              <div className="empty-state-title">No Decision Yet</div>
              <div className="empty-state-text">
                Submit a case or select a demo case to run the decision pipeline.
                Results will appear here with full evaluation and trace data.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}


/* ─── Decision Result Component ─── */

function DecisionResult({ result }: { result: DecisionOutput }) {
  const decisionClass = result.decision.toLowerCase().replace(/_/g, '_');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Decision Header */}
      <div className="card" style={{ padding: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div className="section-title" style={{ marginBottom: '8px' }}>Final Determination</div>
          <div className={`decision-badge ${decisionClass}`} style={{ fontSize: '1.25rem', padding: '12px 28px' }}>
            {result.decision === 'NEED_MORE_INFO' ? 'NEED MORE INFO' : result.decision}
          </div>
        </div>
        <div style={{ textAlign: 'right', minWidth: '150px' }}>
          <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Confidence</div>
          <div style={{ fontSize: '2rem', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--text-accent)', lineHeight: 1.1 }}>
            {Math.round(result.confidence * 100)}%
          </div>
        </div>
      </div>

      {/* Reason */}
      <div className="card" style={{ padding: '24px' }}>
        <p style={{ fontSize: 'var(--text-base)', color: 'var(--text-primary)', lineHeight: 1.6, fontWeight: 500 }}>
          {result.reason}
        </p>
      </div>

      {/* Why This Decision */}
      <div className="why-block">
        <div className="section-title" style={{ color: 'var(--text-accent)' }}>
          <span className="section-icon">❓</span> Why This Decision?
        </div>
        <div className="why-item">
          <span className="why-label">Policy Clause</span>
          <span className="why-value">{result.why_this_decision.policy_clause_used}</span>
        </div>
        <div className="why-item">
          <span className="why-label">Key Condition</span>
          <span className="why-value">{result.why_this_decision.key_condition_matched}</span>
        </div>
        <div className="why-item">
          <span className="why-label">Constraint</span>
          <span className="why-value">{result.why_this_decision.key_constraint_triggered}</span>
        </div>
      </div>

      {/* Policy Citations */}
      <div className="card">
        <div className="section-title"><span className="section-icon">📋</span> Policy Citations</div>
        {result.policy_citations.map((c, i) => (
          <div key={i} className="citation-card">
            <div className="citation-id">{c.policy_id} — {c.policy_name}</div>
            <div className="citation-section">{c.section}</div>
            <div className="citation-text">&ldquo;{c.relevant_text}&rdquo;</div>
          </div>
        ))}
      </div>

      {/* Tool Calls */}
      {result.tool_calls.length > 0 && (
        <div className="card">
          <div className="section-title"><span className="section-icon">🔧</span> Tool Calls</div>
          {result.tool_calls.map((t, i) => (
            <div key={i} className="tool-card">
              <div className="flex-between">
                <span className="tool-name">{t.tool_name}()</span>
                <span className="tool-time">{t.execution_time_ms}ms</span>
              </div>
              <div className="code-block" style={{ marginTop: '8px', fontSize: '11px' }}>
                {JSON.stringify(t.output_data, null, 2)}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Evaluation */}
      <div className="card">
        <div className="section-title"><span className="section-icon">✓</span> Evaluation Verdict</div>
        <div className="confidence-bar" style={{ marginBottom: '16px' }}>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>Overall Score</span>
          <div className="confidence-track">
            <div className="confidence-fill" style={{ width: `${result.evaluation.overall_score * 100}%` }} />
          </div>
          <span className="confidence-value">{Math.round(result.evaluation.overall_score * 100)}%</span>
        </div>
        <EvalCheck label="Grounded" state={result.evaluation.grounded ? 'pass' : 'fail'} detail={result.evaluation.grounded_explanation} />
        <EvalCheck label="Policy Consistent" state={result.evaluation.policy_consistent ? 'pass' : 'fail'} detail={result.evaluation.policy_consistent_explanation} />
        <EvalCheck label="Escalation Decision Correct" state={result.evaluation.escalation_decision_correct ? 'pass' : 'fail'} detail={result.evaluation.escalation_explanation} />
        <EvalCheck label="Retrieval Sufficient" state={result.evaluation.retrieval_sufficient ? 'pass' : 'fail'} detail={result.evaluation.retrieval_explanation} />
        <EvalCheck
          label="Retrieval Quality"
          state={result.evaluation.retrieval_quality === 'clean' ? 'pass' : result.evaluation.retrieval_quality === 'minor_issues' ? 'warn' : 'fail'}
          detail={result.evaluation.retrieval_quality_explanation || 'No quality issues detected.'}
        />
      </div>

      {/* Improvement Suggestion */}
      {result.improvement_suggestion && (
        <div className="improvement-box">
          <div className="improvement-title">💡 Suggested Improvement</div>
          <div className="improvement-text">{result.improvement_suggestion}</div>
        </div>
      )}

      {/* Trace Link */}
      <div style={{ textAlign: 'center' }}>
        <a href={`/traces/${result.trace_id}`} className="btn btn-secondary">
          View Full Trace →
        </a>
      </div>
    </div>
  );
}


function EvalCheck({ label, state, detail }: { label: string; state: 'pass' | 'warn' | 'fail'; detail: string }) {
  const icon = state === 'pass' ? '✓' : state === 'warn' ? '⚠' : '✗';
  return (
    <div className="eval-check">
      <div className={`eval-icon ${state}`}>
        {icon}
      </div>
      <div>
        <div className="eval-label">{label}</div>
        <div className="eval-detail">{detail}</div>
      </div>
    </div>
  );
}
