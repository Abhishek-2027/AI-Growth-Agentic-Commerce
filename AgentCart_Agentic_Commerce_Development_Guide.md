# AgentCart — Safe Agentic Commerce System

## Complete Development, Architecture, Workflow, Module, Payment, and Implementation Guide

---

# 1. Project Overview

## Project Name

**AgentCart — Safe AI-to-Merchant Commerce**

## Hackathon Track

**AI Growth & Agentic Commerce**

## Core Idea

Build an AI-powered commerce system where an AI agent can understand a buyer's request, discover products from a merchant, recommend or select a suitable product, enforce spending and safety constraints, obtain user approval, create a payment order using Razorpay Test Mode, process the payment, and maintain a complete audit trail.

The system is not just a chatbot.

The important behavior is:

```text
AI Agent → Proposes a commerce action
Backend Policy Engine → Validates the action
User → Approves sensitive money action
Backend → Creates payment order
Razorpay → Processes test payment
System → Records the complete audit trail
```

---

# 2. Problem Statement in Simple Words

The problem asks us to build an AI agent that can participate in commerce.

The agent can either:

1. Help a merchant increase revenue.
2. Allow an AI buyer to discover and transact with a merchant.

This project focuses on the second direction:

> A buyer communicates what they want to an AI agent, and the agent can discover products, reason about the options, create a safe purchase proposal, and complete the transaction through Razorpay Test Mode after approval.

Example:

```text
User:
"I want wireless noise-cancelling headphones under ₹5,000."

                ↓

AI understands:
Product = headphones
Requirements = wireless + noise cancellation
Maximum budget = ₹5,000

                ↓

AI searches merchant catalog

                ↓

AI compares available products

                ↓

AI recommends/selects product

                ↓

Policy Engine checks:
✓ Budget
✓ Stock
✓ Product availability
✓ Action permissions

                ↓

User approval

                ↓

Razorpay order creation

                ↓

Razorpay Test Mode checkout

                ↓

Payment result

                ↓

Audit trail
```

---

# 3. Main Requirements

The system must satisfy the following requirements.

## 3.1 AI Agent

The AI agent should:

- Understand natural language requests.
- Extract product requirements.
- Search products.
- Compare products.
- Recommend a suitable option.
- Explain why the recommendation was made.
- Propose actions rather than directly controlling money.

## 3.2 Money Safety

Every money-related action should be:

### Explainable

The system should show:

```text
What action happened?
Why did it happen?
What amount was involved?
What constraints were checked?
Who approved it?
What was the final result?
```

### Bounded

The agent must operate within explicit limits.

Examples:

```text
Maximum purchase budget = ₹5,000
Maximum quantity = 1
Allowed currency = INR
Allowed merchant = AgentCart Demo Merchant
```

If the agent proposes a ₹8,000 product when the budget is ₹5,000:

```text
Agent Proposal → ₹8,000

Policy Engine:
₹8,000 > ₹5,000

Result → BLOCKED
```

The LLM must not be able to override deterministic backend rules.

### Gated

High-risk actions require approval.

Example:

```text
Search products
    ↓
No approval required

Recommend product
    ↓
No approval required

Create payment order
    ↓
Policy validation required

Complete payment
    ↓
User approval required
```

## 3.3 Audit Trail

Every important action should be recorded.

Example:

```text
10:00:01 → User request received
10:00:02 → Intent extracted
10:00:03 → Catalog searched
10:00:05 → Product selected
10:00:06 → Reason generated
10:00:07 → Budget validated
10:00:08 → Approval requested
10:00:15 → User approved
10:00:17 → Razorpay order created
10:00:25 → Payment successful
```

## 3.4 Failure Handling

At least one realistic failure should be handled.

Recommended demo:

```text
Payment attempt
      ↓
Payment fails
      ↓
System records failure
      ↓
No duplicate payment is created
      ↓
Order remains in failed/pending state
      ↓
User sees retry or cancel option
```

---

# 4. Technology Stack

