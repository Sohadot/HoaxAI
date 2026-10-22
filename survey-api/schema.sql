-- Private Cloudflare D1 database; do not copy rows into GitHub.
CREATE TABLE IF NOT EXISTS survey_responses (
  request_id TEXT PRIMARY KEY NOT NULL,
  q1 TEXT NOT NULL,
  q2 TEXT NOT NULL,
  q3 TEXT NOT NULL,
  q4 TEXT NOT NULL,
  q5 TEXT NOT NULL DEFAULT '',
  referral TEXT NOT NULL CHECK (referral IN ('rick','discord','direct','other')),
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
) STRICT;
CREATE INDEX IF NOT EXISTS idx_survey_created ON survey_responses(created_at);
-- Run data retention privately every 30 days:
-- DELETE FROM survey_responses WHERE created_at < strftime('%Y-%m-%dT%H:%M:%fZ','now','-90 days');
