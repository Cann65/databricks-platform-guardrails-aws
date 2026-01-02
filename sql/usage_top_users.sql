-- Top Users by Compute Usage
--
-- Purpose: Identify users consuming the most cluster compute resources
-- to allocate costs and identify optimization opportunities.
--
-- Data Source: system.billing.usage (Unity Catalog system table)
-- Requirement: Unity Catalog must be enabled on workspace
--
-- Assumptions:
--   - system.billing.usage table is available
--   - usage_metadata contains user identity
--   - DBU consumption is the primary cost metric
--
-- Usage:
--   Replace date range with your reporting period

SELECT
  usage_metadata.user_name,
  usage_metadata.cluster_id,
  sku_name,
  COUNT(*) AS usage_records,
  SUM(usage_quantity) AS total_dbus,
  ROUND(SUM(usage_quantity), 2) AS dbus_rounded,
  usage_date
FROM
  system.billing.usage
WHERE
  usage_date >= CURRENT_DATE() - INTERVAL 30 DAYS
  AND usage_metadata.user_name IS NOT NULL
  AND usage_type = 'COMPUTE'
GROUP BY
  usage_metadata.user_name,
  usage_metadata.cluster_id,
  sku_name,
  usage_date
ORDER BY
  total_dbus DESC
LIMIT 100;

-- Cost Optimization Notes:
-- 1. Users with high DBU consumption should review cluster sizes
-- 2. Check if workloads can use job clusters instead of all-purpose
-- 3. Verify auto-termination is enabled and set to ≤15 minutes