## Frontend

- React
- Tailwind CSS
- React Router
- Axios or Fetch API
- Razorpay Checkout JavaScript SDK

## Backend

- FastAPI
- Python
- Pydantic
- Motor or PyMongo for MongoDB
- LangGraph for agent workflow
- LLM provider SDK
- Razorpay Python SDK

## Database

- MongoDB Atlas

MongoDB Atlas collections can include:

```text
users
products
orders
agent_sessions
agent_actions
audit_logs
payment_events
policies
merchant_profiles
```

---

# 5. High-Level Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                            │
│                                                             │
│                 React + Tailwind CSS                        │
│                                                             │
│  Chat │ Product Results │ Approval │ Payment │ Audit Trail  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               │ HTTPS REST API
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                       FASTAPI BACKEND                       │
│                                                             │
│ API Layer                                                   │
│ Agent Orchestrator                                          │
│ Policy Engine                                               │
│ Product Service                                             │
│ Order Service                                               │
│ Payment Service                                             │
│ Audit Service                                               │
└───────────────┬───────────────────┬─────────────────────────┘
                │                   │
                ▼                   ▼
       ┌────────────────┐   ┌────────────────────┐
       │   AI AGENT     │   │   MONGODB ATLAS    │
       │   LangGraph    │   │                    │
       │                │   │ Products           │
       │ Tool Calling   │   │ Orders             │
       │ Reasoning      │   │ Audit Logs         │
       └───────┬────────┘   │ Payment Events     │
               │            └────────────────────┘
               ▼
       ┌────────────────┐
       │ Agent Tools    │
       │                │
       │ Search Catalog │
       │ Get Product    │
       │ Create Proposal│
       └───────┬────────┘
               │
               ▼
       ┌────────────────────────┐
       │ Policy + Approval Gate │
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │ Razorpay Payment Layer │
       │       Test Mode        │
       └────────────────────────┘
```

---

# 6. Complete End-to-End Workflow

```text
┌──────────┐
│   USER   │
└────┬─────┘
     │ Natural language request
     ▼
┌──────────────────────┐
│   REACT FRONTEND     │
│ Chat Interface       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ FASTAPI AGENT API    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ UNDERSTAND INTENT    │
│ Product              │
│ Budget               │
│ Requirements         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ SEARCH CATALOG TOOL  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   MONGODB ATLAS      │
│   PRODUCTS           │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ AGENT RECOMMENDATION │
│ + EXPLANATION        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ POLICY ENGINE        │
│ Budget               │
│ Stock                │
│ Permissions          │
└──────────┬───────────┘
           │
       ┌───┴────┐
       │        │
    BLOCKED   APPROVED
       │        │
       ▼        ▼
     END   USER APPROVAL
                  │
              ┌───┴────┐
              │        │
             NO       YES
              │        │
              ▼        ▼
             END  CREATE ORDER
                         │
                         ▼
                    RAZORPAY
                    TEST MODE
                         │
                   ┌─────┴─────┐
                   │           │
                FAILURE      SUCCESS
                   │           │
                   ▼           ▼
             HANDLE ERROR   COMPLETE
                   │           │
                   └─────┬─────┘
                         ▼
                   AUDIT LOG
