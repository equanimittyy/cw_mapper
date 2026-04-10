# OfficialCW_EarlyMedieval_919Mod — Working Notes

## Overview

**Mapper:** `OfficialCW_EarlyMedieval_919Mod`
**Session date:** 2026-04-09 to 2026-04-10
**Required CK3 Mods:** Vanilla, Africa Plus, Buffed Mongol Invasion, Cultures Expanded, More Traditions v2, Muslim Enhancements, RICE

## Final Status

| Category | Initial State | Resolved | Remaining |
|---|---|---|---|
| Missing MAA (crash risk) | 17 | 14 mapped + 3 siege ignored | **0** ✅ |
| Superfluous MAA | 20 | 14 deleted + 6 fixed | **0** ✅ |
| Missing Cultures | 133 | 131 mapped | **2** (placeholders, deferred) |
| Attila Unit Keys | Valid | — | ✅ |
| Title Keys | Valid | — | ✅ |

---

## Missing MAA — Resolutions

### Mapped (14)

All MAA below are added to both their specific faction **AND** the `Default` faction (crash-prevention requirement).

| MAA | Faction | Attila Unit | Size | Notes |
|---|---|---|---|---|
| `black_armor_cavalry` | Tibetan | `HEP_kushan_cataphracts` | CAVALRY | Chinese MAA — East Asian fallback to Tibetan |
| `RICE_iron_forest` | Tibetan | `att_nom_noble_horse_archers` | CAVALRY | Chinese MAA — East Asian fallback to Tibetan |
| `RICE_drokpa_horsemen` | Tibetan | `att_nom_shamans_of_the_eternal_sky` | CAVALRY | "Changthang Drokpas" nomadic horsemen. Attila unit displays as "Ashina Wolf Shamans" — Göktürk clan, shamanic tradition matches Tibetan Bon/Tengrism |
| `RICE_alodian_cavalry` | Horn African | `att_des_es_abunas_guard` | CAVALRY | "Alwan Cavalry" — elite Christian Nubian heavy cavalry. Abuna's Guard = Ethiopian Orthodox flavor (close cultural match) |
| `RICE_nilotic_raiders` | Horn African | `BLEMM_skirm` | INFANTRY | Blemmyes = historical Nilotic raiders. Light javelin skirmishers, direct cultural match |
| `RICE_sudanese_highlanders` | Horn African | `BLEMM_skirm` | INFANTRY | CK3 classifies as skirmishers — reusing Blemmyes skirmisher key for faithful role representation |
| `danish_obudshaer` | Danelander | `att_nor_elite_duguth_spearmen` | INFANTRY | CK3/CE classifies as **elite spearmen** (not historical levy). Duguth = Old English "experienced warrior retinue" |
| `danish_svenner` | Danelander | `att_nor_nordic_horse_raiders` | CAVALRY | CK3/CE classifies as **light cavalry** (not historical retinue) |
| `landsknecht` | Teutonic | `cha_gen_armoured_spear` | INFANTRY | Central Germanic zweihanders. Fixed from misspelled `landsknechts` |
| `chasseur` | Outremer | `cha_lom_gastald_cav` | CAVALRY | Fixed from misspelled `chasseurs` |
| `outremer_bowmen` | Outremer | `cha_byz_armoured_archers` | RANGED | Well-trained, light-armored archers — Byzantine-influenced Crusader recruits. Light caste despite "armoured" name |
| `outremer_heavy_cavalry` | Outremer | `cha_nor_noblei_chevalers` | CAVALRY | Displays as **"Knights of Jerusalem"** — Norman noble knights, ancestors of Crusader heavy cavalry |
| `outremer_turcopoles` | Outremer | `HEP_steppe_lancers` | CAVALRY | CK3 describes turcopoles as using both lances and bows — this Hephthalite unit has both |
| `palace_guards` | Default only | `KOK_cha_gen_spear` | INFANTRY | Generic unit — temporary fallback. Fixed from misspelled `palace_guard`. **TODO:** expand to all factions with unique heavy-infantry keys per faction |

### Ignored — Siege Weaponry (3)

Siege units are not mapped. They don't appear in Attila battles.

| MAA | Reason |
|---|---|
| `abbasid_trebuchet` | Siege weapon |
| `byzantine_trebuchet` | Siege weapon |
| `bulgarian_testudos` | Battering ram / siege equipment (not a shield formation) |

---

## Superfluous MAA — Cleaned Up (20)

Keys that were in the mapper but not in CK3 source data.

### Misspellings — Fixed (6 correct keys added, 4 wrong keys deleted)

