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

## Initial State (from summary_log.txt)

| Category | Count | Severity |
|---|---|---|
| Missing MAA (crash risk) | 19 | 🔴 |
| Missing Attila Unit Keys | 2 | 🔴 |
| Missing Title Keys | 30 | 🟡 |
| Superfluous MAA | 21 | 🟡 |
| Missing Cultures | 134 | 🟡 |
| Superfluous Cultures | 224 | 🟡 |

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
| `black_armor_cavalry` | TODO | Chinese MAA → Tibetan |
| `RICE_iron_forest` | TODO | Chinese MAA → Tibetan |
| `chasseur` | TODO | → Outremer (after fixing misspelling) |
| `landsknecht` | TODO | → Teutonic (after fixing misspelling) |
| `palace_guards` | TODO | → Default (after fixing misspelling) |
| `danish_obudshaer` | TODO | → Danelander (elite spearmen per CK3) |
| `danish_svenner` | TODO | → Danelander (light cavalry per CK3) |
| `outremer_bowmen` | TODO | → Outremer |
| `outremer_heavy_cavalry` | TODO | → Outremer |
| `outremer_turcopoles` | TODO | → Outremer |
| `RICE_alodian_cavalry` | TODO | → Horn African |
| `RICE_drokpa_horsemen` | TODO | → Tibetan |
| `RICE_nilotic_raiders` | TODO | → Horn African |
| `RICE_sudanese_highlanders` | TODO | → Horn African |

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
