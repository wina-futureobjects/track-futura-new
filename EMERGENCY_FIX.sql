
-- EMERGENCY FIX SQL SCRIPT
-- Run this directly on your production database

-- Update posts for folder Job 3 (ID: 104)
UPDATE brightdata_integration_brightdatascrapedpost 
SET folder_id = 104 
WHERE id IN (78,77,76,6,1,7,8,75,74,9,10,2,73,3,4,72,71,5,70,69,68,67,66,65,64,63,62,61,60,59,58,57,56,55,54,53,52,51,50);

-- Update posts for folder Job 2 (ID: 103)
UPDATE brightdata_integration_brightdatascrapedpost 
SET folder_id = 103 
WHERE id IN (49,48,47,46,45,44,43,42,41,40,39,38,37,36,35,34,33,32,31,30,29,28,27,26,25,24,23,22,21,20,19,18,17,16,15,14,13,12,11);

-- Update workflow runs to completed
UPDATE workflow_scrapingrun 
SET status = 'completed', 
    total_jobs = 1, 
    completed_jobs = 1, 
    successful_jobs = 1,
    completed_at = NOW()
WHERE status = 'pending';

-- Verify the fix
SELECT 'Posts in folder 104' as description, COUNT(*) as count 
FROM brightdata_integration_brightdatascrapedpost 
WHERE folder_id = 104
UNION ALL
SELECT 'Posts in folder 103' as description, COUNT(*) as count 
FROM brightdata_integration_brightdatascrapedpost 
WHERE folder_id = 103
UNION ALL
SELECT 'Completed workflow runs' as description, COUNT(*) as count 
FROM workflow_scrapingrun 
WHERE status = 'completed';
