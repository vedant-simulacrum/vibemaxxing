# Accounting, Pricing, and Time Contract

Status: normative planning contract
Version: 1

## Token Burn

`token_burn_total = input + output + cache_read + cache_write + reasoning + multimodal_input + multimodal_output`.

Each category is stored independently as a non-negative integer. Unknown categories are `null`, never zero. Totals are accepted only when the adapter identifies whether the source total already includes subcategories; reconciliation prevents double addition.

Tool calls are not a separate token category. Tokens used to serialize tool definitions, arguments, results, context, compaction, summaries,