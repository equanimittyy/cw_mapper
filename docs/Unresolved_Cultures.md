# Unresolved Culture Keys — All Official Mappers

## Overview

**Date:** 2026-04-12
**Affected mappers:** All 4 official mappers (Early Medieval 919Mod, High Medieval MK1212, Late Medieval MK1212, Renaissance MK1212)
**Source data used:** CK3 Vanilla, RICE, Africa Plus, Cultures Expanded, Muslim Enhancements, A Game of Thrones

After removing ~616 capitalized display-name duplicates (e.g. `Gallo` removed because correct `gallo` already existed), **~142 culture keys** remain in the mapper files that don't match any culture from the currently known CK3 mods.

These are likely from an unidentified CK3 mod. **Left as-is until the source mod is identified.**

**Note:** Cultures Expanded and Buffed Mongol Invasion were confirmed to NOT add new cultures.

---

## Trailing-Space Typos (5)

These have a trailing space in the culture key — likely copy-paste errors in the original XML.

| Culture Key | Present In |
|---|---|
| `Coigríche ` | High |
| `Jerusaleman ` | High |
| `Turko-Afghan ` | All 4 |
| `kochinim ` | All 4 |
| `tigray ` | All 4 |

---

## Capitalized — No Lowercase Equivalent (11)

These are capitalized display names but unlike the 616 that were removed, there is **no** matching lowercase internal key in the mapper or CK3 source data.

| Culture Key | Present In |
|---|---|
| `Anglo-Nordic` | All 4 |
| `Böhmisch` | All 4 |
| `Coigríche` | All 4 |
| `Gasmoulos` | All 4 |
| `Külföldi` | All 4 |
| `Romansh` | All 4 |
| `Teutonic` | All 4 |
| `Turko-Persian` | All 4 |
| `Ulster-Scot` | All 4 |
| `Wendish` | All 4 |
| `Ænglish` | All 4 |

---

## Lowercase — Unknown Source Mod (126)

All present in all 4 mappers unless noted otherwise.

### Exceptions (not in all 4)

| Culture | Present In |
|---|---|
| `darada` | High, Late, Ren |
| `genoese` | High, Late, Ren |
| `mandinka` | High, Late, Ren |
| `pruthenian` | Late, Ren |
| `romanesque` | Early, High |

### Full List (all 4 mappers)

`aari`, `adyghean`, `afghan`, `african`, `alani`, `amhara`, `amis`, `aquitainian`, `assamese`, `asturian`, `baranis`, `beja`, `belarusian`, `bengali`, `bodpa`, `bohemian_hybrid`, `bono`, `bouxcuengh`, `brahui`, `butr`, `cambrian`, `chuvash`, `circassian`, `copt`, `coptic`, `deilami`, `dregovichian`, `frisian`, `friuli_mpe`, `gaw`, `german`, `germanic`, `gilak`, `guanche`, `gujarati`, `gute`, `habesha`, `hadrami`, `hierosolyman`, `hindustani`, `hlai`, `isaurian_mpe`, `jat`, `jerusaleman`, `kaikani`, `kannada`, `kashmiri`, `khanty`, `khorasani`, `kirati`, `komi`, `krivichian`, `langobard`, `latin_mpe`, `leonese`, `lezgin`, `lhomon`, `lombard`, `macedonian_mpe`, `makrani`, `malvi`, `marathi`, `mashriqi`, `mazanderani`, `mingrelian`, `misri`, `moravian`, `mushuan`, `musta_arabi`, `navarro_aragonese`, `nederfrankish`, `nepali`, `nuba`, `oghuz`, `omotic`, `ongud`, `oriya`, `oropom`, `papuan`, `pashtun`, `peristani`, `polan`, `pomorian`, `pritanian`, `qiang`, `rajput`, `romaios`, `rus`, `samoyed`, `shatuo`, `siculo_arabic`, `sindhi`, `sinhala`, `slovak`, `slovene`, `sumpa`, `svan`, `swear`, `tabari`, `tai`, `tamil`, `tati`, `taureg`, `telugu`, `tervitsian`, `thracian_mpe`, `tsangpa`, `tujia`, `turkish`, `turko_afghan`, `turko_iranian`, `tuscan_ce`, `umbrian_mpe`, `uriankhai`, `veleti`, `vinlandic`, `vyatichian`, `welayta`, `wendish_hybrid`, `yakut`, `zhangzhung`, `zutt`

---

## What Was Fixed (2026-04-12)

Removed **616 capitalized display-name duplicate cultures** across all 4 mapper `.txt` files. These were entries like `Gallo`, `Albanian`, `Flemish` where the correct lowercase CK3 key (`gallo`, `albanian`, `flemish`) already existed in the same mapper.

| Mapper | Duplicates Removed |
|---|---|
| OfficialCW_EarlyMedieval_919Mod | 155 |
| OfficialCW_HighMedieval_MK1212Mod | 153 |
| OfficialCW_LateMedieval_MK1212Mod | 154 |
| OfficialCW_Rennaisance_MK1212Mod | 154 |

---

## Next Steps

1. Identify which CK3 mod provides the 126 lowercase cultures (many look like they could be from a historical cultures/sub-cultures mod)
2. Add that mod to `mod_config.json` for each mapper so validation stops flagging them
3. Fix the 5 trailing-space typos once confirmed they match a real culture key
4. Resolve the 11 capitalized entries — either find their correct internal keys or remove if invalid