```

---

# 7. Frontend Architecture

The frontend should not contain business-critical payment validation.

The frontend is responsible for:

- User interaction.
- Displaying products.
- Displaying AI decisions.
- Asking for approval.
- Opening Razorpay Checkout.
- Displaying payment result.
- Showing audit trail.

## Recommended Pages

```text
/
├── /dashboard
├── /shop
├── /agent
├── /checkout
├── /orders
└── /audit
```

## Recommended React Structure

```text
frontend/
│
├── src/
│   ├── api/
│   │   ├── client.js
│   │   ├── agentApi.js
│   │   ├── productApi.js
│   │   └── paymentApi.js
│   │
│   ├── components/
│   │   ├── AgentChat.jsx
│   │   ├── ProductCard.jsx
│   │   ├── ProductList.jsx
│   │   ├── RecommendationCard.jsx
│   │   ├── ApprovalModal.jsx
│   │   ├── PaymentStatus.jsx
│   │   ├── AuditTimeline.jsx
│   │   └── PolicyStatus.jsx
│   │
│   ├── pages/
│   │   ├── Dashboard.jsx
│   │   ├── AgentPage.jsx
│   │   ├── CheckoutPage.jsx
│   │   ├── OrdersPage.jsx
│   │   └── AuditPage.jsx
│   │
│   ├── hooks/
│   │   └── useAgent.js
│   │
│   ├── App.jsx
│   └── main.jsx
│
└── package.json
```

---

# 8. Main Frontend Screens

## Screen 1: AI Shopping Agent

```text
┌─────────────────────────────────────────────┐
│ AGENTCART AI                                │
├─────────────────────────────────────────────┤
│                                             │
│ User:                                       │
│ I want wireless headphones under ₹5,000     │
│                                             │
│ AI Agent:                                   │
│ I found 3 suitable products.                │
│                                             │
│ [Product A] [Product B] [Product C]         │
│                                             │
└─────────────────────────────────────────────┘
```

## Screen 2: Recommendation

```text
┌─────────────────────────────────────────────┐
│ AI RECOMMENDATION                           │
├─────────────────────────────────────────────┤
│ Sony Wireless Headphones                    │
│ ₹4,500                                      │
│                                             │
│ WHY THIS PRODUCT?                           │
│ ✓ Within your ₹5,000 budget                 │
│ ✓ Wireless                                  │
│ ✓ Noise cancellation                        │
│ ✓ Available in stock                        │
│                                             │
│ [Continue]                                  │
└─────────────────────────────────────────────┘
```

## Screen 3: Policy Gate

```text
┌─────────────────────────────────────────────┐
│ SAFETY CHECK                                │
├─────────────────────────────────────────────┤
│ Budget: ₹5,000                              │
│ Product Price: ₹4,500                       │
│                                             │
│ ✓ Budget check passed                       │
│ ✓ Product available                         │
│ ✓ Quantity allowed                          │
│                                             │
│ STATUS: APPROVED                            │
└─────────────────────────────────────────────┘
```

## Screen 4: Approval

```text
┌─────────────────────────────────────────────┐
│ PAYMENT APPROVAL                            │
├─────────────────────────────────────────────┤
│ Product: Sony Headphones                    │
│ Amount: ₹4,500                              │
│                                             │
│ Reason for purchase:                        │
│ Matches your request and budget.            │
│                                             │
│ [Cancel]      [Approve Payment]             │
└─────────────────────────────────────────────┘
```

## Screen 5: Audit Trail

```text
┌─────────────────────────────────────────────┐
│ AGENT AUDIT TRAIL                           │
├─────────────────────────────────────────────┤
│ ✓ User intent extracted                     │
│ ✓ Merchant catalog searched                 │
│ ✓ Product selected                          │
│ ✓ Budget validated                          │
│ ✓ User approved                             │
│ ✓ Razorpay order created                    │
│ ✓ Payment successful                        │
└─────────────────────────────────────────────┘
```

---

# 9. Backend Architecture

Recommended structure:

```text
backend/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── agent.py
│   │   ├── products.py
│   │   ├── orders.py
│   │   ├── payments.py
│   │   └── audit.py
│   │
│   ├── agents/
│   │   ├── state.py
│   │   ├── graph.py
│   │   ├── nodes.py
│   │   └── prompts.py
│   │
│   ├── tools/
│   │   ├── catalog_tools.py
│   │   └── product_tools.py
│   │
│   ├── services/
│   │   ├── policy_service.py
│   │   ├── recommendation_service.py
│   │   ├── order_service.py
│   │   ├── payment_service.py
│   │   └── audit_service.py
│   │
│   ├── db/
│   │   └── mongodb.py
│   │
│   ├── models/
│   │   ├── product.py
│   │   ├── order.py
│   │   ├── payment.py
│   │   └── audit.py
│   │
│   └── core/
│       ├── config.py
│       └── security.py
│
├── requirements.txt
└── .env
```

---

# 10. FastAPI Modules

## Agent API

Example:

```text
POST /api/agent/chat
```

Input:

```json
{
  "message": "I want wireless headphones under ₹5,000",
  "session_id": "session_123"
}
```

Output:

```json
{
  "intent": {
    "product": "wireless headphones",
    "budget": 5000
  },
  "recommendations": [],
  "agent_response": "I found suitable products."
}
```

---

# 11. Agent Architecture

The agent should use tools.

```text
LLM
 │
 │ Understands request
 ▼
