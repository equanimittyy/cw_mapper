# OfficialCW_HighMedieval_MK1212Mod — Working Notes

## Overview

**Mapper:** `OfficialCW_HighMedieval_MK1212Mod`
**Session date:** 2026-04-10
**Required CK3 Mods:** Vanilla, Africa Plus, Buffed Mongol Invasion, Cultures Expanded, More Traditions v2, Muslim Enhancements, RICE
**Attila Mod Set:** MK1212 (Medieval Kingdoms 1212) + Realistic Infantry/Cavalry/Missile Overhauls + Cilicia Revamp

**⚠️ IMPORTANT:** The Attila mod set is COMPLETELY DIFFERENT from Early Medieval (which uses Age of Charlemagne + vanilla). MK1212 uses `mk_*` prefixed unit keys. Do not copy Early Medieval Attila unit assignments — need to find MK1212 equivalents.

### MK1212 Unit Tier System

See [MK1212_Tier_Reference.md](MK1212_Tier_Reference.md) for full tier breakdown and mapper usage data.

---

## Status

| Category | Initial | Resolved | Remaining |
|---|---|---|---|
| Missing MAA (crash risk) | 19 | 14 mapped + 5 siege ignored | **0** ✅ |
| Missing Attila Unit Keys | 2 | 2 fixed (wrong key references) | **0** ✅ |
| Missing Title Keys | 30 | 30 fixed (trailing spaces in keys) | **0** ✅ |
| Superfluous MAA | 21 | 15 deleted + 5 misspellings fixed + 1 typo fixed | **0** ✅ |
| Missing Cultures | 134 | 132 mapped | **2** (placeholders, deferred) |
| Superfluous Cultures | 224 | Not addressed | 224 |
| Trailing spaces in keys | ~582 | All trimmed (TITLES_AND_MAA, TITLE_NAMES, FACTIONS_AND_MAA) | **0** ✅ |

---

## Missing Attila Unit Keys — Fixed ✅

Both keys were **wrong references** to existing units:

| Wrong Key | Correct Key | Used In | Fix |
|---|---|---|---|
| `ghu_t1_afghan_spearmen` | `mk_ghu_t1_afghan_spearmen` | Indian / accolade_maa_pikes | Missing `mk_` prefix |
| `mk_mio_t1_spanish_order_knights_dismounted` | `mk_cas_t1_order_knights_dismounted` | Aragonese / house_guard | The `mk_mio_*` value was a `land_unit` reference, not the actual `unit` key. The TSV's unit column uses `mk_cas_t1_*` |

---

## Missing MAA — TODO (19)

Same 17 as Early Medieval PLUS 2 MK1212-specific siege:

| MAA | Status | Notes |
|---|---|---|
| `abbasid_trebuchet` | ⏭️ Ignore | Siege |
| `byzantine_trebuchet` | ⏭️ Ignore | Siege |
| `bulgarian_testudos` | ⏭️ Ignore | Siege (battering ram) |
| `cloud_ladder` | ⏭️ Ignore | Siege equipment |
| `siege_tower` | ⏭️ Ignore | Siege equipment |
| `black_armor_cavalry` | ✅ | Tibetan + Default → `mk_mon_t1_keshiq_lancers` (CAVALRY) |
| `RICE_iron_forest` | ✅ | Tibetan + Default → `mk_gold_t1_khorchi_khisigten` (CAVALRY) |
| `RICE_drokpa_horsemen` | ✅ | Tibetan + Default → `earl_gold_t2_cavalry` (CAVALRY) |
| `chasseur` | ✅ | Outremer + Default → `mk_jer_t1_ministeriales` (CAVALRY) — from misspelling fix |
| `landsknecht` | ✅ | Teutonic + Default → `mk_hre_t3_doppelsoldner_pikemen` (INFANTRY) — from misspelling fix |
| `palace_guards` | ✅ | Default → `mk_khw_t1_junior_ghulaman` (INFANTRY) — from misspelling fix. TODO: all factions |
| `danish_obudshaer` | ✅ | Danelander + Default → `mk_merc_bra_t1_brabanzonen_voulgier` (INFANTRY) |
| `danish_svenner` | ✅ | Danelander + Default → `earl_dan_t1_cavalry` / "Hestevend" (CAVALRY) |
| `outremer_bowmen` | ✅ | Outremer + Default → `mk_merc_arm_t1_armenian_archers` (RANGED) |
| `outremer_heavy_cavalry` | ✅ | Outremer + Default → `mk_mio_t1_templar_knights` (CAVALRY) — matches existing Default mapping |
| `outremer_turcopoles` | ✅ | Outremer + Default → `mk_jer_t1_turcopoles` (CAVALRY) — matches existing Default mapping |
| `RICE_alodian_cavalry` | ✅ | Horn African + Default → `mk_mak_t1_alodian_horsemen` (CAVALRY) — follows accolade_maa_lancers |
| `RICE_nilotic_raiders` | ✅ | Horn African + Default → `mk_mak_t1_nubian_slingers` (INFANTRY) |
| `RICE_sudanese_highlanders` | ✅ | Horn African + Default → `mk_mak_t1_nubian_quilted_infantry` (INFANTRY) — melee fighters despite CK3 skirmisher tag |

