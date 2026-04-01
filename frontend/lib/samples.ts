import type { SampleCase } from './types';

export const SAMPLE_CASES: SampleCase[] = [
  {
    title: 'Standard Refund — Within Window',
    description: 'Routine refund request within 30-day policy window. Low risk.',
    expectedOutcome: 'APPROVE',
    data: {
      case_type: 'refund_request',
      customer_id: 'CUST-1042',
      amount: 49.99,
      purchase_date: new Date(Date.now() - 15 * 86400000).toISOString().split('T')[0],
      request_date: new Date().toISOString().split('T')[0],
      priority: 'low',
      description: 'Customer requests full refund on unused product. Within 30-day standard window. Product sealed and unopened.',
    },
  },
  {
    title: 'VIP Exception — Outside Window',
    description: 'Platinum VIP requests refund 47 days after purchase. 3rd exception.',
    expectedOutcome: 'ESCALATE',
    data: {
      case_type: 'exception_request',
      customer_id: 'CUST-7721',
      amount: 299.0,
      purchase_date: new Date(Date.now() - 47 * 86400000).toISOString().split('T')[0],
      request_date: new Date().toISOString().split('T')[0],
      priority: 'high',
      description: 'VIP Platinum customer requesting refund 47 days after purchase. This is their third exception request this year. Customer states product did not meet expectations.',
    },
  },
  {
    title: 'Repeated Returns — Suspicious Pattern',
    description: '4th refund this year. Pattern of purchasing and returning. $89 order.',
    expectedOutcome: 'DENY',
    data: {
      case_type: 'refund_request',
      customer_id: 'CUST-9381',
      amount: 89.5,
      purchase_date: new Date(Date.now() - 97 * 86400000).toISOString().split('T')[0],
      request_date: new Date().toISOString().split('T')[0],
      priority: 'medium',
      description: 'Customer requesting fourth refund this year. Pattern of purchasing and returning within 30 days. Claims dissatisfaction. Outside refund window by 67 days.',
    },
  },
  {
    title: 'Damaged Goods — Missing Documentation',
    description: 'High-value $650 item. Claims damage but no photos submitted.',
    expectedOutcome: 'NEED_MORE_INFO',
    data: {
      case_type: 'claim_review',
      customer_id: 'CUST-5564',
      amount: 650.0,
      purchase_date: new Date(Date.now() - 27 * 86400000).toISOString().split('T')[0],
      request_date: new Date().toISOString().split('T')[0],
      priority: 'high',
      description: 'Customer claims product arrived damaged. High-value item at $650. No photographic evidence provided. Requesting full refund. Missing mandatory damage documentation.',
    },
  },
];