Tool Selection
 │
 ├── search_catalog()
 ├── get_product()
 ├── check_stock()
 └── create_purchase_proposal()
```

Important rule:

```text
The LLM should not directly execute unrestricted money actions.
```

Instead:

```text
LLM
 ↓
Purchase Proposal
 ↓
Deterministic Policy Engine
 ↓
Approval Gate
 ↓
Payment Service
 ↓
Razorpay
```

---

# 12. LangGraph Workflow

Recommended graph:

```text
START
  │
  ▼
UNDERSTAND_REQUEST
  │
  ▼
SEARCH_CATALOG
  │
  ▼
ANALYZE_PRODUCTS
  │
  ▼
SELECT_PRODUCT
  │
  ▼
CREATE_EXPLANATION
  │
  ▼
POLICY_CHECK
  │
  ├──────────────→ BLOCKED → AUDIT → END
  │
  ▼
WAIT_FOR_APPROVAL
  │
  ├──────────────→ REJECTED → AUDIT → END
  │
  ▼
CREATE_PAYMENT_ORDER
  │
  ▼
WAIT_FOR_PAYMENT_RESULT
  │
  ├──────────────→ FAILED → HANDLE_FAILURE → AUDIT
  │
  ▼
SUCCESS
  │
  ▼
AUDIT
  │
  ▼
END
```

---

# 13. Agent State

Example conceptual state:

```python
class AgentState:
    session_id
    user_message
    intent
    products
    selected_product
    recommendation_reason
    policy_result
    approval_status
    order_id
    payment_status
    error
```

A possible structured representation:

```json
{
  "session_id": "session_123",
  "user_message": "Buy headphones under ₹5,000",
  "intent": {},
  "products": [],
  "selected_product": {},
  "recommendation_reason": "",
  "policy_result": {},
  "approval_status": "pending",
  "order_id": null,
  "payment_status": null
}
```

---

# 14. Agent Tools

## Tool 1: Search Catalog

```text
search_catalog(
    query,
    max_price,
    required_features
)
```

Example:

```text
search_catalog(
    query="wireless headphones",
    max_price=5000,
    required_features=["noise cancellation"]
)
```

The backend queries MongoDB Atlas.

---

## Tool 2: Get Product Details

```text
get_product(product_id)
```

Returns authoritative product data.

The price should be read from the database, not trusted from the LLM.

---

## Tool 3: Check Availability

```text
check_stock(product_id, quantity)
```

Returns:

```json
{
  "available": true,
  "stock": 10
}
```

---

## Tool 4: Create Purchase Proposal

This does not create payment.

It creates:

```json
{
  "product_id": "product_123",
  "quantity": 1,
  "expected_amount": 4500,
  "reason": "Matches user requirements and budget"
}
```

---

# 15. Policy Engine

This module should be deterministic Python code.

It should validate:

```text
1. Product exists
2. Product is available
3. Quantity is valid
4. Price is valid
5. Budget is not exceeded
6. Currency is allowed
7. User approval is present before payment
```

Workflow:

```text
AI Proposal
    │
    ▼
Get authoritative product from database
    │
    ▼
Calculate actual amount
    │
    ▼
Compare with policy
    │
    ├── Invalid → BLOCK
    │
    ▼
