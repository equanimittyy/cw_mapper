# 7K_AGOT_BRR — Working Notes

## Overview

**Mapper:** `7K_AGOT_BRR`
**Session date:** 2026-04-13
**Time Period:** 0–8282 (Before Robert's Rebellion)
**Tag:** AGOT
**Required CK3 Mods:** A Game of Thrones (2962333032)
**Required Attila Mods:** 7K_Overhaul, 7K_Models_and_Textures, 7K_Additional_Houses, 7K_Additional_Houses_2, Lord_Of_The_Tides_Submod_V0.4, 7k_submod_2

## Default Faction Design — Why Essos Slaver Units?

The Default faction uses `Essos_Slaver_MAA_*` units for nearly all its mappings, with `Essos_Wise_Masters` as General.

**IMPORTANT — visual caveat (user-flagged 2026-04-13):** `Essos_Slaver_MAA_Spearmen` and `Essos_Slaver_MAA_Swordsmen` are **actually Ghiscari professional heavy infantry** (Meereenese/Yunkai/Astapor style), not generic sellswords. This means the "aesthetic neutrality" argument is weaker than initially assumed — a Westerosi lord falling back to Default will see tokar-wearing Ghiscari troops, not anonymous armed men.

The original author likely chose these because:
- They're still the **least-Westerosi** option (no recognizable house heraldry)
- The 7K mod may not have a truly neutral generic unit set
- Ghiscari-style troops are at least **foreign-looking** — visually signals "out of place" which is appropriate for a fallback that shouldn't have fired

**USER CHECK:** Consider whether a different Default unit set would be more appropriate. Options to investigate:
- `Essos_Second_MAA_*` (Second Sons — closer to true sellsword aesthetic)
- `Crownlands_Kings_Landing_Golden_Company_*` (sellsword company but limited unit types)
- A Westeros-generic unit set if one exists

`Essos_Wise_Masters` as General — also Ghiscari-flavored, same caveat applies.

**Rule (for now):** When adding new Default fallback entries, prefer `Essos_Slaver_MAA_*` keys to stay consistent with the existing pattern. Use region-specific units when the CK3 MAA itself is region-specific (e.g. `riverlands_light_infantry` uses Riverlands_Tully_MAA_Axemen).

## Current Status

| Category | Status | Notes |
|---|---|---|
| Essos split | **NEW — NEEDS USER REVIEW** | Replaced single Essos faction with Free_Cities (33 entries) + Slaver_Cities (31 entries) |
| Wall Targaryen fix | Done | `handpicked_faithful,Wall` fixed from Dragon to Targaryen |
| Dragon→Targaryen fixes | Done | 5 Default entries fixed: `royal_crossbowmen`, `marsh_walker`, `sea_snakes`, `outriders`, `crownlands_spears` |
| Missing Default entries | Done | 6 added: `accolade_maa_crossbowmen`, `accolade_maa_vanguard`, `giant_regiment`, `gold_cloaks`, `iron_bows`, `iron_pikes` |
| Size/type mismatches | Done | 3 fixed: `westerlands_knights` CAVALRY, `westerosi_sellswords` CAVALRY, `accolade_maa_crossbowers` RANGED |
| Faction MAA sizes | Done | 256 None-sized entries filled (see below) |
| MAA only in Default | 45 | Confirmed intentional — all region-specific |
| Title MAA sizes | Done | 2,351 None-sized entries filled (suffix inference + 2 manual) |
| Duplicate keys | N/A | `accolade_maa_vanguards` vs `accolade_maa_vanguard` — distinct CK3 keys, both mapped |

---

## Essos Split: Free_Cities + Slaver_Cities Factions (NEEDS USER REVIEW)

Originally added a single `Essos` faction using `Essos_Slaver_MAA_*` as base. User flagged that those units are Ghiscari professional heavy infantry, NOT generic sellswords — wrong cultural fit for Free Cities. Split into two factions:

### Free_Cities (33 entries)
**Cultures (10):** essosi_valyrian, braavosi, lyseni, myrish, norvoshi, pentoshi, qohorik, tyroshi, volantene, lorathi
**Unit base:** `Essos_Second_MAA_*` (Second Sons sellsword aesthetic)
**GENERAL:** `Essos_Second_MAA_Lance_Cavalry`
**KNIGHTS:** `Essos_Second_MAA_Mounted_Swordsmen`
**LEVY:** Spearmen 35% / Swordsmen 25% / Crossbowmen 25% / Axemen 15% (Myrish crossbow flavor)
**Free Cities-specific MAA:** cohort_of_the_three_thousand, myrish_crossbows, purple_sailors, stepstone_sailors, sun_guard, weeping_guard, westerosi_sellswords

### Slaver_Cities (31 entries)
**Cultures (10):** gogossosi, mantaryan, tolosi, elyrian, essarian, hartalari, painted_clansman, rhoynish, selhori, summer_rhoynish
**Unit base:** `Essos_Slaver_MAA_*` (Ghiscari professional heavy infantry) + `Essos_Targaryen_Unsullied_*` flavoring
**GENERAL:** `Essos_Slaver_MAA_Lance_Cavalry`
**KNIGHTS:** `Essos_Slaver_MAA_Mounted_Swordsmen`
**LEVY:** Spearmen 35% / Swordsmen 25% / Longbowmen 20% / Axemen 20%
**Slaver Cities-specific MAA:** indentured_legion, moroshi_pikes, ornate_helms, seal_hunters, unsullied

### Logic
- **Free_Cities** covers western/mercantile Free Cities — sellsword-hiring, cosmopolitan. Second Sons aesthetic fits.
- **Slaver_Cities** covers eastern Valyrian remnants (Tolos, Elyria, Mantarys, Gogossos) which are slave economies close to Slaver's Bay culturally, plus the Rhoynish (spear-focused, Unsullied as closest fit) and painted_clansman.
- No dedicated Rhoynish unit set exists — merging with Slaver_Cities is the least-bad option.

### Review Checklist
- [ ] Verify Second Sons units visually fit the Free Cities cultures (Braavos, Myr, Volantis, etc.)
- [ ] Verify Slaver units visually fit the Valyrian Remnants + Rhoynish cultures
- [ ] Check `Essos_Daario_Naharis` as GENERAL — is he appropriate for a faction-wide commander or too specific?
- [ ] Confirm levy compositions play well (both at 100%)
- [ ] Verify Rhoynish cultures (rhoynish, selhori, summer_rhoynish) in Slaver_Cities look acceptable despite lore mismatch
- [ ] Once reviewed, apply same split to `7K_AGOT_ARR.txt`

### Structure

| Type | Attila Unit | Notes |
|---|---|---|
| GENERAL | `Essos_Wise_Masters` | Same as Default |
| KNIGHTS | `Essos_Slaver_MAA_Lance_Cavalry` | Same as Default |
| LEVY 1 | `Essos_Slaver_MAA_Spearmen` (25%) | Balanced 4-way split |
| LEVY 2 | `Essos_Slaver_MAA_Swordsmen` (25%) | |
| LEVY 3 | `Essos_Slaver_MAA_Longbowmen` (25%) | |
| LEVY 4 | `Essos_Slaver_MAA_Axemen` (25%) | |

### Common MAA (all regional factions have these)

| CK3 MAA | Attila Unit |
|---|---|
| `accolade_maa_archers` | `Essos_Slaver_MAA_Longbowmen` |
| `accolade_maa_crossbowmen` | `Essos_Slaver_MAA_Crossbowmen` |
| `accolade_maa_lancers` | `Essos_Slaver_MAA_Lance_Cavalry` |
| `accolade_maa_outriders` | `Essos_Slaver_MAA_Mounted_Swordsmen` |
| `accolade_maa_pikes` | `Essos_Slaver_MAA_Pikemen` |
| `accolade_maa_skirmishers` | `Essos_Slaver_MAA_Axemen` |
| `accolade_maa_vanguard` | `Essos_Slaver_MAA_Halberdiers` |
| `handpicked_faithful` | `Essos_Slaver_MAA_Halberdiers` |
| `house_guard` | `Essos_Slaver_MAA_Halberdiers` |
| `maa_bandits` | `Essos_Slaver_MAA_Axemen` |
| `maa_marauders` | `Essos_Slaver_MAA_Mounted_Swordsmen` |
| `maa_poachers` | `Essos_Slaver_MAA_Longbowmen` |
| `maa_thieves` | `Essos_Slaver_MAA_Spearmen` |

### Standard MAA (most regional factions have these)

| CK3 MAA | Attila Unit | Notes |
|---|---|---|
| `armored_footmen` | `Essos_Slaver_MAA_Swordsmen` | |
| `armored_horsemen` | `Essos_Slaver_MAA_Lance_Cavalry` | |
| `bowmen` | `Essos_Slaver_MAA_Longbowmen` | |
| `crossbowmen` | `Essos_Second_MAA_Crossbowmen` | Uses Second Sons — Myrish crossbow flavor |
| `light_footmen` | `Essos_Slaver_MAA_Axemen` | |
| `light_horsemen` | `Essos_Slaver_MAA_Mounted_Swordsmen` | |
| `pikemen_unit` | `Essos_Slaver_MAA_Pikemen` | |

### Essos-Specific MAA

| CK3 MAA | Attila Unit | Notes |
|---|---|---|
| `cohort_of_the_three_thousand` | `Essos_Second_MAA_Billmen` | Second Sons sellsword company |
| `indentured_legion` | `Essos_Targaryen_Unsullied_Spearmen` | Slave soldier spearmen |
| `moroshi_pikes` | `Essos_Slaver_MAA_Halberdiers` | Morosh (Ghiscari city) pikes |
| `myrish_crossbows` | `Essos_Second_MAA_Crossbowmen` | Famous Myrish crossbowmen |
| `ornate_helms` | `Essos_Slaver_MAA_Pikemen` | Decorative helmed pikemen |
| `purple_sailors` | `Essos_Slaver_MAA_Axemen` | Braavosi/Tyroshi sailors |
| `seal_hunters` | `Essos_Slaver_MAA_Axemen` | Ibbenese hunters |
| `stepstone_sailors` | `Essos_Slaver_MAA_Billmen` | Pirate isles fighters |
| `sun_guard` | `Essos_Slaver_MAA_Halberdiers` | Volantene triarch guard |
| `unsullied` | `Essos_Targaryen_Unsullied_Pikemen` | Elite slave-soldier pikemen |
| `weeping_guard` | `Essos_Slaver_MAA_Halberdiers` | Lys/Volantis guard |
| `westerosi_sellswords` | `Essos_Slaver_MAA_Lance_Cavalry` | Exiled knights as sellswords |

### Review Checklist

- [ ] Load BRR mapper in GUI, inspect Essos faction entries
- [ ] Verify Attila unit appearances match intended Essosi military identity
- [ ] Check if `Essos_Second_MAA_*` vs `Essos_Slaver_MAA_*` choices look right visually
- [ ] Confirm levy percentages (25/25/25/25) play well — adjust if needed
- [ ] Check if any Essos-specific CK3 MAA are missing from the faction
- [ ] Once reviewed, apply same faction to `7K_AGOT_ARR.txt`

### Cultures Served

These 20 cultures now resolve to the Essos faction:

**heritage_valyrian:** essosi_valyrian, braavosi, gogossosi, mantaryan, tolosi, elyrian, volantene, painted_clansman, essarian, lorathi, lyseni, myrish, hartalari, norvoshi, pentoshi, qohorik, tyroshi

**heritage_rhoynish:** rhoynish, selhori, summer_rhoynish

---

## Fixes Applied

### Wall `handpicked_faithful` — Targaryen Era Fix

`handpicked_faithful,Wall` was mapped to `Crownlands_Dragon_MAA_Halberdiers` — incorrect for BRR (pre-rebellion Targaryen era). Changed to `Crownlands_Targaryen_MAA_Halberdiers` which exists in the additional houses TSV.

The other `Crownlands_Dragon_MAA_Halberdiers` reference (title mapping for `k_dragonstone`) was left as-is — Dragon-themed is correct for Dragonstone regardless of era.

---

## Outstanding Issues

### Missing from Default (6 MAA)

These MAA exist in regional factions but have no Default fallback (crash risk if triggered by an unassigned culture):

| MAA | In Factions |
|---|---|
| `accolade_maa_crossbowmen` | All 10 regional factions |
| `accolade_maa_vanguard` | All 10 regional factions |
| `giant_regiment` | All_Factions only |
| `gold_cloaks` | Crownlands only |
| `iron_bows` | Iron_Islands only |
| `iron_pikes` | Iron_Islands only |

### Size/Type Mismatches (3)

| MAA,Faction | Attila Unit | Current Size | Expected |
|---|---|---|---|
| `westerlands_knights,Default` | `Westerlands_Lannister_MAA_Lance_Cavalry` | INFANTRY | CAVALRY? |
| `westerosi_sellswords,Default` | `Essos_Slaver_MAA_Lance_Cavalry` | INFANTRY | CAVALRY? |
| `accolade_maa_crossbowers,Default` | `Essos_Slaver_MAA_Crossbowmen` | INFANTRY | RANGED? |

### Default Mapping Fix — `riverlands_light_infantry`

Changed from `Riverlands_Tully_MAA_Crossbowmen` (RANGED Attila unit) to `Riverlands_Tully_MAA_Axemen` (INFANTRY). The CK3 MAA is "light infantry" so an infantry Attila unit is correct. Uses the Riverlands-specific unit rather than Essos_Slaver because the MAA is Riverlands-specific.

**USER CHECK:** Verify what `Riverlands_Tully_MAA_Axemen` actually looks like in Attila. It's now the Default fallback for `riverlands_light_infantry` — make sure its visual appearance fits "light infantry" and not heavy axe troops.

### Faction MAA Size Backfill (256 entries)

All regional faction MAA entries originally had `null` sizes — only Default had explicit size types. Sizes were inferred by copying the Default faction's size for the same CK3 MAA key across all regional factions.

- **254 entries** filled from Default's size assignment
- **2 entries** (`wolfswood_hunters` Default + North) had no size anywhere — set to RANGED (maps to `North_Stark_MAA_Longbowmen`)
- **12 `light_footmen` entries** had a hardcoded `400` unit count instead of a type — changed to INFANTRY

**Method:** For each None-sized regional entry, the script checked if Default had a size for the same CK3 MAA key. If so, that size was applied. This is safe because the size reflects the CK3 MAA's unit classification (INFANTRY/CAVALRY/RANGED), which is the same regardless of which Attila unit it maps to in a given faction.
