# All Mappers — Change Summary

One table per mapper. For full detail, see the individual `*_Notes.md` files.

**Last updated:** 2026-04-13

---

## OfficialCW_EarlyMedieval_919Mod

| Field | Value |
|---|---|
| Setting / Era | Historical — 919 AD |
| Attila mods | Age of Charlemagne + Vanilla |
| CK3 mods | Vanilla + 919Mod + Africa Plus + Cultures Expanded + More Traditions v2 + Muslim Enhancements + RICE + BMI |
| Missing MAA | 17 → 14 mapped + 3 siege ignored |
| Superfluous MAA | 20 → 14 deleted + 6 misspelling fixes |
| Missing cultures | 133 → 131 mapped (2 placeholders deferred) |
| New heritage added | `heritage_buyeo` (ancient Korean → Tibetan) |
| Notable MAA added | `black_armor_cavalry`, `RICE_iron_forest`, `RICE_drokpa_horsemen`, Horn African RICE trio, Outremer set, `danish_obudshaer`, `danish_svenner`, `landsknecht`, `palace_guards` |
| Misspelling fixes | `chasseurs→chasseur`, `landsknechts→landsknecht`, `palace_guard→palace_guards`, `Huscarls→huscarl` |
| Notable removal | 400-line block of invalid DEFAULT Attila keys (would have crashed CW) |
| Status | Stable |

---

## OfficialCW_HighMedieval_MK1212Mod

| Field | Value |
|---|---|
| Setting / Era | Historical — 1212 AD |
| Attila mods | MK1212 + Realistic Overhauls + Cilicia Revamp |
| Tier | T1 |
| Missing MAA | 19 → 14 mapped + 5 siege ignored |
| Missing Attila unit keys | 2 → 2 wrong-reference fixes |
| Missing title keys | 30 → 30 trailing-space fixes |
| Superfluous MAA | 21 → 15 deleted + 5 misspellings + 1 typo |
| Missing cultures | 134 → 132 mapped (2 placeholders) |
| Trailing spaces in keys | ~582 trimmed |
| Attila key fixes | `ghu_t1_afghan_spearmen→mk_ghu_t1_afghan_spearmen`; `mk_mio_t1_spanish_order_knights_dismounted→mk_cas_t1_order_knights_dismounted` |
| Title fix | `accolade_maa_vanguardss→accolade_maa_vanguards` |
| Elephant caveat rows | 3 set to CAVALRY |
| Status | Stable |

---

## OfficialCW_LateMedieval_MK1212Mod

| Field | Value |
|---|---|
| Setting / Era | Historical — late 13th–14th c. |
| Attila mods | MK1212 |
| Tier | T2 (85% of units) |
| Superfluous MAA deleted | 14 |
| Misspelling fixes | 4 |
| New MAA mapped | 11 (+ Default) |
| Missing cultures added | 132 |
| New heritage added | `heritage_buyeo` |
| Trailing spaces fixed | ~593 |
| Tier-upgrade examples | `black_armor_cavalry→mk_mon_t2_golden_keshiq_lancers`; `danish_obudshaer→mk_bur_t2_pavise_spearmen`; `outremer_heavy_cavalry→mk_mio_t2_templar_knights`; `RICE_alodian_cavalry→mk_mak_t2_nubian_knights` |
| Elephant caveat rows | 3 set to CAVALRY |
| Status | Stable |

---

## OfficialCW_Rennaisance_MK1212Mod

| Field | Value |
|---|---|
| Setting / Era | Historical — 15th c. |
| Attila mods | MK1212 |
| Tier | T3 (82% of units) |
| Superfluous MAA deleted | 14 |
| Misspelling fixes | 4 |
| New MAA mapped | 11 (+ Default) |
| Missing cultures added | 132 |
| New heritage added | `heritage_buyeo` |
| Trailing spaces fixed | ~601 |
| Tier-upgrade examples | `black_armor_cavalry→mk_mon_t3_golden_keshiq_lancers`; `danish_obudshaer→mk_merc_swi_t3_swiss_pikemen`; `outremer_heavy_cavalry→mk_mio_t3_templar_knights`; `RICE_alodian_cavalry→mk_mak_t3_nubian_knights`; `palace_guards→mk_ghu_t3_royal_paiks` |
| Refined progression | `rice_alodian_cavalry` |
| Elephant caveat rows | 5 set to CAVALRY (incl. 2 `accolade_maa_elephantiers`) |
| Status | Stable |