APPROVE FOR NEXT STEP
```

Example:

```python
if actual_amount > max_budget:
    return {
        "approved": False,
        "reason": "Budget exceeded"
    }
```

---

# 16. MongoDB Atlas Database Design

## Collection: products

```json
{
  "_id": "product_123",
  "name": "Sony Wireless Headphones",
  "description": "Wireless headphones with noise cancellation",
  "price": 4500,
  "currency": "INR",
  "category": "electronics",
  "features": [
    "wireless",
    "noise cancellation"
  ],
  "stock": 10,
  "active": true
}
```

---

## Collection: orders

```json
{
  "_id": "order_123",
  "user_id": "user_123",
  "product_id": "product_123",
  "quantity": 1,
  "amount": 4500,
  "currency": "INR",
  "status": "payment_pending",
  "razorpay_order_id": "order_xxx",
  "created_at": "timestamp"
}
```

---

## Collection: audit_logs

```json
{
  "_id": "audit_123",
  "session_id": "session_123",
  "timestamp": "timestamp",
  "actor": "agent",
  "action": "SELECT_PRODUCT",
  "reason": "Best match within budget",
  "data": {
    "product_id": "product_123"
  },
  "status": "success"
}
```

---

## Collection: payment_events

```json
{
  "_id": "payment_event_123",
  "order_id": "order_123",
  "razorpay_order_id": "order_xxx",
  "razorpay_payment_id": "pay_xxx",
  "status": "success",
  "created_at": "timestamp"
}
```

---

## Collection: policies

```json
{
  "_id": "policy_default",
  "max_purchase_amount": 5000,
  "max_quantity": 1,
  "currency": "INR",
  "require_user_approval": true
}
```

---

# 17. Payment Architecture

The payment flow should be separated from the AI decision-making flow.

```text
AI AGENT
    │
    │ Proposes product
    ▼
POLICY ENGINE
    │
    │ Validates constraints
    ▼
USER APPROVAL
    │
    │ Explicit approval
    ▼
ORDER SERVICE
    │
    │ Reads actual product price
    ▼
PAYMENT SERVICE
    │
    │ Creates Razorpay order
    ▼
RAZORPAY TEST MODE
    │
    ▼
REACT CHECKOUT
    │
    ▼
PAYMENT CALLBACK / VERIFICATION
    │
    ▼
ORDER STATUS UPDATE
    │
    ▼
AUDIT LOG
```

---

# 18. Razorpay Payment Flow

## Step 1: User approves

The frontend sends:

```text
POST /api/orders/{order_id}/approve
```

The backend stores approval.

---

## Step 2: Backend creates Razorpay Order

Important:

The frontend should not decide the payment amount.

The backend should:

```text
Product ID
   ↓
Read product from MongoDB
   ↓
Get authoritative price
   ↓
Validate policy again
   ↓
Calculate amount
   ↓
Create Razorpay Order
```

Conceptually:

```python
razorpay_client.order.create({
    "amount": amount_in_paise,
    "currency": "INR",
    "receipt": internal_order_id
})
```

For ₹4,500:

```text
Razorpay amount = 450000 paise
```

---

## Step 3: Return Order Information to Frontend

Example:

```json
{
  "internal_order_id": "internal_123",
  "razorpay_order_id": "order_xxx",
  "amount": 450000,
  "currency": "INR",
  "key_id": "public_test_key"
}
```

The backend secret must never be exposed to the frontend.

---

## Step 4: Open Razorpay Checkout

The React frontend loads Razorpay Checkout and passes the backend-generated order ID.

```text
React
  ↓
Receive Razorpay order details
  ↓
Open Razorpay Checkout
  ↓
User completes test payment
  ↓
Receive payment response
  ↓
Send verification data to FastAPI
```

---

## Step 5: Verify Payment

Frontend sends payment response to:

```text
POST /api/payments/verify
```

The backend verifies the payment response/signature using the Razorpay secret.

Only after verification should the order be marked successful.

```text
Payment response
      ↓
