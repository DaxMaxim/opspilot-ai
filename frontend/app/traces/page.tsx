'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import type { TraceListItem, TraceListResponse } from '@/lib/types';
import { getTraces } from '@/lib/api';

export default function TracesPage() {
  const router = useRouter();
  const [traces, setTraces] = useState<TraceListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const limit = 20;

  useEffect(() => {
    loadTraces();
  }, [page]);

  const loadTraces = async () => {
    setLoading(true);
    try {
      const data = await getTraces(page, limit);
      setTraces(data.traces);
      setTotal(data.total);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load traces');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (iso: string) => {
    return new Date(iso).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatCaseType = (ct: string) => {
    return ct.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="flex-between">
          <div>
            <h1 className="page-title">Trace History</h1>
            <p className="page-subtitle">
              {total} decision traces recorded
            </p>
          </div>
          <a href="/review" className="btn btn-primary">
            New Case Review →
          </a>
        </div>
      </div>

      {loading && (
        <div className="card loading-overlay">
          <div className="spinner" />
          <div>Loading traces...</div>
        </div>
      )}

      {error && (
        <div className="error-box">
          <div className="error-title">Failed to Load</div>
          <div className="error-text">{error}</div>
          <button className="btn btn-secondary" style={{ marginTop: '16px' }} onClick={loadTraces}>
            Retry
          </button>
        </div>
      )}

      {!loading && !error && traces.length === 0 && (
        <div className="card empty-state">
          <div className="empty-state-icon">📊</div>
          <div className="empty-state-title">No Traces Yet</div>
          <div className="empty-state-text">
            Run a case review to generate decision traces. Each trace captures
            the full workflow execution with inputs, outputs, and evaluation.
          </div>
          <a href="/review" className="btn btn-primary" style={{ marginTop: '20px' }}>
            Submit First Case →
          </a>
        </div>
      )}

      {!loading && !error && traces.length > 0 && (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Case Type</th>
                <th>Decision</th>
                <th>Confidence</th>
                <th>Grounded</th>
                <th>Policy</th>
                <th>Duration</th>
              </tr>
            </thead>
            <tbody>
              {traces.map((trace) => (
                <tr
                  key={trace.id}
                  onClick={() => router.push(`/traces/${trace.id}`)}
                >
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)' }}>
                    {formatDate(trace.created_at)}
                  </td>
                  <td>{formatCaseType(trace.case_type)}</td>
                  <td>
                    <span className={`decision-badge ${trace.decision.toLowerCase().replace(/_/g, '_')}`}>
                      {trace.decision === 'NEED_MORE_INFO' ? 'MORE INFO' : trace.decision}
                    </span>
                  </td>
                  <td>
                    <span className="confidence-value" style={{ fontSize: 'var(--text-sm)' }}>
                      {Math.round(trace.confidence * 100)}%
                    </span>
                  </td>
                  <td>
                    <span className={`eval-icon ${trace.grounded ? 'pass' : 'fail'}`} style={{ display: 'inline-flex' }}>
                      {trace.grounded ? '✓' : '✗'}
                    </span>
                  </td>
                  <td>
                    <span className={`eval-icon ${trace.policy_consistent ? 'pass' : 'fail'}`} style={{ display: 'inline-flex' }}>
                      {trace.policy_consistent ? '✓' : '✗'}
                    </span>
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>
                    {(trace.duration_ms / 1000).toFixed(1)}s
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {total > limit && (
        <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginTop: '24px' }}>
          <button
            className="btn btn-ghost btn-sm"
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
          >
            ← Previous
          </button>
          <span style={{ padding: '6px 12px', fontSize: 'var(--text-sm)', color: 'var(--text-tertiary)' }}>
            Page {page} of {Math.ceil(total / limit)}
          </span>
          <button
            className="btn btn-ghost btn-sm"
            disabled={page * limit >= total}
            onClick={() => setPage((p) => p + 1)}
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
}