### Tier Progression Notes (for Late Medieval / Renaissance mappers)

These MAA should follow their natural tier progression when mapping Late Medieval and Renaissance. Source column shows how the progression was determined.

| MAA | High | Late | Renaissance | Source |
|---|---|---|---|---|
| `black_armor_cavalry` | `mk_mon_t1_keshiq_lancers` | `mk_mon_t2_golden_keshiq_lancers` | `mk_mon_t3_golden_keshiq_lancers` | Shared with `samurai` in Default |
| `RICE_iron_forest` | `mk_gold_t1_khorchi_khisigten` | `mk_gold_t2_khorchi_khisigten` | `mk_gold_t3_khorchi_khisigten` | Shared with `mongolian_horse_archers` in Default |
| `RICE_drokpa_horsemen` | `earl_gold_t2_cavalry` | `earl_gold_t3_cavalry` | (use T3 or verify) | Natural T1→T2→T3 progression (started at T2) |
| `chasseur` | `mk_jer_t1_ministeriales` | `mk_jer_t2_turcopole_scouts` | `mk_jer_t3_turcopole_scouts` | From misspelled `chasseurs` in Late/Ren |
| `landsknecht` | `mk_hre_t3_doppelsoldner_pikemen` | `mk_hre_t3_doppelsoldner_pikemen` | `mk_hre_t3_doppelsoldner_pikemen` | Stays T3 across all (from misspelled `landsknechts`) |
| `palace_guards` | `mk_khw_t1_junior_ghulaman` | `mk_khw_t2_qullughchi` | `mk_khw_t3_qullughchi` | Shared with `accolade_maa_archers` in Daylamite |
| `danish_obudshaer` | `mk_merc_bra_t1_brabanzonen_voulgier` | `mk_bur_t2_pavise_spearmen` | `mk_merc_swi_t3_swiss_pikemen` | Shared with `accolade_maa_pikes` in Breton |
| `danish_svenner` | `earl_dan_t1_cavalry` | `earl_dan_t2_cavalry` | `earl_dan_t3_cavalry` | Natural progression |
| `outremer_bowmen` | `mk_merc_arm_t1_armenian_archers` | `mk_merc_arm_t2_armenian_archers` | `mk_merc_arm_t3_armenian_archers` | Natural progression |
| `outremer_heavy_cavalry` | `mk_mio_t1_templar_knights` | `mk_mio_t2_templar_knights` | (verify T3) | Natural progression |
| `outremer_turcopoles` | `mk_jer_t1_turcopoles` | `mk_jer_t2_turcopoles` | (verify T3) | Natural progression |
| `RICE_alodian_cavalry` | `mk_mak_t1_alodian_horsemen` | `mk_mak_t2_nubian_knights` | `mk_mak_t3_nubian_knights` | Stays Nubian — Alodia was a Nubian kingdom (sibling to Makuria) |
| `RICE_nilotic_raiders` | `mk_mak_t1_nubian_slingers` | `mk_mak_t2_nubian_slingers` | `mk_mak_t3_nubian_quilted_spearmen` | User-specified progression |
| `RICE_sudanese_highlanders` | `mk_mak_t1_nubian_quilted_infantry` | `mk_mak_t2_nubian_footmen` | `mk_mak_t3_nubian_footmen` | User-specified progression |