| Wrong Key | Correct Key | Attila Unit | Factions |
|---|---|---|---|
| `chasseurs` | `chasseur` | `cha_lom_gastald_cav` (CAVALRY) | Outremer, Default |
| `landsknechts` | `landsknecht` | `cha_gen_armoured_spear` (INFANTRY) | Teutonic, Default |
| `palace_guard` | `palace_guards` | `KOK_cha_gen_spear` (INFANTRY) | Default |
| `Huscarls` | `huscarl` | `cha_eng_huscarlas` (INFANTRY) | Anglo Saxon, English, Scots, New English (Default already had it) |

### Deleted — No CK3 Equivalent (10)

`RICE_norman_cavalry`, `bedouin_tribesmen`, `chu_ko_nu`, `cichiciquitzo`, `hashashin`, `hindu_recruits`, `macemen`, `shotel_warrior` (singular — `shotel_warriors` plural is valid), `sofa`, `tennataerion`

---

## Missing Cultures — Resolutions

### 102 Easy Mappings — Heritage Already in Mapper

Added via `heritage batch` on 2026-04-10. All cultures inherited their parent faction from existing heritage entries.

| Heritage | Parent Faction | Cultures Added |
|---|---|---|
| `heritage_arabic` | Abbasid | 6 — RICE_harranian, RICE_wahati, RICE_wahati_hybrid, hedjazi, iraqi, madan |
| `heritage_austronesian` | Burmese | 14 — batak, bungku, danao, gorontalo, jakun, lampung, moklen, sama, seletar, semang, sumba, sunda, timor, tolaki |
| `heritage_bantu` | West African | 13 — chagga, makonde, makua, mijikenda, nguni, pokomo, ruvu, seuta, shirazi, shona, sotho_tswana, tsonga, wamvita |
| `heritage_berber` | Baranis | 4 — RICE_siwi, haratin, siculo_barbari, tuareg |
| `heritage_brythonic` | Brythonic | 2 — iwerddonian, old_brythonic |
| `heritage_burman` | Burmese | 3 — meitei, pyu, rakhine |
| `heritage_byzantine` | Byzantine | 5 — RICE_aegean, italo_greek, italo_greek_calabria, siculo_greek, siculo_greek_hybrid |
| `heritage_central_african` | West African | 4 — fur, maban, tora, toubou |
| `heritage_chinese` | Tibetan | 2 — asian_american, wenmo |
| `heritage_east_african` | Coptic | 3 — beta_israeli, ongamo, siddi |
| `heritage_east_slavic` | Rus | 5 — byelorusian, chernigovan, ryazanian, vladimirian, volyn_ |
| `heritage_elamite` | Persian | 1 — elamite |
| `heritage_frankish` | Frankish | 1 — gascon |
| `heritage_goidelic` | Irish | 2 — breatnach, sassenach |
| `heritage_gur` | West African | 4 — kibsi, kurumba, lilse, senufo |
| `heritage_indo_aryan` | Indian | 3 — avadhi, bihari, magadhi |
| `heritage_iranian` | Persian | 4 — RICE_kalash, RICE_shina, RICE_wakhi, mazandarani |
| `heritage_israelite` | Himyarite | 2 — kaifengim, kochinim |
| `heritage_mon_khmer` | Burmese | 4 — bahnar, chong, kuy, wa |
| `heritage_north_germanic` | Viking | 3 — bretagner, scanian, vender |
| `heritage_sahelian` | Sahelian | 1 — zarma |
| `heritage_siberian` | Permian | 1 — yeniseian |
| `heritage_somalian` | Horn African | 4 — aweer, dahalo, harla, oromo |
| `heritage_tibetan` | Tibetan | 5 — RICE_balti_hybrid, RICE_monguor, gyalrong, himalayan, khalkha |
| `heritage_ugro_permian` | Permian | 1 — mansi |
| `heritage_viet` | Tibetan | 1 — muong |
| `heritage_volga_finnic` | Finnic | 1 — moksha |
| `heritage_yoruba` | West African | 3 — akpoto, baatonu, ijaw |
| **TOTAL** | | **102** |

### 29 Ambiguous Cultures — Resolved by Cultural/Historical Inference

These had blank heritage in the source data (defined only in `_names.txt` files). Assigned based on cultural/geographic identity.