Backend verification
      ↓
Valid?
   ┌──┴──┐
   │     │
  NO    YES
   │     │
FAILED SUCCESS
```

---

# 19. Payment Safety Rules

## Rule 1

Never trust price sent from the frontend.

Bad:

```json
{
  "product_id": "P123",
  "amount": 1
}
```

Good:

```json
{
  "product_id": "P123"
}
```

Backend:

```text
P123
 ↓
MongoDB product lookup
 ↓
Actual price = ₹4,500
 ↓
Use ₹4,500
```

## Rule 2

Never allow the LLM to directly provide the final payment amount.

The LLM may propose a product.

The backend determines the final amount.

## Rule 3

Require approval before payment.

## Rule 4

Verify payment on the backend.

## Rule 5

Prevent duplicate payment/order processing.

Use internal order states and idempotent handling.

---

# 20. Order State Machine

```text
CREATED
   │
   ▼
POLICY_APPROVED
   │
   ▼
AWAITING_USER_APPROVAL
   │
   ├────→ CANCELLED
   │
   ▼
APPROVED
   │
   ▼
RAZORPAY_ORDER_CREATED
   │
   ▼
PAYMENT_PENDING
   │
   ├────→ PAYMENT_FAILED
   │
   ▼
PAYMENT_VERIFIED
   │
   ▼
COMPLETED
```

This state machine prevents unclear transaction behavior.

---

# 21. Failure Handling

Recommended failure demonstration:

## Payment Failure

```text
PAYMENT_PENDING
       │
       ▼
Razorpay failure
       │
       ▼
PAYMENT_FAILED
       │
       ├── Log audit event
       ├── Record payment event
       ├── Do not mark order complete
       ├── Do not automatically duplicate charge
       │
       ▼
Show options:
[Retry]
[Cancel]
```

The audit trail should explain:

```text
Action:
PAYMENT_FAILED

Reason:
Payment provider returned a failed transaction.

System Action:
Order was not completed.
No duplicate payment was created.
User can retry.
```

---

# 22. API Design

## Agent APIs

```text
POST /api/agent/chat
GET  /api/agent/session/{session_id}
```

## Product APIs

```text
GET /api/products
GET /api/products/{product_id}
POST /api/products/search
```

## Purchase APIs

```text
POST /api/purchase/propose
POST /api/purchase/{proposal_id}/approve
POST /api/purchase/{proposal_id}/reject
```

## Payment APIs

```text
POST /api/payments/create-order
POST /api/payments/verify
GET  /api/payments/{order_id}/status
```

## Audit APIs

```text
GET /api/audit/{session_id}
GET /api/orders/{order_id}/audit
```

---

# 23. Main Backend Sequence

```text
1. POST /agent/chat
        ↓
2. Agent extracts intent
        ↓
3. Agent searches MongoDB catalog
        ↓
4. Agent recommends product
        ↓
5. Create purchase proposal
        ↓
6. Policy engine validates
        ↓
7. Frontend displays proposal
        ↓
8. User clicks Approve
        ↓
9. Backend records approval
        ↓
10. Backend creates Razorpay order
        ↓
11. React opens Razorpay Checkout
        ↓
12. Payment response received
        ↓
13. Backend verifies payment
        ↓
14. Update order status
        ↓
15. Write audit events
```

---

# 24. Audit Trail Architecture

Every important module should call the audit service.

```text
AGENT
  │
  ├── intent extraction event
  ├── product search event
  └── recommendation event

POLICY ENGINE
  │
  └── validation event

APPROVAL SERVICE
  │
  └── approval event

PAYMENT SERVICE
  │
  ├── order creation event
  ├── payment verification event
  └── failure event
```

All events:

```text
        ↓
   AUDIT SERVICE
        ↓
  MONGODB ATLAS
