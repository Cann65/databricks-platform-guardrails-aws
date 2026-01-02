-- Cost Allocation by Tag (Cost Center, Environment)
--
-- Purpose: Allocate Databricks costs to business units using custom tags
-- enforced by cluster policies.
--
-- Data Source: system.billing.usage (Unity Catalog system table)
-- Requirement: Unity Catalog must be enabled on workspace
--
-- Assumptions:
--   - Cluster policies enforce custom_tags: owner, cost_center, env
--   - usage_metadata contains custom_tags JSON
--   - List pricing is available or can be estimated
--
-- Usage:
--   Replace date range and adjust tag extraction as needed

SELECT
  usage_date,
  usage_metadata.custom_tags['cost_center'] AS cost_center,
  usage_metadata.custom_tags['env'] AS environment,
  usage_metadata.custom_tags['owner'] AS owner,
  sku_name,
  usage_type,
  COUNT(*) AS usage_records,
  SUM(usage_quantity) AS total_dbus,
  -- Estimate cost (adjust rate based on your contract)
  ROUND(SUM(usage_quantity) * 0.20, 2) AS estimated_cost_usd
FROM
  system.billing.usage
WHERE
  usage_date >= CURRENT_DATE() - INTERVAL 30 DAYS
  AND usage_type = 'COMPUTE'
GROUP BY
  usage_date,
  usage_metadata.custom_tags['cost_center'],
  usage_metadata.custom_tags['env'],
  usage_metadata.custom_tags['owner'],
  sku_name,
  usage_type
ORDER BY
  usage_date DESC,
  total_dbus DESC;

-- Chargeback Summary by Cost Center:
--
-- SELECT
--   usage_metadata.custom_tags['cost_center'] AS cost_center,
--   SUM(usage_quantity) AS total_dbus,
--   ROUND(SUM(usage_quantity) * 0.20, 2) AS estimated_cost_usd
-- FROM system.billing.usage
-- WHERE usage_date >= CURRENT_DATE() - INTERVAL 30 DAYS
-- GROUP BY usage_metadata.custom_tags['cost_center']
-- ORDER BY total_dbus DESC;

-- Notes:
-- 1. Adjust DBU rate ($0.20 is example) based on your contract
-- 2. Missing tags indicate non-compliant clusters (should be flagged)
-- 3. Use this data for monthly chargeback to business units
