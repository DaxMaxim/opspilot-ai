# Policy: Fraud Review Rules

**Policy ID:** POL-003  
**Effective Date:** January 1, 2024  
**Category:** Fraud  
**Priority:** Critical

## 1. Automatic Fraud Review Triggers

A case is flagged for fraud review if ANY of the following conditions are met:
- 3 or more refund requests within a 90-day period
- 5 or more refund requests within a 12-month period
- Refund amount exceeds $1,000 on a single transaction
- Customer account is less than 30 days old at time of request
- Shipping address differs from billing address AND account was created recently
- Multiple claims of "item not received" from the same customer

## 2. Investigation Process

1. **Auto-hold**: The refund request is placed on hold pending review
2. **Pattern analysis**: System reviews customer's full transaction and refund history
3. **Risk scoring**: A risk score is calculated based on behavioral patterns
4. **Decision**: Senior reviewer makes final determination

## 3. Auto-Deny Criteria

A request is automatically denied if:
- The customer has been previously flagged for confirmed fraud
- The account is on the fraud watchlist
- Transaction patterns match known fraud signatures
- The customer has provided falsified documentation

## 4. Escalation

- Suspected fraud cases are escalated to the Fraud Prevention Team
- SLA for fraud review: 48 hours for standard, 24 hours for high-value
- Law enforcement referral for confirmed fraud over $5,000

## 5. Customer Communication

- Customers are notified of the hold but NOT informed of the fraud investigation
- Communication uses neutral language: "Your request requires additional review"
