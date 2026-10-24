# Fraud Pattern Analysis: Credit Card Transactions (Jan–Feb 2019)

The dataset contains about 600 fraudulent transactions across about 60 compromised cards. Three strong, consistent patterns stand out.

---

## Pattern 1: Fraud happens at night, mostly 22:00–04:00

Most fraudulent transactions fall into two time windows:

| Window | What happens |
|---|---|
| **22:00 – 23:59** | Peak window. High-value online and in-store shopping bursts. |
| **00:00 – 04:00** | Grocery purchases and small gas "test" charges. |
| 08:00 – 20:00 | Comparatively rare. |

**Why this matters:** Fraudsters operate while cardholders are asleep and unlikely to notice alerts or check their accounts. This gives them a window of several hours before the card is blocked.

---

## Pattern 2: A repeatable "test, then cash out" sequence with distinctive amounts

Spending is not random. It follows three tiers by category and amount:

| Tier | Categories | Typical amount | Purpose |
|---|---|---|---|
| **Card testing** | `gas_transport`, `misc_pos`, `travel`, `kids_pets`, `personal_care`, `health_fitness` | **$4 – $25** | Check that the card works without triggering alerts |
| **Mid-value goods** | `grocery_pos` | **$257 – $380** (very tight band) | Resellable goods; looks like a "big grocery run" |
| **Cash-out** | `shopping_net`, `misc_net`, `shopping_pos` | **$650 – $1,335** | Maximum extraction, often card-not-present |

**Typical lifecycle (Jason Murphy, card …1966):**
- Jan 2, 01:06: grocery_pos $281.06
- Jan 2, 03:38: gas_transport **$7.03** (test)
- Jan 2, 13:38: shopping_net $844.80
- Jan 2, 23:52: misc_net $843.91
- Jan 3, 22:21 to 23:41: four purchases of **$942, $822, $1,093, $1,254** (amounts escalating)

**Other observations:**
- The grocery_pos amounts are almost always $270–$350. This is a near-fixed "fraud ticket size."
- Most fraud targets online categories (`shopping_net`, `misc_net`), where no physical card is needed.

---

## Pattern 3: High-velocity bursts across many merchants (2–3 day card lifespan)

Each compromised card typically shows **8–15 fraudulent transactions within 2–3 days**, almost always at a **different merchant each time**. Charges often come minutes or even seconds apart.

| Cardholder | Burst |
|---|---|
| Dorothy Thomas (OH) | Two shopping_pos charges **2 seconds apart** (23:04:57 and 23:04:59): $704.60 + $810.35, at merchants about 120 km apart |
| Dustin Roberts (NC) | $1,169.82 + $690.81 **10 seconds apart** at different merchants |
| Mark Brown (AK) | **6 transactions in 36 minutes** (22:02–22:38), totaling about $3,729 |
| Mark Brown (AK) | Two gas stations **6 minutes apart**, roughly 20 km apart |

Physically impossible timing like this shows card credentials being used in parallel, likely online or by multiple actors.

**Secondary signals:**
- **Victim profile:** Many cardholders live in very small towns, such as Thompson, UT (pop. 46), West Bethel, ME (47), Summerfield, TX (53), and Westerville, NE (73). Many are elderly (born 1925–1945). This group may monitor accounts less actively.
- **Recurring merchants:** Several merchants appear across many unrelated victims, including Koepp-Parker, Kilback LLC, Heathcote LLC, Gleason-Macejkovic, Baumbach Feeney & Morar, and Labadie Treutel & Bode. These are candidates for point-of-compromise or mule-merchant investigation.

---

## Recommended Detection Rules

1. **Night-time escalation:** Flag a card when a charge under $25 is followed within 24 hours by a charge over $600, especially between 22:00 and 04:00.
2. **Velocity:** Flag 3 or more transactions within 60 minutes at different merchants, or any two charges less than 5 minutes apart at merchants more than 50 km apart.
3. **Amount fingerprint:** Raise risk scores for `grocery_pos` charges of $270–$380 at night, and for `shopping_net`/`misc_net` charges over $800.
4. **Merchant watchlist:** Monitor the recurring merchants listed above.

## Caveats

- **No baseline:** This list contains only fraud rows. Each pattern should be confirmed against legitimate transactions to measure lift. For example, check what share of legitimate transactions also occur at 22:00–04:00.
- **Merchant names are not a signal:** The "fraud_" prefix on every merchant is a naming artifact of this synthetic dataset (Sparkov). It appears on legitimate transactions too and should not be used as a feature.