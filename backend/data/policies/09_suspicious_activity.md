# Policy: Suspicious Activity Triggers

**Policy ID:** POL-009  
**Effective Date:** January 1, 2024  
**Category:** Fraud Prevention  
**Priority:** Critical

## 1. Velocity-Based Triggers

The following transaction velocity patterns trigger automatic review:
- 3+ refund requests in 7 days
- 5+ refund requests in 30 days
- Refund-to-purchase ratio exceeding 40% over any 90-day period
- Total refund amount exceeding 50% of total purchase amount in 6 months

## 2. Behavioral Triggers

- Customer contacts multiple channels simultaneously about the same issue
- Conflicting information provided across different interactions
- Request timing correlates with known fraud windows (e.g., immediately after promotional periods)
- Unusual payment method changes before refund request

## 3. Account-Based Triggers

- New account (less than 30 days) with high-value refund request
- Account information recently changed (email, phone, address) before refund request
- Multiple accounts linked to the same payment method or address
- Account associated with previously flagged accounts

## 4. Auto-Hold Rules

When suspicious activity is detected:
1. **Immediate hold**: Refund processing is paused
2. **Flag level assignment**: Low / Medium / High suspicion
3. **Notification**: Fraud prevention team is alerted
4. **Customer communication**: Neutral hold notification sent
5. **Investigation window**: 48-72 hours for team to investigate

## 5. Resolution

- **Cleared**: Refund proceeds normally, flag is removed
- **Confirmed suspicious**: Case escalated to fraud review (POL-003)
- **Confirmed fraud**: Account flagged, refund denied, potential legal action
