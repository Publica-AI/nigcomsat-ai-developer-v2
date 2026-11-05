# Answer Key (instructor only)

Do not give this file to participants. It records the true facts in each document and the traps built into them, so demos and test sets can be checked against known answers.

## Key facts by document

### HR-POL-2024-001 — Annual Leave Policy (SUPERSEDED)
- 20 working days annual leave
- 5 days carry-forward max
- 7 working days notice for leave requests
- Manager has 3 working days to respond
- Leave without pay: max 10 days/year
- **STATUS: SUPERSEDED by HR-POL-2025-006 on 2025-07-01**

### HR-POL-2025-006 — Annual Leave Policy (Revised) — CURRENT
- 25 working days annual leave
- 10 days carry-forward max, must use by 31 March
- 10 working days notice (15 for 5+ consecutive days)
- Manager has 2 working days to respond
- Compassionate leave: 5 days immediate family, 3 days extended
- Sick leave: 12 days/year, medical cert for 3+ consecutive days
- Maternity: 16 weeks (4 before, 12 after), fully paid
- Paternity: 10 working days within 3 months of birth
- Leave without pay: max 15 days/year
- Cash-out of unused days only on termination

### HR-POL-2024-002 — Code of Conduct
- Zero-tolerance on harassment
- Conflict of interest: report within 7 days
- Misconduct categories: minor, serious, gross
- Gross misconduct may result in summary dismissal
- Disciplinary: verbal → first written (6mo) → final written (12mo) → dismissal panel
- Appeal to MD within 10 working days, decision is final

### HR-POL-2024-003 — Remote Work Policy
- Eligibility: completed 6-month probation
- Hybrid: 3 office days (Tue/Wed/Thu), remote Mon/Fri
- Fully remote: case-by-case, 1 in-office week per quarter
- Monthly allowance: NGN 25,000 (UPDATED to NGN 35,000 by HR-CIR-2026-003)
- Equipment up to NGN 80,000 (UPDATED to NGN 120,000 by HR-CIR-2026-003)
- Core hours: 09:00–16:00 WAT
- Must use company laptop and VPN
- Co-working: not reimbursed (UPDATED: up to NGN 40,000/month for fully remote outside Lagos, by HR-CIR-2026-003)

### HR-POL-2025-004 — Data Protection Policy
- NDPA 2023 compliance
- Lawful bases: contract, legal obligation, legitimate interest (not consent)
- Retention: 6 years after exit for employment records
- Unsuccessful applicants: 12 months then deleted
- Employee rights: access, correction, deletion, objection, portability
- DPO response within 30 days
- HRIS: encrypted servers Lagos, backup Abuja
- Breach reporting: to DPO within 24 hours

### HR-POL-2025-005 — Travel and Expense Policy
- Domestic per diem: NGN 15,000/day
- International per diem: USD 75/day
- Domestic accommodation: NGN 35,000 (GL 1–4), NGN 55,000 (GL 5–7), NGN 85,000 (GL 8+)
- International accommodation: up to USD 200/night
- Mileage: NGN 80/km with odometer log
- Claims within 14 days, after 60 days not reimbursed
- Non-reimbursable: alcohol, personal entertainment, traffic fines, mini-bar, laundry <5 days

### HR-SOP-2024-001 — Onboarding
- Probation: 6 months
- Review at month 3 and month 6
- Outcomes: confirm, extend (up to 3 months), terminate (2 weeks notice)
- Day 1: orientation, IT setup, buddy assignment, 30-60-90 plan
- Mandatory training: InfoSec (1hr), NDPA (45min), Harassment (30min)
- Office: 14th Floor, Civic Towers, Ozumba Mbadiwe Avenue, Victoria Island, Lagos

### HR-SOP-2025-002 — Performance Review
- Cycle: goal setting (Jan) → mid-year check (Jul) → year-end review (Dec) → calibration (Jan+1)
- Scale: 1 (Unsatisfactory) to 5 (Exceptional)
- Rating 1 or 2 triggers 90-day PIP
- Bonus: 20% (rating 5), 15% (4), 10% (3), not eligible (1–2)
- Promotion: rating 4+ current year, 3+ prior year, 18+ months in grade
- Salary review effective 1 April

### HR-SOP-2025-003 — Employee Exit
- Notice: 1 month (GL 1–4), 2 months (GL 5–7), 3 months (GL 8+)
- Final settlement within 30 days of last working day
- Includes: salary, pro-rated 13th month, unused leave cash-out, expenses owed
- Email forwarded to manager for 30 days then deactivated
- Reference letters: factual only (title, dates, grade)

### HR-SOP-2025-004 — Expense Claims
- Submit within 14 days (30 days with HoD approval, 60+ days rejected)
- Receipts required for everything except per diem
- Claims above NGN 100,000 need HoD approval
- Finance processes within 10 working days

## Retrieval traps

### Trap 1: Superseded leave policy
**Question:** "How many days of annual leave do I get?"
**Correct answer:** 25 days (HR-POL-2025-006)
**Wrong answer:** 20 days (HR-POL-2024-001 — superseded)
**What catches it:** Filtering by status=current, or the system seeing the SUPERSEDED banner.

### Trap 2: Circular updates policy amounts
**Question:** "What is the remote work allowance?"
**Correct answer:** NGN 35,000/month (per HR-CIR-2026-003)
**Wrong answer:** NGN 25,000/month (per HR-POL-2024-003 — the policy is current but its amounts are outdated)
**What catches it:** Retrieving from both policies and circulars, and recognising the circular as the latest figure. The policy itself says NGN 25,000 and has not been reissued.

### Trap 3: FAQ overlaps with authoritative source
**Question:** "Can I carry over unused leave?"
**Correct answer:** Yes, up to 10 days, must be used by 31 March (HR-POL-2025-006, section 3c)
**Both the FAQ (HR-FAQ-2025-001, Q3) and the policy give the same answer.** A good system cites the policy as the authoritative source, not just the FAQ.

### Trap 4: Cross-document answer
**Question:** "What equipment do I get for working from home?"
**Correct answer requires chunks from three documents:**
- Laptop, VPN, Microsoft 365 from onboarding (HR-SOP-2024-001)
- Chair/monitor up to NGN 120,000 from the circular (HR-CIR-2026-003), not NGN 80,000 from the policy
- Privacy screen requirement from remote work policy (HR-POL-2024-003)

### Trap 5: Filtering by date matters
**Question:** "What changed in the leave policy this year?" (asked in 2025)
**Correct answer:** Lists the changes from HR-POL-2025-006, section 10.
**Without a date filter:** Could return changes from 2024 or mix up which year "this year" refers to.

## Questions the corpus cannot answer (refusal tests)

A correct assistant must say the information is not in the documents:

- What is the CEO's salary?
- Can I bring my pet to the office?
- What is the company's revenue?
- Does NovaNet have a gym or fitness benefit?
- What is the dress code on Saturdays?
- Who is the current Managing Director?
