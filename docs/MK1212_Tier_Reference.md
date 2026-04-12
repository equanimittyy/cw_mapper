# MK1212 AD — Unit Tier Reference

## Tier System

The MK1212 (Medieval Kingdoms 1212 AD) Attila mod uses a tiered unit system where each tier corresponds to a historical period:

| Tier | Period | Visual Style |
|---|---|---|
| **T1** | Early Medieval (~900–1100) | Mail, round shields, simpler helms |
| **T2** | High Medieval (~1100–1300) | Surcoats, heater shields, great helms |
| **T3** | Late Medieval / Renaissance (~1300–1500) | Plate armor, pavises, pollaxes |

## Mapper Tier Distribution (from actual data)

| Mapper | T1 | T2 | T3 | Other | Total |
|---|---|---|---|---|---|
| **HighMedieval_MK1212Mod** | 3386 (89%) | 340 (9%) | 44 (1%) | 43 (1%) | 3813 |
| **LateMedieval_MK1212Mod** | 417 (11%) | 3255 (85%) | 110 (3%) | 33 (1%) | 3815 |
| **Rennaisance_MK1212Mod** | 359 (9%) | 282 (7%) | 3136 (82%) | 54 (1%) | 3831 |

### Key Takeaways

- Each mapper has **one dominant tier** (~85–89% of all units)
- **High Medieval → T1** (with some T2 for variety)
- **Late Medieval → T2** (with some T1 for variety)
- **Renaissance → T3** (with some T1/T2 for variety)
- T1 units can look too early visually for later mappers — lean toward the dominant tier
- Small T4 presence in Late Medieval and Renaissance (4–14 units) — likely special/unique units

## Tier Selection Guidelines

When assigning new Attila unit keys to MK1212 mappers:

1. **Default to the mapper's dominant tier** (T1 for High, T2 for Late, T3 for Renaissance)
2. **One tier up is acceptable** for elite/special units (e.g. T2 in High Medieval for an elite unit)
3. **Avoid going two tiers up** (e.g. T3 in High Medieval) — will look visually anachronistic
4. **One tier down is acceptable** for levy/light units in later mappers (e.g. T1 in Late Medieval)

## Unit Key Naming Convention

MK1212 unit keys follow the pattern:

```
mk_[faction]_t[tier]_[unit_name]
```

Examples:
- `mk_dan_t1_huskarls` — Danish T1 Huskarls
- `mk_hre_t2_ritter` — HRE T2 Knights (Ritter)
- `mk_fre_t3_chevaliers` — French T3 Chevaliers

### Common Faction Prefixes

| Prefix | Faction |
|---|---|
| `mk_dan_` | Danish |
| `mk_eng_` | English |
| `mk_fre_` | French |
| `mk_hre_` | Holy Roman Empire (German) |
| `mk_nor_` | Norse/Norwegian |
| `mk_swd_` | Swedish |
| `mk_cas_` | Castilian |
| `mk_ara_` | Aragonese |
| `mk_byz_` | Byzantine |
| `mk_nic_` | Nicene (Byzantine successor) |
| `mk_tre_` | Trebizond |
| `mk_epi_` | Epirus |
| `mk_arm_` | Armenian |
| `mk_georg_` | Georgian |
| `mk_sal_` | Saljuq/Seljuk |
| `mk_ayy_` | Ayyubid |
| `mk_khw_` | Khwarazmian |
| `mk_ghu_` | Ghurid |
| `mk_gold_` | Golden Horde |
| `mk_mon_` | Mongol (base/Yuan) |
| `mk_ilkhan_` | Ilkhanate |
| `mk_cuman_` | Cuman |
| `mk_volga_` | Volga Bulgaria |
| `mk_mak_` | Makuria (Nubian) |
| `mk_zag_` | Zagwe (Ethiopian) |
| `mk_jer_` | Jerusalem (Crusader) |
| `mk_ant_` | Antioch (Crusader) |
| `mk_lat_` | Latin Empire |
| `mk_teu_` | Teutonic Order |
| `mk_mio_` | Military Orders (generic) |
| `mk_lit_` | Lithuanian |
| `mk_rus_` | Russian |
| `mk_merc_` | Mercenary |
| `earl_` | Earl submod (realistic overhauls) |

### Realistic Overhaul Keys

Some unit keys use the `earl_` prefix — these come from the **Realistic Infantry/Cavalry/Missile Overhaul** submods rather than MK1212 base. They follow the same tier system.