```

---

# 25. Recommended Development Order

## Phase 1 — Project Setup

Create:

```text
React + Vite
Tailwind CSS
FastAPI
MongoDB Atlas connection
Environment variables
```

Test:

```text
Frontend → FastAPI → MongoDB Atlas
```

---

## Phase 2 — Merchant Catalog

Create:

```text
products collection
product APIs
product search
```

Test:

```text
GET /products
POST /products/search
```

---

## Phase 3 — Agent

Create:

```text
LangGraph
Agent state
Intent node
Catalog search node
Recommendation node
```

Test:

```text
User message
↓
Intent
↓
Product search
↓
Recommendation
```

---

## Phase 4 — Policy Engine

Add:

```text
Budget validation
Stock validation
Quantity validation
Approval requirement
```

Test blocked cases.

Example:

```text
Budget = ₹5,000
Product = ₹8,000

Expected:
BLOCKED
```

---

## Phase 5 — Frontend Approval Flow

Build:

```text
Recommendation card
Safety check card
Approve button
Reject button
```

---

## Phase 6 — Razorpay Integration

Implement:

```text
Create internal order
Create Razorpay order
Open checkout
Verify payment
Update order status
```

---

## Phase 7 — Audit Trail

Log:

```text
Agent decisions
Policy checks
Approval
Payment creation
Payment result
Failure
```

---

## Phase 8 — Failure Demo

Demonstrate:

```text
Successful payment
```

and:

```text
Failed payment
↓
No duplicate charge
↓
Clear user explanation
↓
Retry possible
```

---

# 26. Suggested Team Module Division

If working in a team:

## Person 1 — Frontend

```text
React
Tailwind
Chat UI
Recommendation UI
Approval UI
Audit UI
Razorpay Checkout
```

## Person 2 — Agent

```text
LangGraph
Intent extraction
Tool calling
Recommendation logic
Agent explanation
```

## Person 3 — Backend

```text
FastAPI
MongoDB Atlas
Products
Orders
Policies
Audit service
```

## Person 4 — Payment and Integration

```text
Razorpay
Payment verification
Order state machine
Failure handling
End-to-end integration
```

---

# 27. Final Demo Workflow

The strongest demo sequence:

```text
STEP 1
User:
"Buy wireless noise-cancelling headphones under ₹5,000"

        ↓

STEP 2
AI:
Understands requirements

        ↓

STEP 3
AI:
Searches AI-readable merchant catalog

        ↓

STEP 4
AI:
Recommends a ₹4,500 product

        ↓

STEP 5
UI shows:
Why selected?
✓ Matches requirements
✓ Within budget
✓ In stock

        ↓

STEP 6
Policy engine:
✓ Budget passed
✓ Stock passed
✓ Allowed

        ↓

STEP 7
User clicks:
APPROVE ₹4,500

        ↓

STEP 8
Backend creates Razorpay Test Mode order

        ↓

STEP 9
React opens Razorpay Checkout

        ↓

STEP 10
Payment success

        ↓

STEP 11
Backend verifies payment

        ↓

STEP 12
Audit trail displays every action
```

Then show failure:

```text
Payment attempt
      ↓
Failure
      ↓
Order marked PAYMENT_FAILED
      ↓
Audit recorded
      ↓
No duplicate payment
      ↓
Retry / Cancel
```

---

# 28. Minimum Viable Product

For the hackathon, do not initially build unnecessary complexity.

The MVP should include:

```text
✓ AI chat interface
✓ Product catalog in MongoDB Atlas
✓ Agent product search
✓ Product recommendation
✓ Explainable decision
✓ Budget limit
✓ Policy validation
✓ User approval gate
✓ Razorpay Test Mode
✓ Backend payment verification
✓ Audit trail
✓ One graceful failure case
```

This is enough to demonstrate the main problem statement end to end.

---

# 29. Future Extensions

After the MVP works, possible extensions:

## Agent-readable Merchant Protocol

Expose a structured endpoint such as:

```text
GET /.well-known/merchant.json
```

Possible metadata:

```json
{
  "merchant": "AgentCart Demo Store",
  "capabilities": [
    "catalog_search",
    "product_details",
    "checkout"
  ],
  "catalog_api": "/api/products/search"
}
```

## Autonomous Commerce Permissions

Users could configure:

```text
Maximum spending: ₹5,000
Maximum purchases per day: 2
Approval required above: ₹1,000
```

## Merchant Growth Agent

The same architecture could later support:

```text
Customer intent
     ↓
