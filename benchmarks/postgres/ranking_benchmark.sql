-- VibeMaxxing ranking benchmark seed schema. Run only in an ephemeral database.
CREATE TABLE IF NOT EXISTS period_scores (
  period_kind text NOT NULL,
  period_start timestamptz NOT NULL,
  board_id uuid NOT NULL,
  user_id uuid NOT NULL,
  token_burn bigint NOT NULL CHECK (token_burn >= 0),
  cash_burn_microunits bigint NOT NULL CHECK (cash_burn_microunits >= 0),
  updated_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (period_kind, period_start, board_id, user_id)
);
CREATE INDEX IF NOT EXISTS period_scores_rank_idx
  ON period_scores (period_kind, period_start, board_id, token_burn DESC, user_id ASC);

-- Explicit competition ranking with gaps. Change only through an ADR.
PREPARE top_leaderboard(text, timestamptz, uuid, integer) AS
SELECT user_id, token_burn,
       rank() OVER (ORDER BY token_burn DESC) AS rank
FROM period_scores
WHERE period_kind = $1 AND period_start = $2 AND board_id = $3
ORDER BY token_burn DESC, user_id ASC
LIMIT $4;

PREPARE user_rank(text, timestamptz, uuid, uuid) AS
WITH ranked AS (
  SELECT user_id, token_burn,
         rank() OVER (ORDER BY token_burn DESC) AS rank
  FROM period_scores
  WHERE period_kind = $1 AND period_start = $2 AND board_id = $3
)
SELECT * FROM ranked WHERE user_id = $4;
