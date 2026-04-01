/* OpsPilot AI — Backend API Client */

import type {
  CaseInput,
  DecisionOutput,
  TraceListResponse,
  TraceDetail,
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }

  return res.json();
}

export async function reviewCase(caseInput: CaseInput): Promise<DecisionOutput> {
  return fetchAPI<DecisionOutput>('/api/cases/review', {
    method: 'POST',
    body: JSON.stringify(caseInput),
  });
}

export async function getTraces(page = 1, limit = 20): Promise<TraceListResponse> {
  return fetchAPI<TraceListResponse>(`/api/traces?page=${page}&limit=${limit}`);
}

export async function getTraceDetail(traceId: string): Promise<TraceDetail> {
  return fetchAPI<TraceDetail>(`/api/traces/${traceId}`);
}

export async function seedData(): Promise<{ status: string; chunks_indexed: number }> {
  return fetchAPI('/api/seed', { method: 'POST' });
}

export async function healthCheck(): Promise<{ status: string }> {
  return fetchAPI('/api/health');
}
