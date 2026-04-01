/* OpsPilot AI — TypeScript Types */

export interface CaseInput {
  case_type: 'refund_request' | 'claim_review' | 'exception_request' | 'fraud_investigation' | 'escalation';
  customer_id: string;
  amount: number;
  purchase_date: string;
  request_date: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  description: string;
}

export interface PolicyCitation {
  policy_id: string;
  policy_name: string;
  section: string;
  relevant_text: string;
}

export interface RetrievedPolicy {
  policy_id: string;
  policy_name: string;
  content: string;
  relevance_score: number;
}

export interface ToolCallResult {
  tool_name: string;
  input_data: Record<string, unknown>;
  output_data: Record<string, unknown>;
  execution_time_ms: number;
}

export interface EvaluationResult {
  grounded: boolean;
  grounded_explanation: string;
  policy_consistent: boolean;
  policy_consistent_explanation: string;
  escalation_decision_correct: boolean;
  escalation_explanation: string;
  retrieval_sufficient: boolean;
  retrieval_explanation: string;
  retrieval_quality: 'clean' | 'minor_issues' | 'poor';
  retrieval_quality_explanation: string;
  overall_score: number;
  details: string;
}

export interface WhyThisDecision {
  policy_clause_used: string;
  key_condition_matched: string;
  key_constraint_triggered: string;
}

export type Decision = 'APPROVE' | 'DENY' | 'ESCALATE' | 'NEED_MORE_INFO';

export interface DecisionOutput {
  decision: Decision;
  confidence: number;
  reason: string;
  why_this_decision: WhyThisDecision;
  policy_citations: PolicyCitation[];
  retrieved_policies: RetrievedPolicy[];
  tool_calls: ToolCallResult[];
  evaluation: EvaluationResult;
  improvement_suggestion: string | null;
  trace_id: string;
}

export interface TraceListItem {
  id: string;
  created_at: string;
  case_type: string;
  decision: Decision;
  confidence: number;
  grounded: boolean;
  policy_consistent: boolean;
  duration_ms: number;
}

export interface TraceListResponse {
  traces: TraceListItem[];
  total: number;
  page: number;
  limit: number;
}

export interface NodeTrace {
  node: string;
  timestamp: string;
  duration_ms: number;
  output_summary: string;
}

export interface TraceDetail {
  id: string;
  created_at: string;
  case_input: CaseInput;
  case_type: string;
  decision: Decision;
  confidence: number;
  reason: string;
  why_this_decision: WhyThisDecision;
  retrieved_policies: RetrievedPolicy[];
  policy_citations: PolicyCitation[];
  tool_calls: ToolCallResult[];
  evaluation: EvaluationResult;
  improvement_suggestion: string | null;
  workflow_trace: NodeTrace[];
  duration_ms: number;
}

export interface SampleCase {
  title: string;
  description: string;
  expectedOutcome: string;
  data: CaseInput;
}
