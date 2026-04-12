# 7K_AGOT_ARR — Working Notes

## Overview

**Mapper:** `7K_AGOT_ARR`
**Session date:** 2026-04-13
**Time Period:** 8283–15000 (After Robert's Rebellion)
**Tag:** AGOT
**Required CK3 Mods:** A Game of Thrones (2962333032)
**Required Attila Mods:** 7K_Overhaul, 7K_Models_and_Textures, 7K_Additional_Houses, 7K_Additional_Houses_2, Lord_Of_The_Tides_Submod_V0.4, 7k_submod_2

## Current Status

| Category | Status | Notes |
|---|---|---|
| Essos faction | **PENDING** | Will be copied from BRR once reviewed in-game |
| Missing Default entries | Done | 7 added (same 6 as BRR + `wolfswood_hunters`) |
| Size/type mismatches | Done | 3 fixed: `westerlands_knights` CAVALRY, `westerosi_sellswords` CAVALRY, `accolade_maa_crossbowers` RANGED |
| Faction MAA sizes | Done | 174 None-sized entries filled + 1 numeric `400` changed to INFANTRY + 2 `winter_wolves` set to INFANTRY |
| Title MAA sizes | Done | 2,316 None-sized entries filled (176 from Attila key match, 2,140 from suffix pattern) |
| Heritage orphan factions | `Essos` | Will resolve when Essos faction is added |
| Duplicate keys | 1 flagged | `accolade_maa_vanguards` vs `accolade_maa_vanguard` — needs CK3 verification |

---

## Fixes Applied (mirrored from BRR)

### Missing Default Entries (7)

| MAA | Attila Unit | Size | Notes |
|---|---|---|---|
| `accolade_maa_crossbowmen` | `Essos_Slaver_MAA_Crossbowmen` | RANGED | Follows Default accolade pattern |
| `accolade_maa_vanguard` | `Essos_Slaver_MAA_Halberdiers` | INFANTRY | Follows Default accolade pattern |
| `giant_regiment` | `BTW_Wildling_MAA_Spearmen` | INFANTRY | Wildling unit, only thematic fit |
| `gold_cloaks` | `Essos_Slaver_MAA_Swordsmen` | INFANTRY | Neutral default (not house-specific) |
| `iron_bows` | `Essos_Slaver_MAA_Longbowmen` | RANGED | Generic ranged fallback |
| `iron_pikes` | `Essos_Slaver_MAA_Spearmen` | INFANTRY | Generic spear fallback |
| `wolfswood_hunters` | `North_Stark_MAA_Longbowmen` | RANGED | Not in BRR Default, added here |

### Size/Type Mismatches (3)

| MAA,Faction | Attila Unit | Old Size | New Size |
|---|---|---|---|
| `westerlands_knights,Default` | `Westerlands_Lannister_MAA_Lance_Cavalry` | INFANTRY | CAVALRY |
| `westerosi_sellswords,Default` | `Essos_Slaver_MAA_Lance_Cavalry` | INFANTRY | CAVALRY |
| `accolade_maa_crossbowers,Default` | `Essos_Slaver_MAA_Crossbowmen` | INFANTRY | RANGED |

### Faction MAA Size Backfill

- **172 entries** filled from Default's size assignment
- **2 entries** (`winter_wolves` Default + North) had no size anywhere — set to INFANTRY (maps to `North_Stark_MAA_Swordsmen`)
- **1 `light_footmen,Default`** had hardcoded `400` — changed to INFANTRY

### Title MAA Size Backfill

- **176** filled from matching Attila keys in faction mappings
- **2,140** filled from Attila key suffix patterns

---

## Pending: Essos Faction

The BRR mapper has a new Essos faction (38 entries) that needs user review in Attila/CK3 before being copied to ARR. Until then, the 20 Essosi cultures assigned to `Essos` in the heritage mappings will fall through to Default.

See `AGOT_BRR_Notes.md` for the full Essos faction documentation and review checklist.
