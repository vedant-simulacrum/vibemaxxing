# Onboarding and Privacy Verification Research

## Primary outcome

A developer unfamiliar with VibeMaxxing can install it, understand the privacy boundary, connect one supported agent, inspect an outbound claim, and appear on a test leaderboard within five minutes.

## Required prototype steps

1. Explain Token Burn and estimated Cash Burn.
2. Explain that genuine but pointless usage counts.
3. Show exactly which processes can read local agent data.
4. Show which process can access the network.
5. Display the fixed outbound schema before enabling sync.
6. Let the user run a synthetic safe test.
7. Connect an adapter with minimum permissions.
8. Show evidence state and why it received that state.
9. Display the signed claim and server receipt in human-readable form.
10. Provide disconnect, export, local-delete, and server-delete actions.

## Study measures

- completion rate
- median and p90 time to first qualifying claim
- permission comprehension
- privacy-boundary comprehension
- correct interpretation of Cash Burn
- correct interpretation of evidence states
- trust rating before and after claim inspection
- uninstall/deletion confidence
- abandonment step and reason
- accessibility failures

## Blocking criteria

- median time <= 5 minutes for a supported agent;
- no participant believes Cash Burn is an invoice after onboarding;
- at least 90% identify that transcripts stay local;
- at least 90% can locate outbound-claim inspection;
- all critical flows keyboard accessible and screen-reader labeled;
- no dark patterns around sync, presence, deletion, or notifications.
