# OfficialCW_Rennaisance_MK1212Mod — Working Notes

## Overview

**Mapper:** `OfficialCW_Rennaisance_MK1212Mod`
**Session date:** 2026-04-12
**Attila Mod Set:** MK1212 — dominant tier: **T3** (82%)

See [MK1212_Tier_Reference.md](MK1212_Tier_Reference.md) for tier system details.

## Changes Applied

All fixes replicated from High Medieval mapper with T3 tier progression.

| Category | Count |
|---|---|
| Superfluous MAA deleted | 14 |
| Misspelling fixes (chasseurs→chasseur, etc.) | 4 |
| New MAA mapped | 11 (+ Default entries) |
| Missing cultures added | 132 |
| heritage_buyeo added | 1 |
| Trailing spaces fixed (title keys) | ~601 |

## MAA Assignments (T3 tier)

| MAA | Faction | Attila Key |
|---|---|---|
| `black_armor_cavalry` | Tibetan | `mk_mon_t3_golden_keshiq_lancers` |
| `RICE_iron_forest` | Tibetan | `mk_gold_t3_khorchi_khisigten` |
| `RICE_drokpa_horsemen` | Tibetan | `earl_gold_t3_cavalry` |
| `danish_obudshaer` | Danelander | `mk_merc_swi_t3_swiss_pikemen` |
| `danish_svenner` | Danelander | `earl_dan_t3_cavalry` |
| `outremer_bowmen` | Outremer | `mk_merc_arm_t3_armenian_archers` |
| `outremer_heavy_cavalry` | Outremer | `mk_mio_t3_templar_knights` |
| `outremer_turcopoles` | Outremer | `mk_jer_t3_turcopoles` |
| `RICE_alodian_cavalry` | Horn African | `mk_mak_t3_nubian_knights` |
| `RICE_nilotic_raiders` | Horn African | `mk_mak_t3_nubian_quilted_spearmen` |
| `RICE_sudanese_highlanders` | Horn African | `mk_mak_t3_nubian_footmen` |
| `chasseur` | Outremer | `mk_jer_t3_turcopole_scouts` |
| `landsknecht` | Teutonic | `mk_hre_t3_doppelsoldner_pikemen` (stays T3) |
| `palace_guards` | Default | `mk_ghu_t3_royal_paiks` |

---

## Elephant Size Caveat (flagged 2026-04-13)

During the Attila-inferred size-fill pass, 5 elephant rows in this mapper were set from `null` → `CAVALRY`:

- `accolade_maa_lancers,Nubian` → `earl_mak_t3_nubian_elephants`
- `accolade_maa_lancers,Ethiopian` → `earl_zag_t3_war_elephants`
- `accolade_maa_outriders,Ethiopian` → `earl_zag_t3_elephants`
- `accolade_maa_elephantiers,Burmese` → `mk_ghu_t3_hathnal_cannon_elephants`
- `accolade_maa_elephantiers,Indian` → `mk_ghu_t3_war_elephants`

**Concern:** CW XML output passes size as `max="CAVALRY"` verbatim. Unclear whether CW's parser interprets this as "a cavalry-typical count (~80-100)" or as "just a classifier, let Attila's native `num_men` apply." If it's the former, elephants would spawn at cavalry-unit sizes — ~100 elephants per unit is nonsense.

**Other mappers for reference:**
- **MK1212 High/Late/Ren Default elephant rows** were already `CAVALRY` pre-session (authored that way) — if this is a bug, it's a pre-existing one.
- **LOTR (RiE)** uses numeric caps (`20`, `6`, `3`) for elephants — possibly indicating the LOTR author explicitly capped counts to avoid the CAVALRY scaling issue.

**Decision (2026-04-13):** Leave as `CAVALRY` for now (matches pre-existing mapper convention). If in-game testing shows 100-elephant units spawning, revert these 5 rows to `null` or set small numeric caps (e.g. `6`).
