# Social, Ranking, and Abuse Research Contract

## Ranking simulations

Simulate daily, weekly, monthly, seasonal, yearly, and lifetime boards with:

- ties;
- late claims;
- UTC period rollover;
- users in different display time zones;
- score corrections;
- quarantined claims;
- evidence downgrades;
- deleted accounts;
- private boards;
- country cohort suppression.

The default public rank is competition rank: equal scores share a rank and subsequent ranks have gaps. Secondary ordering is display stability only.

## Notification policy research

Test overtake notifications with hysteresis and rate limits. Prevent oscillating users from generating notification storms. Presence must expire automatically and reveal only an allowlisted agent enum and coarse active state.

## Abuse operations

Required controls:

- friend-request rate limits and block controls;
- username/profile reporting;
- private-board owner moderation;
- quarantine with reason codes;
- appeal state machine;
- device revocation;
- suspicious-cluster review;
- moderator audit log;
- two-person review for permanent competitive bans;
- evidence retention limits.

## Country privacy

- country is optional;
- never expose IP, city, coordinates, or nationality claims;
- require minimum cohort size;
- use switching cooldowns;
- preserve correction history privately;
- provide opt-out;
- disable a country leaderboard when abuse or safety risk is material.
