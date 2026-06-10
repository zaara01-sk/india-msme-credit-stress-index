-- ================================================================
-- MSME Credit Stress Index — SQL Analysis
-- Author: Zaara Akbar Shaikh
-- Database: msme_stress (MySQL 8.0)
-- ================================================================

USE msme_stress;

-- ----------------------------------------------------------------
-- Query 1: Which year had the fastest MSME credit growth?
-- ----------------------------------------------------------------
SELECT fiscal_year,
       msme_credit_growth_pct,
       RANK() OVER (ORDER BY msme_credit_growth_pct DESC) AS growth_rank
FROM rbi_msme_credit
WHERE msme_credit_growth_pct IS NOT NULL
ORDER BY msme_credit_growth_pct DESC;

-- ----------------------------------------------------------------
-- Query 2: YoY NPA change with stress classification
-- ----------------------------------------------------------------
SELECT fiscal_year,
       gross_npa_pct,
       npa_yoy_change,
       stress_signal
FROM rbi_npa
ORDER BY fiscal_year;

-- ----------------------------------------------------------------
-- Query 3: 3-year rolling average NPA (window function)
-- ----------------------------------------------------------------
SELECT fiscal_year,
       gross_npa_pct,
       ROUND(AVG(gross_npa_pct) OVER (
           ORDER BY fiscal_year
           ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
       ), 2) AS rolling_3yr_avg_npa
FROM rbi_npa
ORDER BY fiscal_year;

-- ----------------------------------------------------------------
-- Query 4: CGTMSE policy signal classification
-- ----------------------------------------------------------------
SELECT fiscal_year,
       guarantee_amt_cr,
       guarantee_growth_pct,
       CASE
           WHEN guarantee_growth_pct > 50 THEN 'Aggressive Expansion'
           WHEN guarantee_growth_pct > 0  THEN 'Moderate Expansion'
           WHEN guarantee_growth_pct < 0  THEN 'Contraction'
           ELSE 'Baseline'
       END AS policy_signal
FROM cgtmse_guarantees
ORDER BY fiscal_year;

------------------------------------------------------------------
-- Query 5: CTE — Credit growth vs NPA for overlapping years
------------------------------------------------------------------
WITH credit AS (
    SELECT fiscal_year, msme_credit_growth_pct
    FROM rbi_msme_credit
),
npa AS (
    SELECT fiscal_year, gross_npa_pct
    FROM rbi_npa
)
SELECT c.fiscal_year,
       c.msme_credit_growth_pct,
       n.gross_npa_pct
FROM credit c
INNER JOIN npa n ON c.fiscal_year = n.fiscal_year
ORDER BY c.fiscal_year;