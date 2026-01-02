-- Job Failure Analysis
--
-- Purpose: Identify failing jobs to improve reliability and reduce
-- wasted compute from failed runs.
--
-- Data Source: system.workflow.job_run_timeline (Unity Catalog system table)
-- Requirement: Unity Catalog must be enabled on workspace
--
-- Assumptions:
--   - system.workflow.job_run_timeline table is available
--   - run_state tracks success/failure
--   - Failed jobs represent wasted compute and require investigation
--
-- Usage:
--   Adjust lookback period as needed (default: 7 days)

SELECT
  job_id,
  job_name,
  run_id,
  run_state,
  result_state,
  start_time,
  end_time,
  TIMESTAMPDIFF(MINUTE, start_time, end_time) AS duration_minutes,
  error_message
FROM
  system.workflow.job_run_timeline
WHERE
  start_time >= CURRENT_TIMESTAMP() - INTERVAL 7 DAYS
  AND result_state IN ('FAILED', 'TIMEDOUT', 'CANCELED')
ORDER BY
  start_time DESC;

-- Failure Pattern Analysis:
-- Run this to group by job and identify chronic failures
--
-- SELECT
--   job_name,
--   COUNT(*) AS failure_count,
--   COUNT(DISTINCT DATE(start_time)) AS days_with_failures
-- FROM system.workflow.job_run_timeline
-- WHERE start_time >= CURRENT_TIMESTAMP() - INTERVAL 7 DAYS
--   AND result_state = 'FAILED'
-- GROUP BY job_name
-- ORDER BY failure_count DESC;

-- Cost Impact:
-- Failed jobs waste DBUs. Multiply duration_minutes by cluster size
-- to estimate wasted compute resources.
