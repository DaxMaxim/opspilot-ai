# Policy: Escalation Criteria

**Policy ID:** POL-007  
**Effective Date:** January 1, 2024  
**Category:** Escalation  
**Priority:** High

## 1. Automatic Escalation Triggers

Cases must be escalated when ANY of the following conditions are met:
- Transaction value exceeds $500
- Customer is VIP tier (Gold, Platinum, or Diamond)
- Case involves potential fraud indicators
- Standard policy does not clearly cover the situation
- Customer has submitted a formal complaint
- Case requires manual override of automated decision

## 2. Priority Mapping

| Priority | SLA | Queue | Handler |
|----------|-----|-------|---------|
| Low | 72 hours | General Review | Senior Agent |
| Medium | 48 hours | Priority Review | Team Lead |
| High | 24 hours | Urgent Review | Manager |
| Critical | 4 hours | Executive Review | Director |

## 3. Escalation Process

1. **Auto-classification**: System determines escalation priority based on triggers
2. **Queue assignment**: Case is routed to the appropriate review queue
3. **Notification**: Assigned handler receives immediate notification
4. **SLA tracking**: Timer starts from the moment of escalation
5. **Resolution**: Handler reviews and makes final decision

## 4. Escalation Decision Authority

- **Senior Agent**: May approve/deny cases up to $500
- **Team Lead**: May approve/deny cases up to $2,000
- **Manager**: May approve/deny cases up to $10,000 and override policies
- **Director**: Unlimited authority, handles all critical cases

## 5. SLA Breach Protocol

If SLA is breached:
- Automatic re-escalation to the next priority level
- Notification sent to handler's supervisor
- Case is flagged in the compliance audit trail
