-- Fix incorrect post_count values in UnifiedRunFolder
-- Generated on 2025-10-11T20:26:19.456856

-- Fix folder 240: Facebook - Posts
UPDATE workflow_management_unifiedrunfolder SET post_count = 0 WHERE id = 240;

-- Fix folder 239: Facebook
UPDATE workflow_management_unifiedrunfolder SET post_count = 0 WHERE id = 239;

-- Fix folder 237: Instagram - Posts
UPDATE workflow_management_unifiedrunfolder SET post_count = 0 WHERE id = 237;

-- Fix folder 236: Instagram
UPDATE workflow_management_unifiedrunfolder SET post_count = 0 WHERE id = 236;

-- Fix folder 235: Nike - 11/10/2025 07:28:10
UPDATE workflow_management_unifiedrunfolder SET post_count = 0 WHERE id = 235;

-- Fix folder 233: Facebook - Posts
UPDATE workflow_management_unifiedrunfolder SET post_count = 0 WHERE id = 233;

-- Fix folder 232: Facebook
UPDATE workflow_management_unifiedrunfolder SET post_count = 0 WHERE id = 232;
