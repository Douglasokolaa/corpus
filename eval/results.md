# Evaluation Results

| Metric | Value |
|---|---|
| Questions | 22 |
| Groundedness | 80.0% |
| Citation accuracy | 80.0% |
| Partial match vs gold | 95.0% |
| Refusal accuracy (off-topic) | 100.0% |
| Latency p50 | 3.25 s |
| Latency p95 | 8.47 s |

## Per-question results

| Question | Latency (s) | Grounded | Citations OK | Match | Answer |
|---|---|---|---|---|---|
| How many days of PTO do full-time employees get each year? | 3.76 | yes | yes | yes | Full-time employees receive 20 days of PTO per calendar year. [pto-policy] |
| How many unused PTO days can I carry over into the next year? | 3.7 | yes | yes | yes | You may carry over a maximum of 5 unused PTO days into the next calendar year. [pto-policy] |
| How much notice do I need to give for a PTO request of a week or longer? | 8.47 | yes | yes | yes | Requests for a PTO period of one week or longer must be submitted at least two weeks in advance. [pto-policy] |
| When do I need a doctor's note for sick leave? | 3.68 | yes | yes | yes | A doctor’s note is required when you are absent due to illness for more than three consecutive working days. The note mu |
| How many days per week can I work remotely? | 2.63 | yes | yes | yes | Employees may work remotely up to three days per week. [remote-work-policy] |
| What are the company's core working hours? | 20.0 | yes | yes | yes | All employees must be available between 10:00 and 16:00 local time for meetings and collaboration, regardless of where t |
| How soon after incurring an expense do I have to submit it? | 2.76 | yes | yes | yes | You must submit expenses in Expensify within 30 days of incurring them. [expense-policy] |
| Do I need a receipt for a $20 lunch expense? | 7.51 | no | no | yes | No, you do not need a receipt for a $20 lunch expense. The policy states that itemized receipts are required only for ex |
| What is the nightly hotel rate cap for business travel? | 3.49 | yes | yes | yes | The nightly hotel rate cap is $250 for standard locations, and $350 for high‑cost cities (New York, San Francisco, Londo |
| What class of ticket should I book for a 3-hour flight? | 4.42 | yes | yes | yes | For a flight under 6 hours, the policy requires booking economy class. Since your flight is 3 hours, you should book an  |
| How quickly must I report a security incident? | 3.61 | no | no | no | You must report a suspected security incident within 24 hours of discovery. This applies to general security incidents ( |
| What is the minimum password length? | 2.96 | yes | yes | yes | The minimum password length is 14 characters. [password-policy] |
| How long does the company keep financial records? | 2.9 | yes | yes | yes | Financial records are retained for 7 years. [data-privacy-policy] |
| How many days does the company have to respond to a data subject request? | 3.0 | yes | yes | yes | The company must respond to a data subject request within 30 days of receipt. [data-privacy-policy] |
| How many weeks of paid leave do primary caregivers get? | 3.31 | yes | yes | yes | Primary caregivers receive 16 weeks of fully paid leave. [parental-leave-policy] |
| How much is the home office stipend? | 3.13 | no | no | yes | The home office stipend is a one‑time payment of **$500** for purchasing a desk, chair, or other home office equipment [ |
| How often do performance reviews happen and in which months? | 3.19 | yes | yes | yes | Performance reviews occur twice per year, in April and October. [performance-review-policy] |
| Do I have to disclose a $150 gift from a vendor? | 3.39 | yes | yes | yes | Yes. Any gift from a vendor worth more than $100 must be disclosed to ethics@acmecorp.com (and may need to be declined o |
| When is a purchase order required for a vendor purchase? | 3.08 | yes | yes | yes | A purchase order is required for any vendor purchase that exceeds $5,000. [vendor-policy] |
| How many paid company holidays are there per year? | 2.98 | no | no | yes | Acme Corporation observes 11 paid company holidays per year. [holiday-policy] Holiday Policy - Paid Holidays |
| Who won the 2022 FIFA World Cup? | 1.27 | - | - | refusal OK | I can only answer questions about our company policies, and I couldn't find anything relevant in them. |
| What is the capital of France? | 0.8 | - | - | refusal OK | I can only answer questions about our company policies, and I couldn't find anything relevant in them. |
