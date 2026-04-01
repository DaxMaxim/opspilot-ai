'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import type { TraceDetail } from '@/lib/types';
import { getTraceDetail } from '@/lib/api';

export default function TraceDetailPage() {
  const params = useParams();
  const traceId = params.id as string;
  const [trace, setTrace] = useState<TraceDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTrace();
  }, [traceId]);

  const loadTrace = async () => {
    try {
      const data = await getTraceDetail(traceId);
      setTrace(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load trace');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="card loading-overlay">
          <div className="spinner" />
          <div>Loading trace detail...</div>
        </div>
      </div>
    );
  }

  if (error || !trace) {
    return (
      <div className="page-container">
        <div className="error-box">
          <div className="error-title">Trace Not Found</div>
          <div className="error-text">{error || 'The requested trace does not exist.'}</div>
          <a href="/traces" className="btn btn-secondary" style={{ marginTop: '16px' }}>
            ← Back to Traces
          </a>
        </div>
      </div>
    );
  }

  const formatDate = (iso: string) => {
    return new Date(iso).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const decisionClass = trace.decision.toLowerCase().replace(/_/g, '_');

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div className="flex-between">
          <div>
            <a href="/traces" style={{ fontSize: 'var(--text-sm)', color: 'var(--text-tertiary)', display: 'block', marginBottom: '8px' }}>
              ← Back to Traces
            </a>
            <h1 className="page-title">Trace Detail</h1>
            <p className="page-subtitle" style={{ fontFamily: 'var(--font-mono)' }}>
              {trace.id}
            </p>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div className={`decision-badge ${decisionClass}`} style={{ fontSize: '1rem', padding: '10px 24px' }}>
              {trace.decision === 'NEED_MORE_INFO' ? 'NEED MORE INFO' : trace.decision}
            </div>
            <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)', marginTop: '8px' }}>
              {formatDate(trace.created_at)} · {(trace.duration_ms / 1000).toFixed(1)}s total
            </div>
          </div>
        </div>
      </div>

      {/* Top: Input + Decision summary */}
      <div className="two-col">
        <div className="card">
          <div className="section-title"><span className="section-icon">📥</span> Input Payload</div>
          <div className="code-block">
            {JSON.stringify(trace.case_input, null, 2)}
          </div>
        </div>
        <div className="card" style={{ padding: '24px' }}>
          <div className="section-title" style={{ marginBottom: '16px' }}>
            <span className="section-icon">⚖️</span> Final Determination
          </div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
            <div className={`decision-badge ${decisionClass}`} style={{ fontSize: '1rem', padding: '10px 24px' }}>
              {trace.decision === 'NEED_MORE_INFO' ? 'NEED MORE INFO' : trace.decision}
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Confidence</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--text-accent)', lineHeight: 1.1 }}>
                {Math.round(trace.confidence * 100)}%
              </div>
            </div>
          </div>
          <p style={{ fontSize: 'var(--text-base)', color: 'var(--text-primary)', lineHeight: 1.6, fontWeight: 500 }}>
            {trace.reason}
          </p>
        </div>
      </div>

      {/* Why This Decision */}
      {trace.why_this_decision && (
        <div className="why-block" style={{ marginTop: '16px' }}>
          <div className="section-title" style={{ color: 'var(--text-accent)' }}>
            <span className="section-icon">❓</span> Why This Decision?
          </div>
          <div className="why-item">
            <span className="why-label">Policy Clause</span>
            <span className="why-value">{trace.why_this_decision.policy_clause_used}</span>
          </div>
          <div className="why-item">
            <span className="why-label">Key Condition</span>
            <span className="why-value">{trace.why_this_decision.key_condition_matched}</span>
          </div>
          <div className="why-item">
            <span className="why-label">Constraint</span>
            <span className="why-value">{trace.why_this_decision.key_constraint_triggered}</span>
          </div>
        </div>
      )}

      {/* Workflow Timeline */}
      <div className="card" style={{ marginTop: '16px' }}>
        <div className="section-title"><span className="section-icon">⏱</span> Workflow Execution Timeline</div>
        <div className="timeline">
          {trace.workflow_trace.map((node, i) => (
            <div key={i} className="timeline-item">
              <div className="timeline-dot" />
              <div className="timeline-content">
                <div>
                  <span className="timeline-node">{node.node}</span>
                  <span className="timeline-duration">{node.duration_ms}ms</span>
                </div>
                <div className="timeline-summary">{node.output_summary}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Retrieved Docs + Tool Outputs + Evaluation */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginTop: '16px' }}>
        {/* Policy Citations */}
        <div className="card">
          <div className="section-title"><span className="section-icon">📋</span> Policy Citations</div>
          {trace.policy_citations.length > 0 ? (
            trace.policy_citations.map((c, i) => (
              <div key={i} className="citation-card">
                <div className="citation-id">{c.policy_id} — {c.policy_name}</div>
                <div className="citation-section">{c.section}</div>
                <div className="citation-text">&ldquo;{c.relevant_text}&rdquo;</div>
              </div>
            ))
          ) : (
            <div style={{ fontSize: 'var(--text-sm)', color: 'var(--text-tertiary)' }}>
              No policy citations recorded.
            </div>
          )}
        </div>

        {/* Tool Calls */}
        <div className="card">
          <div className="section-title"><span className="section-icon">🔧</span> Tool Outputs</div>
          {trace.tool_calls.length > 0 ? (
            trace.tool_calls.map((t, i) => (
              <div key={i} className="tool-card">
                <div className="flex-between">
                  <span className="tool-name">{t.tool_name}()</span>
                  <span className="tool-time">{t.execution_time_ms}ms</span>
                </div>
                <div className="code-block" style={{ marginTop: '8px', fontSize: '11px' }}>
                  {JSON.stringify(t.output_data, null, 2)}
                </div>
              </div>
            ))
          ) : (
            <div style={{ fontSize: 'var(--text-sm)', color: 'var(--text-tertiary)' }}>
              No tool calls executed.
            </div>
          )}
        </div>
      </div>

      {/* Evaluation */}
      <div className="card" style={{ marginTop: '16px' }}>
        <div className="section-title"><span className="section-icon">✓</span> Evaluation Output</div>
        <div className="confidence-bar" style={{ marginBottom: '16px' }}>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>Overall Score</span>
          <div className="confidence-track">
            <div className="confidence-fill" style={{ width: `${trace.evaluation.overall_score * 100}%` }} />
          </div>
          <span className="confidence-value">{Math.round(trace.evaluation.overall_score * 100)}%</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <EvalCheck label="Grounded" state={trace.evaluation.grounded ? 'pass' : 'fail'} detail={trace.evaluation.grounded_explanation} />
          <EvalCheck label="Policy Consistent" state={trace.evaluation.policy_consistent ? 'pass' : 'fail'} detail={trace.evaluation.policy_consistent_explanation} />
          <EvalCheck label="Escalation Decision Correct" state={trace.evaluation.escalation_decision_correct ? 'pass' : 'fail'} detail={trace.evaluation.escalation_explanation} />
          <EvalCheck label="Retrieval Sufficient" state={trace.evaluation.retrieval_sufficient ? 'pass' : 'fail'} detail={trace.evaluation.retrieval_explanation} />
          <EvalCheck
            label="Retrieval Quality"
            state={trace.evaluation.retrieval_quality === 'clean' ? 'pass' : trace.evaluation.retrieval_quality === 'minor_issues' ? 'warn' : 'fail'}
            detail={trace.evaluation.retrieval_quality_explanation || 'No quality issues detected.'}
          />
        </div>
        {trace.evaluation.details && (
          <div style={{ marginTop: '16px', padding: '12px', background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)', fontSize: 'var(--text-sm)', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            {trace.evaluation.details}
          </div>
        )}
      </div>

      {/* Improvement Suggestion */}
      {trace.improvement_suggestion && (
        <div className="improvement-box" style={{ marginTop: '16px' }}>
          <div className="improvement-title">💡 Suggested Improvement</div>
          <div className="improvement-text">{trace.improvement_suggestion}</div>
        </div>
      )}
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
