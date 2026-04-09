# OfficialCW_EarlyMedieval_919Mod — Working Notes

## Validation Summary (from summary_log.txt)

| Category | Status |
|---|---|
| CK3 Cultures | 133 missing (fall back to DEFAULT) |
| CK3 Men-at-Arms | **17 missing — WILL CAUSE CRASH** (15 actionable after excluding siege) |
| Attila Unit Keys | All valid |
| Title Keys | All valid |

Required CK3 Mods: Vanilla, Africa Plus, Buffed Mongol Invasion, Cultures Expanded, More Traditions v2, Muslim Enhancements, RICE

---

## Missing MAA — Faction Assignments

### Confirmed by user (CK3 in-game origin checked)

| MAA | In-Game Origin | Assigned Faction | Notes |
|---|---|---|---|
| ~~`black_armor_cavalry`~~ | Chinese | Tibetan | DONE — `HEP_kushan_cataphracts` (+ Default) |
| `palace_guards` | Generic | ALL factions | Default to existing heavy infantry per faction; add XML comment for later refinement |
| `chasseur` | Outremer | Outremer | |
| `landsknecht` | Central Germanic (zweihanders) | Teutonic | Zweihander/Doppelsöldner tradition |
| ~~`RICE_iron_forest`~~ | Chinese | Tibetan | DONE — `att_nom_noble_horse_archers` (+ Default) |

### Ignored — Siege Weaponry

Siege units are not mapped. They do not appear in Attila battles and should be skipped.

| MAA | Reason |
|---|---|
| `abbasid_trebuchet` | Siege weapon — ignore |
| `byzantine_trebuchet` | Siege weapon — ignore |

### Confirmed by explicit naming

| MAA | Assigned Faction |
|---|---|
| `bulgarian_testudos` | Bulgarian |
| `danish_obudshaer` | Danelander |
| `danish_svenner` | Danelander |
| `outremer_bowmen` | Outremer |
| `outremer_heavy_cavalry` | Outremer |
| `outremer_turcopoles` | Outremer |

### Guessed (RICE units) — user approved reasoning

| MAA | Assigned Faction | Reasoning |
|---|---|---|
| `RICE_alodian_cavalry` | Horn African | Alodia = Nubian kingdom on the Blue Nile |
| `RICE_drokpa_horsemen` | Tibetan | Drokpa = Tibetan plateau nomadic pastoralists |
| `RICE_nilotic_raiders` | Horn African | Nilotic peoples = Upper Nile / South Sudan corridor |
| `RICE_sudanese_highlanders` | Horn African | Nuba Mountains / Ethiopian-Sudanese borderlands |

---

## Notes

- **palace_guards**: Temporary heavy infantry default per faction. To be refined later with unique Attila keys per faction.
- **Horn African** receives 3 new RICE units — acceptable for now, no Nubian faction split needed.
- **East Asian MAA** (Chinese, Japanese, SEA) fall back to Tibetan or Eastern Steppe since Attila has no unit packs for those regions.
- **Outremer** units are anachronistic for 919 AD start but needed to prevent crashes if a player forms the culture mid-campaign.
- **Siege weaponry** (trebuchets, etc.) is ignored — these don't appear in Attila battles and should not be mapped.

---

## Missing Cultures (133)

Not yet addressed. These fall back to the DEFAULT faction (no crash, but generic units). To be tackled after MAA mapping is complete.