---

## 7K_AGOT_BRR

| Field | Value |
|---|---|
| Setting / Era | Westeros — Before Robert's Rebellion (0–8282) |
| Attila mods | 7K Overhaul + Additional Houses + LotT + 7k_submod_2 |
| CK3 mods | A Game of Thrones (2962333032) |
| Essos split | Single `Essos` → `Free_Cities` (33) + `Slaver_Cities` (31), user-verified |
| Default aesthetic | Ghiscari `Essos_Slaver_MAA_*` → Second Sons `Essos_Second_MAA_*` (39 rows) |
| Default GENERAL/KNIGHTS | Now mirror Free_Cities pattern |
| Missing Default entries added | 6 |
| Size/type mismatches fixed | 3 (`westerlands_knights`, `westerosi_sellswords`, `accolade_maa_crossbowers`) |
| Faction MAA null sizes filled | 256 |
| Title MAA null sizes filled | 2,351 |
| Era fix | `handpicked_faithful,Wall`: Dragon → Targaryen (pre-rebellion) |
| Default Dragon→Targaryen fixes | 5 (`royal_crossbowmen`, `marsh_walker`, `sea_snakes`, `outriders`, `crownlands_spears`) |
| Out-of-era halberds | Fixed via Targaryen/Crownlands key swap |
| Status | User-verified |

---

## 7K_AGOT_ARR

| Field | Value |
|---|---|
| Setting / Era | Westeros — After Robert's Rebellion (8283–15000) |
| Attila mods | Same as BRR |
| CK3 mods | A Game of Thrones (2962333032) |
| Essos split | `Free_Cities` (32) + `Slaver_Cities` (32), copied from BRR, user-verified |
| Default aesthetic | Slaver → Second Sons swap (37 rows), mirrors Free_Cities |
| Missing Default entries added | 7 (BRR's 6 + `wolfswood_hunters`) |
| Size/type mismatches fixed | 3 (same as BRR) |
| Faction MAA null sizes filled | 174 (+ 2 `winter_wolves` → INFANTRY, 1 hardcoded `400` → INFANTRY) |
| Title MAA null sizes filled | 2,316 (176 from Attila match, 2,140 from suffix pattern) |
| Default fix | `riverlands_light_infantry`: Crossbowmen → Axemen (INFANTRY) |
| Status | User-verified |

---

## OfficialCW_RealmsInExile_TheDawnlessDays

| Field | Value |
|---|---|
| Setting / Era | Middle-earth — Third Age |
| Attila mods | The Dawnless Days + `rom_exe_extended_elves` + `war_for_the_mountains` + `the_last_breath` + `fiefs_of_gondor` |
| CK3 mods | Realms In Exile (2291024373) |
| Marchwarden placeholders | 3 Lothlorien rows replaced with real units |
| Khazad junk keys deleted | 6 (Attila-prefix keys absent from RiE) |
| Balin's Expedition duplicates | 6 (mirrors of Khazad junk) |
| Illegal CK3 key deleted | `Shieldwall Arbalests,Umbar` (spaces + title-case) |
| AGOT cross-contamination removed | 3 full titles (54 MAA rows + 3 TITLE_NAMES) |
| Null sizes filled | 1,156 (701 FACTIONS + 499 TITLES + 11 auto-resolved) |
| Orphan heritages resolved | 11 culture entries added across 6 heritages |
| Orphan heritages remaining | 6 (PARENT_KEY fallback retained) |
| FACTIONS_AND_MAA delta | 1,304 → 1,297 (−7) |
| TITLES_AND_MAA delta | 570 → 510 (−60) |
| HERITAGES_AND_CULTURES delta | 280 → 291 (+11) |
| TITLE_NAMES delta | 30 → 27 (−3) |
| Status | Cleaned |

---

## Reference Files

- `docs/EarlyMedieval_919Mod_Notes.md`
- `docs/HighMedieval_MK1212Mod_Notes.md`
- `docs/LateMedieval_MK1212Mod_Notes.md`
- `docs/Rennaisance_MK1212Mod_Notes.md`
- `docs/AGOT_BRR_Notes.md`
- `docs/AGOT_ARR_Notes.md`
- `docs/RealmsInExile_TheDawnlessDays_Notes.md`
- `docs/MK1212_Tier_Reference.md`
- `docs/Unresolved_Cultures.md`
