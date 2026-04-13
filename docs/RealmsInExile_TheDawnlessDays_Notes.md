# OfficialCW_RealmsInExile_TheDawnlessDays — Working Notes

## Overview

**Mapper:** `OfficialCW_RealmsInExile_TheDawnlessDays`
**Session date:** 2026-04-13
**Required CK3 Mods:** Realms In Exile (2291024373)
**Required Attila Mods:** The Dawnless Days (TDD) + 4 submods: `rom_exe_extended_elves`, `war_for_the_mountains`, `the_last_breath`, `fiefs_of_gondor`

## Current Status

| Category | Status | Notes |
|---|---|---|
| Marchwarden placeholders | Done | 3 Lothlorien accolade rows — invalid literal `Marchwarden` replaced |
| Khazad junk placeholder keys | Done | 6 rows with Attila-prefix CK3 keys — verified absent from RiE's 865 MAA |
| Balin's Expedition junk copies | Done | 6 matching rows in `d_balins_expedition` title also removed |
| Invalid `Shieldwall Arbalests,Umbar` | Done | Spaces + title-case → illegal CK3 MAA key |
| AGOT mapper cross-contamination | Done | 3 full AGOT titles deleted (54 MAA rows + 3 TITLE_NAMES) |
| Null MAA sizes | Done | 1,156 filled from Default (0 remaining) |
| Orphan heritages (resolvable) | Done | 11 culture entries added across 6 heritages |
| Orphan heritages (unresolved) | **Left as-is** | 6 heritages — PARENT_KEY fallback retained |

---

## Fixes Applied

### Marchwarden Placeholders → Real Units (3 rows, Lothlorien)

Literal `Marchwarden` is not a valid Attila unit key. Replaced following other Elf factions' archer/skirmisher split pattern.

| Row | Old Attila key | New Attila key | New Size |
|---|---|---|---|
| `accolade_maa_archers,Lothlorien` | `Marchwarden` | `loth_galad_bow_warriors` | RANGED |
| `accolade_maa_crossbowmen,Lothlorien` | `Marchwarden` | `loth_galad_bow_warriors` | RANGED |
| `accolade_maa_skirmishers,Lothlorien` | `Marchwarden` | `loth_wardens_fences` | RANGED |

**Why:** `loth_wardens_fences` is literally the TDD Marchwardens unit ("Wardens of the Fences" — Haldir's border guards). `loth_galad_bow_warriors` matches existing `bowmen,Lothlorien`. Pattern mirrors Lindon/Eregion.

### Khazad Junk Placeholder Keys (6 rows deleted)

All 6 CK3 MAA keys verified absent from RiE's actual MAA definitions (cli_data with 865 MAA, 133 RiE cultures):

| CK3 key | Reason deleted |
|---|---|
| `khz_legionaries,Khazad` | Not in RiE; Attila-style prefix not a RiE convention |
| `khz_durins_gate_guard,Khazad` | Not in RiE; redundant with `KNIGHTS,Khazad` and `accolade_maa_pikes,Khazad` |
| `khz_crossbows,Khazad` | Not in RiE; redundant with `bowmen`, `crossbowmen`, both archer accolades |
| `ere_baruk_guard,Khazad` | Not in RiE |
| `ere_merc_cav,Khazad` | Not in RiE; redundant with `light_horsemen` across Dwarf factions |
| `roh_eored_gap,Khazad` | Rohan MAA in a Dwarven faction — category error, not in RiE |

**Verification:** Fuzzy search on `khz_*`, `ere_*`, `roh_*` prefixes in RiE cultures/MAA returned zero hits for these keys. RiE uses thematic snake_case (`riders_of_rohan`, `donan_slingers`) not Attila-style prefixes.

### Balin's Expedition Junk Copies (6 rows deleted)

Same 6 junk keys appeared in `d_balins_expedition` title (title name: "Khazad"). Clearly mirrored from the Khazad faction mapping. Removed for consistency.

### Invalid `Shieldwall Arbalests,Umbar` (1 row deleted)

CK3 MAA keys must be snake_case lowercase. `Shieldwall Arbalests` has spaces + title-case — CK3 engine cannot emit this key, so the row was dead code. Attila target (`umb_lb_corsair_archers`) is a real TDD/Last Breath unit, but no reachable CK3 MAA targets it in this mapper (Umbar already has `umb_black_haven_marksmen` covering bow/crossbow slots).

### AGOT Mapper Cross-Contamination (54 title rows + 3 names)

Three entire AGOT titles got pasted in from a 7K mapper. Attila targets reference 7K mod units not loaded here.

| Title | TITLE_NAMES value | Rows |
|---|---|---|
| `c_lannisport` | Lordship of Lannisport | 19 |
| `c_wayleroot` | Lordship of Wayleroot | 17 |
| `e_the_iron_throne` | The Iron Throne | 18 |

Attila targets were `Westerlands_Lannisport_MAA_*`, `Riverlands_Vypren_MAA_*`, `Stormlands_Baratheon_MAA_*`, `Crownlands_Kings_Landing_Goldcloak_*` — none in this mapper's Attila mod list.

### Null MAA Sizes Backfill (1,156 rows)

Default faction had 0 null entries and unambiguous CK3 MAA → size mapping. Used as source of truth:

- **FACTIONS_AND_MAA:** 701 null rows → all filled (0 remaining)
- **TITLES_AND_MAA:** 499 null rows resolvable via Default → filled; other 11 auto-resolved after junk/AGOT cleanup

Unicode faction names (`Ringló Vale`, `Khamûl`) required encoding composite keys as JSON `\uXXXX` escapes to match the file's storage format.

### Orphan Heritage Culture Entries (11 rows added, 6 heritages)

Heritages that had only PARENT_KEY set — added culture-level entries for the 6 heritages with real RiE cultures:

| Heritage | Parent Faction | Cultures Added |
|---|---|---|
| `heritage_eastern_adunaic` | Umbar | `east_adunai_colonial` |
| `heritage_harshandatt` | Khand | `muranian` |
| `heritage_magri` | Umbar | `mag` |
| `heritage_mordorrim` | Mordor | `mordorrim` |
| `heritage_thani_native` | Haradrim | `adena`, `drel`, `pel` |
| `heritage_womaw` | Easterlings | `womaw`, `lokhaw`, `codyan`, `vulmaw` |

All cultures inherit the PARENT_KEY faction assignment — no lore reason to split.

---

## Unresolved / Left As-Is

### 6 Heritages with No RiE Cultures in cli_data

PARENT_KEY entries retained (safe fallback). These may be defined in a submod or legacy content not covered by current cli_data export:

| Heritage | Parent Faction |
|---|---|
| `heritage_kirani` | Umbar |
| `heritage_new_sirayni` | Haradrim |
| `heritage_old_sirayni` | Haradrim |
| `heritage_shayn` | Haradrim |
| `heritage_south_khailuza` | Khand |
| `heritage_troll` | Orc |

`heritage_troll` is lore-important (Mordor trolls) — its absence in cli_data is notable but PARENT_KEY → Orc faction covers any runtime emission.

---

## Final Counts

| Section | Before | After | Delta |
|---|---|---|---|
| FACTIONS_AND_MAA | 1,304 | 1,297 | −7 |
| TITLES_AND_MAA | 570 | 510 | −60 |
| HERITAGES_AND_CULTURES | 280 | 291 | +11 |
| TITLE_NAMES | 30 | 27 | −3 |
| Null sizes | 1,211 | 0 | −1,211 |

**File integrity:** UTF-8 BOM + CRLF line endings + 4-space JSON indentation preserved throughout. JSON valid after every edit.