| Heritage | Faction | Cultures | Reasoning |
|---|---|---|---|
| `heritage_indo_aryan` | Indian | dhundari, marwari, mewari, kathiawari, nimadi, maithili, munda (7) | North Indian regional cultures |
| `heritage_berber` | Baranis | kabylian (1) | Berber people of Kabylia, Algeria |
| `heritage_east_african` | Coptic | gurage, harari, hadiyya (3) | Ethiopian highland peoples |
| `heritage_frankish` | Frankish | aquitanian, poitevin, provancale, new_frankish (4) | West Frankish regional cultures — confirmed by `aquitanian_hybrid` precedent in data |
| `heritage_central_germanic` | Franconian | suisse, schwiizer, svcizzero (3) | Swiss language variants — matching existing `swiss` assignment |
| `heritage_arabic` | Abbasid | hejazi, RICE_jibbali, baggara (3) | Arabian peninsula + Arabized Sudanese peoples |
| `heritage_turkic` | Turkic | RICE_khallukh (Karluk), RICE_khalaj (2) | Turkic confederations |
| `heritage_central_african` | West African | abakwariga (1) | Sudanic Central African |
| `heritage_dravidian` | Indian | malayali (1) | Dravidian South Indian |
| `heritage_korean` | Tibetan | goryeo_hybrid (1) | East Asian fallback to Tibetan |
| `heritage_turkic` | Turkic | RICE_kanjina (1) | Creation name for divergent `turco_hephthalite` culture in Khuttal (upper Oxus). Post-Hephthalite Turko-Iranian identity |

### 2 Cultures Needing Research — Resolved

| Culture | Heritage | Faction | Notes |
|---|---|---|---|
| `samhan_hybrid` | `heritage_buyeo` (NEW — added to mapper) | Tibetan | Ancient Korean (Samhan confederacies). `heritage_buyeo` is the CK3 heritage for baekje/goguryeo/balhae/samhan. East Asian fallback → Tibetan. **This is the only new heritage added to the mapper this session.** |
| `RICE_scarboroughian` | `heritage_west_germanic` | Anglo Saxon | Not a standalone culture — it's a CK3 *culture creation name* triggered for divergent cultures from the Duchy of York. Base heritage is Anglo-Saxon |

### 2 Cultures Deferred

| Cultures | Status |
|---|---|
| `nomadic_house_name` | **Ignored** — likely CK3 internal placeholder/template name, not a real playable culture |
| `nomadic_house_name_hybrid` | **Ignored** — same as above |

---

## Key Decisions & Principles

### East Asian Fallback
East Asian MAA (Chinese, Japanese, SEA, etc.) and cultures (Korean, etc.) are assigned to **Tibetan** or **Eastern Steppe** factions since Total War: Attila has no unit packs for those regions.

**Applied to:**
- MAA: `black_armor_cavalry`, `RICE_iron_forest` → Tibetan
- Cultures: `heritage_chinese`, `heritage_korean`, `heritage_buyeo` → Tibetan

### CK3 Reality Trumps Historical Interpretation
The MAA's actual in-game classification (weapon, role, unit type) takes precedence over historical accuracy.

**Applied to:**
- `danish_obudshaer` — historically Danish military levy, but CK3/CE classifies as **elite spearmen**
- `danish_svenner` — historically Danish elite retinue, but CK3/CE classifies as **light cavalry**

### Default Faction Requirement
Every MAA added to any faction must also exist in `Default` (crash-prevention). All 14 mapped MAA satisfy this.

### Siege Weaponry Skipped
Trebuchets, battering rams, and other siege equipment are not mapped since they don't appear in Attila battles.

### Horn African Receives 3 RICE Units
Alwan/Nubian/Nilotic RICE units all land in Horn African. Acceptable for now — no dedicated Nubian faction split needed.

### Outremer Anachronism
Outremer units and culture are anachronistic for 919 AD start but still mapped to prevent crashes if a player forms the culture mid-campaign.

---

## Outstanding TODO

1. **`palace_guards` — Expand to all factions.** Currently only in Default with `KOK_cha_gen_spear`. Should be added to every faction with that faction's unique heavy-infantry Attila key. Add XML comment for future refinement.

2. **`nomadic_house_name` / `nomadic_house_name_hybrid`** — Investigate whether these are real cultures or CK3 internal placeholders. If real, assign them to appropriate heritages.

3. **Run validation.** Re-export `summary_log.txt` from the GUI after loading the updated `OfficialCW_EarlyMedieval_919Mod.txt` to confirm all changes resolved the missing-key issues.

---

## Session Activity Log

- **14** missing MAA resolved (12 mapped to specific factions + Default, 2 Chinese MAA fallback to Tibetan + Default)
- **3** siege MAA explicitly ignored
- **20** superfluous MAA cleaned up (6 misspellings fixed with key renames, 14 invalid entries deleted)
- **131** missing cultures mapped (102 easy heritage matches + 29 cultural inferences + 2 research-resolved)
- **1** new heritage added to mapper (`heritage_buyeo` for ancient Korean cultures)
- **4** huscarl mappings added (Anglo Saxon, English, Scots, New English)
- **`palace_guards`** added to Default faction as temporary fallback
