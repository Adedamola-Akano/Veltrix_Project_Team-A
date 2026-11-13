# Six-week campaign test design (seg-v1.0)

Written by the DS team before the test runs. Numbers come from the cleaned data up to 2026-09-30.

## 1. What we are testing
**Segment:** Buy-to-let investors (12,178 customers; 7,022 gave marketing consent).
**Why this segment:** it was chosen by a rule written in advance. Among segments where the test can detect a lift of 40% or less, it has the most expected extra wins: about 5 extra completed deal(s) if enquiries rise by 20% (26 extra enquiries at a 19% win rate).
**Treatment:** the campaign planned for next month, sent to the treatment arm only. **Control:** business as usual, no campaign.

## 2. How customers were assigned
Consenting customers in the segment were split 50/50 at random (seed 2026): **3,511 treatment and 3,511 control**. The groups are balanced on budget, browsing, past leads, mobile use and overseas share (largest standardised difference 0.03; below 0.1 is balanced). The assignment is in `test_assignment.csv`.

## 3. The primary KPI and what counts as a win
**Primary KPI: enquiry rate** = the share of customers in each arm who create at least one new lead during the six weeks.
- Why not completed sales? The median decision for this segment takes 43 days, and the test lasts 42. A sale cannot be counted in time unless decisions are quick, so the enquiry is the measurable first step.
- **Baseline:** 3.77% per six weeks (typical movement between six-week windows: +/- 0.39 points).
- **A win:** the treatment enquiry rate is at least **37% higher** than control (that is, at least 5.16% against 3.77%) **and** a two-sided test gives p < 0.05.
- **Sample size:** detecting a 37% lift needs about 3,443 customers per arm. We have 3,511, so the smallest lift the test can reliably detect is about 37%.

## 4. Secondary measures (reported, not used to declare a win)
- Leads that reach a viewing, and completed deals in the six weeks (for quick-deciding customers).
- Segment mix of the enquiries that came in.
- Guardrails for the DA team to monitor weekly: unsubscribe and complaint rates in the treatment arm. If either rises sharply, pause the campaign and report.

## 5. Rules so the result can be trusted
- Fixed length of six weeks. **No stopping early because the numbers look good.** The weekly monitoring is for guardrails and delivery problems only.
- One primary test, two-sided, at the 5% level. Other cuts of the data are reported as exploratory.
- Treat the control group exactly as normal. No other campaign may target either arm differently.
- If the lift is below the win threshold, report it as **inconclusive**, not as "the campaign does not work": a test of this size can only detect a lift of about 37% or more, so a smaller real effect could be missed. Report the size of the effect and its range.

## 6. After the test
- **Win:** roll the campaign out to the rest of the segment, then test the next segment in the ranking.
- **No win:** keep the learning, review the message or channel, and do not repeat the same test unchanged.
- Re-score the segments monthly (see the refresh process) so the audience stays current.
