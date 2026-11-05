# Synthetic HR Corpus — NovaNet Technologies Ltd

Fictional HR policy handbook for a mid-size Lagos-based ISP/tech company. Every organisation, person, reference number and amount is invented. No real company data belongs in this folder or anywhere in course files.

Each document carries a "SYNTHETIC DOCUMENT" banner on its first line.

## Company

**NovaNet Technologies Ltd** — a fictional Nigerian internet service provider and technology company headquartered at Civic Towers, Victoria Island, Lagos. ~250 employees, operating since 2018.

## Documents (15 files)

### Policies (6)

| File | doc_id | Status | Date issued |
|------|--------|--------|-------------|
| HR-POL-2024-001_annual_leave_policy.txt | HR-POL-2024-001 | SUPERSEDED by HR-POL-2025-006 | 2024-01-15 |
| HR-POL-2024-002_code_of_conduct.txt | HR-POL-2024-002 | CURRENT | 2024-02-01 |
| HR-POL-2024-003_remote_work_policy.txt | HR-POL-2024-003 | CURRENT (amounts updated by HR-CIR-2026-003) | 2024-03-01 |
| HR-POL-2025-004_data_protection_policy.txt | HR-POL-2025-004 | CURRENT | 2025-01-10 |
| HR-POL-2025-005_travel_expense_policy.txt | HR-POL-2025-005 | CURRENT | 2025-03-01 |
| HR-POL-2025-006_annual_leave_policy_revised.txt | HR-POL-2025-006 | CURRENT | 2025-07-01 |

### SOPs (4)

| File | doc_id | Status | Date issued |
|------|--------|--------|-------------|
| HR-SOP-2024-001_employee_onboarding.txt | HR-SOP-2024-001 | CURRENT | 2024-04-01 |
| HR-SOP-2025-002_performance_review.txt | HR-SOP-2025-002 | CURRENT | 2025-01-15 |
| HR-SOP-2025-003_employee_exit.txt | HR-SOP-2025-003 | CURRENT | 2025-04-01 |
| HR-SOP-2025-004_expense_claims.txt | HR-SOP-2025-004 | CURRENT | 2025-05-01 |

### Circulars (3)

| File | doc_id | Status | Date issued |
|------|--------|--------|-------------|
| HR-CIR-2025-001_revised_leave_entitlements.txt | HR-CIR-2025-001 | CURRENT | 2025-06-15 |
| HR-CIR-2025-002_public_holiday_schedule.txt | HR-CIR-2025-002 | CURRENT | 2025-11-28 |
| HR-CIR-2026-003_remote_work_allowance_update.txt | HR-CIR-2026-003 | CURRENT | 2026-02-10 |

### FAQs (2)

| File | doc_id | Status | Date issued |
|------|--------|--------|-------------|
| HR-FAQ-2025-001_leave_and_absence.txt | HR-FAQ-2025-001 | CURRENT | 2025-08-01 |
| HR-FAQ-2025-002_benefits_and_allowances.txt | HR-FAQ-2025-002 | CURRENT | 2025-09-01 |

## Metadata fields for ChromaDB

When ingesting into ChromaDB, store these metadata fields per chunk:

| Field | Type | Values |
|-------|------|--------|
| `doc_id` | string | e.g. `HR-POL-2025-006` |
| `doc_type` | string | `policy`, `sop`, `circular`, `faq` |
| `department` | string | `HR`, `HR / IT`, `HR / Legal`, `HR / Finance`, `Finance` |
| `date_issued` | string | ISO date, e.g. `2025-07-01` |
| `status` | string | `current`, `superseded` |
| `title` | string | Document title |

## Built-in retrieval traps

See ANSWER-KEY.md for the full list. Key traps:

1. **Superseded leave policy** — the old policy (HR-POL-2024-001) says 20 days annual leave; the current one (HR-POL-2025-006) says 25. Without a status filter, the assistant may blend both and give the wrong answer.
2. **Circular updates a policy without replacing it** — the remote work allowance circular (HR-CIR-2026-003) changes the amounts in the remote work policy (HR-POL-2024-003), but the policy itself is not reissued. A search for "remote work allowance" should find both and cite the circular as the current figure.
3. **FAQ contradicts nothing but overlaps everything** — the FAQs restate information from policies and circulars. A good system cites the authoritative source (the policy), not just the FAQ.
4. **Cross-department questions** — "What equipment do I get when I start?" touches onboarding (HR-SOP-2024-001), remote work (HR-POL-2024-003), and the circular (HR-CIR-2026-003). The system must retrieve from multiple doc_types.