**Notes:**
- `landsknecht` stays T3 across all mappers — no T1/T2 variants exist for doppelsoldner pikemen (historically accurate: landsknechts are a late-period unit)
- `chasseur` Late/Ren keys come from the misspelled `chasseurs` entries that already exist in those mappers — fix the misspelling and inherit the key
- `RICE_drokpa_horsemen` started at T2 in High Medieval (user chose T2 over T1 for visual reasons)
- `RICE_nilotic_raiders` switches from slingers (T1/T2) to quilted spearmen (T3) — represents evolution of Nilotic warfare
- `RICE_sudanese_highlanders` uses melee infantry despite CK3 skirmisher tag — represents Sudanese melee fighters, gives different progression from nilotic raiders

**Actionable:** 14 (same as Early Medieval)
**Siege ignored:** 5

---

## Superfluous MAA — Cleaned Up ✅ (20)

### Misspellings fixed (5 → correct keys, reusing Attila mappings)

| Wrong Key | Correct Key | Attila Unit | Factions |
|---|---|---|---|
| `chasseurs` | `chasseur` | `mk_jer_t1_ministeriales` (CAVALRY) | Outremer, Default |
| `landsknechts` | `landsknecht` | `mk_hre_t3_doppelsoldner_pikemen` (INFANTRY) | Teutonic, Default |
| `palace_guard` | `palace_guards` | `mk_khw_t1_junior_ghulaman` (INFANTRY) | Default |
| `Huscarls` | `huscarl` | `mk_dan_t1_huskarls` (INFANTRY) | New English (already in Default + 7 others) |
| `accolade_maa_vanguardss` | `accolade_maa_vanguards` | `mk_ayy_t1_tabardariyya` | Khwarazmian |

### Deleted — No CK3 Equivalent (10)

`RICE_norman_cavalry`, `bedouin_tribesmen`, `chu_ko_nu`, `cichiciquitzo`, `hashashin`, `hindu_recruits`, `macemen`, `shotel_warrior` (singular — `shotel_warriors` plural is valid), `sofa`, `tennataerion`

---

## Missing Cultures (134) — TODO

134 cultures missing — same set as Early Medieval + `cappadocian`. The heritage assignments will reuse the same logic since CK3 mods are the same.

---

## Missing Title Keys (30) — TODO

30 missing title keys related to Crusader/Italian/Germanic titles:

**Counties (9):** c_boulogne, c_brugge, c_genoa, c_guines, c_lille, c_luni, c_pisa, c_trier, c_yperen

**Duchies (15):** d_burgundy, d_cephalonia, d_dyrrachion, d_epirus, d_flanders, d_genoa, d_knights_hospitaler, d_knights_templar, d_osterreich, d_pisa, d_savoie, d_swiss, d_teutonic_order, d_upper_burgundy, d_upper_lorraine

**Kingdoms (6):** k_genoa, k_naples, k_pisa, k_romagna, k_saxony, k_switzerland

---

## Elephant Size Caveat (flagged 2026-04-13)

During the Attila-inferred size-fill pass, 3 elephant rows in this mapper were set from `null` → `CAVALRY`:

- `accolade_maa_lancers,Nubian` → `earl_mak_t1_nubian_elephants`
- `accolade_maa_lancers,Ethiopian` → `earl_zag_t1_war_elephants`
- `accolade_maa_outriders,Ethiopian` → `earl_zag_t1_elephants`

**Concern:** CW XML output passes size as `max="CAVALRY"` verbatim. Unclear whether CW's parser interprets this as "a cavalry-typical count (~80-100)" or as "just a classifier, let Attila's native `num_men` apply." If it's the former, elephants would spawn at cavalry-unit sizes — ~100 elephants per unit is nonsense.

**Other mappers for reference:**
- **MK1212 High/Late/Ren Default elephant rows** were already `CAVALRY` pre-session (authored that way) — if this is a bug, it's a pre-existing one.
- **LOTR (RiE)** uses numeric caps (`20`, `6`, `3`) for elephants — possibly indicating the LOTR author explicitly capped counts to avoid the CAVALRY scaling issue.

**Decision (2026-04-13):** Leave as `CAVALRY` for now (matches pre-existing mapper convention). If in-game testing shows 100-elephant units spawning, revert these 3 rows to `null` or set small numeric caps (e.g. `6`).