AI analyzes basket
     ↓
Relevant upsell/cross-sell
     ↓
Campaign recommendation
```

---

# 30. Core Design Principle

The most important architecture decision is:

```text
AI decides what to propose.

Deterministic backend code decides what is allowed.

The user approves sensitive money actions.

The payment service executes the transaction.

The audit system records everything.
```

This gives the project a clear separation of responsibility.

```text
┌──────────────┐
│ AI AGENT     │ → Intelligence and recommendation
└──────────────┘

┌──────────────┐
│ POLICY CODE  │ → Safety and constraints
└──────────────┘

┌──────────────┐
│ USER         │ → Approval for sensitive action
└──────────────┘

┌──────────────┐
│ RAZORPAY     │ → Payment processing
└──────────────┘

┌──────────────┐
│ AUDIT SYSTEM │ → Accountability and explanation
└──────────────┘
```

---

# 31. Final Project Architecture

```text
                        ┌─────────────────────┐
                        │       USER          │
                        └──────────┬──────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │ REACT + TAILWIND    │
                        │                     │
                        │ Chat Interface      │
                        │ Product UI          │
                        │ Approval UI         │
                        │ Audit Timeline      │
                        └──────────┬──────────┘
                                   │
                                   ▼
                    ┌────────────────────────────┐
                    │       FASTAPI API          │
                    └─────────────┬──────────────┘
                                  │
          ┌───────────────────────┼────────────────────────┐
          │                       │                        │
          ▼                       ▼                        ▼
 ┌────────────────┐     ┌─────────────────┐     ┌─────────────────┐
 │ AI AGENT       │     │ POLICY ENGINE   │     │ AUDIT SERVICE   │
 │ LangGraph      │     │                 │     │                 │
 │                │     │ Budget          │     │ Actions         │
 │ Intent         │     │ Stock           │     │ Reasons         │
 │ Tools          │     │ Permissions     │     │ Results         │
 │ Recommendation │     │ Approval        │     │ Timestamps      │
 └───────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                        │
         ▼                       ▼                        ▼
 ┌────────────────┐      ┌──────────────────────────────────┐
 │ PRODUCT SERVICE│      │          MONGODB ATLAS           │
 │                │      │                                  │
 │ Search Catalog │─────▶│ Products                         │
 └────────────────┘      │ Orders                           │
                         │ Audit Logs                       │
                         │ Payment Events                   │
                         │ Policies                         │
                         └──────────────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │ PAYMENT SERVICE        │
                         │                        │
                         │ Create Razorpay Order  │
                         │ Verify Payment         │
                         └───────────┬────────────┘
                                     │
                                     ▼
                         ┌────────────────────────┐
                         │ RAZORPAY TEST MODE     │
                         │                        │
                         │ Checkout               │
                         │ Payment Processing     │
                         └────────────────────────┘
```

---

# Conclusion

This project is an end-to-end agentic commerce system.

The final product should demonstrate:

```text
Natural Language Request
        ↓
AI Understanding
        ↓
AI-Readable Merchant Catalog
        ↓
Agent Recommendation
        ↓
Explainable Decision
        ↓
Deterministic Safety Checks
        ↓
User Approval Gate
        ↓
Razorpay Test Payment
        ↓
Backend Verification
        ↓
Order Completion / Failure Handling
        ↓
Complete Audit Trail
```

The hackathon value is not simply that an LLM can recommend a product.

The value is proving that an AI agent can participate in commerce while money actions remain:

```text
EXPLAINABLE
BOUNDED
GATED
AUDITABLE
```
