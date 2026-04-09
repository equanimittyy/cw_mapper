# CLI Guide — Claude-Assisted Mapper Creation

A command-line interface for building CW mappers collaboratively with Claude Code. The GUI remains fully functional — the CLI is an additional interface optimized for AI-assisted workflows.

## Setup

### Prerequisites

- Attila unit keys are already in the repo at `attila_exports/db/main_units_tables/*.tsv` — the CLI reads these directly
- CK3 data (cultures, MAA, titles) must be exported once before using the CLI

### Exporting CK3 Source Data

Choose one method:

**From GUI (recommended):**
1. Open the GUI (`python main.py`)
2. Click **"Export Source Data for CLI"** on the main window
3. Done — CK3 data is written to `cli_data/`

**From CLI (if game files are accessible):**
```bash
python cli.py source export
```

Re-export whenever your CK3 mods change.

### Data Layout

```
attila_exports/db/main_units_tables/*.tsv   # Attila keys (committed to repo)
cli_data/                                    # CK3 exports (gitignored, you produce this)
  ck3_cultures.csv                           #   cultures + heritages
  ck3_maa.csv                                #   Man-at-Arms types
  ck3_titles.csv                             #   landed titles
custom_mappers/                              # Mapper save files (gitignored)
  *.txt                                      #   JSON format, shared by GUI and CLI
```

## Collaborative Workflow

The intended workflow is conversational — Claude proposes, you review, Claude executes:

1. **You describe intent**: "I need a Norse faction", "Map all Germanic heritages to Western"
2. **Claude queries source data** to find matching keys:
   ```bash
   python cli.py source attila --search norse
   python cli.py source cultures --search germanic
   python cli.py source maa --search cavalry
   ```
3. **Claude proposes mappings** in conversation for you to review:
   > Here's what I'd suggest for the Norse faction:
   > - huscarl -> att_vik_huscarl (INFANTRY)
   > - GENERAL -> att_vik_general
   > - KNIGHTS -> att_vik_knights
   > - LEVY-SPEAR -> att_vik_levy_spear (50%)
   > - LEVY-SWORD -> att_vik_levy_sword (25%)
   > - LEVY-ARCHER -> att_vik_levy_archer (25%)
   >
   > Want me to apply these?
4. **You approve or adjust**: "Swap huscarl for berserker, otherwise looks good"
5. **Claude executes** the approved changes via batch commands
6. **You verify** — Claude shows the mapper state with `mapper show`

### Example Session

```
You:    "Create a new mapper called MyMod and set up a Norse faction"

Claude: *runs* python cli.py mapper create MyMod
Claude: *runs* python cli.py source attila --search norse
Claude: *runs* python cli.py source attila --search vik
Claude: "Based on available Attila units, here's what I'd suggest for Norse: ..."

You:    "Looks good, add them"

Claude: *runs* echo '[{"op":"add","faction":"Norse","maa":"GENERAL",...}, ...]' | python cli.py mapping batch MyMod
Claude: *runs* python cli.py mapper show MyMod --section mappings --faction Norse
Claude: "Done. Here's the Norse faction: [shows state]"

You:    "Now copy Norse to a Western faction but swap the general"

Claude: *runs* python cli.py mapping copy-faction MyMod Norse Western
Claude: *runs* python cli.py mapping add MyMod Western GENERAL att_wes_general
Claude: "Done. Western faction created with Norse units, general swapped."

You:    "Map the Germanic heritages"

Claude: *runs* python cli.py source cultures --search germanic
Claude: "Found these cultures under heritage_north_germanic: norse, anglo_norse, ..."
Claude: *proposes heritage assignments*

You:    "All Norse except anglo_norse goes to Western"

Claude: *runs heritage batch*
Claude: *runs* python cli.py mapper show MyMod --section heritage

You:    "Export it"

Claude: *runs* python cli.py export MyMod --tag MyMod_v1 --start 919 --end 1453
```

## Command Reference

### Source Data Queries

```bash
# List CK3 Man-at-Arms keys
python cli.py source maa [--source SOURCE] [--search TERM]

# List Attila unit keys
python cli.py source attila [--source SOURCE] [--search TERM]

# List CK3 cultures with heritage info (returns full dicts, searches both culture and heritage names)
python cli.py source cultures [--source SOURCE] [--search TERM]

# List CK3 title keys
python cli.py source titles [--source SOURCE] [--search TERM] [--rank e|k|d|c]

# List all available source names (mod names, etc.)
python cli.py source list-sources

# Export CK3 source data to cli_data/ (requires game files)
python cli.py source export

# Run full validation pipeline (generates reports/ and summary_log.txt)
python cli.py validate
```

`--source` filters by source name (e.g. `CK3`, a mod name, or a TSV filename). Use `list-sources` to see available values.

`--search` is case-insensitive substring match.

### Mapper Lifecycle

```bash
python cli.py mapper list                    # List all saved mappers
python cli.py mapper create <name>           # Create empty mapper
python cli.py mapper show <name>             # Show full mapper contents (JSON)
python cli.py mapper show <name> --section factions          # Just faction names
python cli.py mapper show <name> --section mappings          # All faction mappings
python cli.py mapper show <name> --section mappings --faction Norse  # One faction
python cli.py mapper show <name> --section heritage          # Heritage assignments
python cli.py mapper show <name> --section titles            # Title mappings
python cli.py mapper show <name> --section mods              # Mod config
python cli.py mapper copy <source> <dest>    # Duplicate a mapper
python cli.py mapper delete <name>           # Delete a mapper
```

### Faction MAA Mappings

```bash
# Add a single mapping
python cli.py mapping add <mapper> <faction> <maa> <attila> [--size SIZE]

# Remove a mapping
python cli.py mapping remove <mapper> <faction> <maa>

# Copy all mappings from one faction to others (comma-separated destinations)
python cli.py mapping copy-faction <mapper> <source-faction> <dest-factions>

# Set levy percentage (0-100)
python cli.py mapping set-levy <mapper> <faction> <levy-key> <percentage>

# Batch operations from JSON (stdin or file)
python cli.py mapping batch <mapper> [--input FILE]
```

### Heritage/Culture Assignments

```bash
# Add a culture -> faction mapping (auto-creates heritage PARENT_KEY if new)
python cli.py heritage add <mapper> <heritage> <culture> <faction>

# Set heritage-level default faction
python cli.py heritage add-parent <mapper> <heritage> <faction>

# Remove a culture mapping, or entire heritage (omit culture)
python cli.py heritage remove <mapper> <heritage> [culture]

# Batch operations from JSON
python cli.py heritage batch <mapper> [--input FILE]
```

### Title Mappings

Titles support GENERAL, KNIGHTS, and regular MAA only — **no levies**.

```bash
# Register a title key with display name
python cli.py title add-key <mapper> <title-key> <display-name>

# Remove a title and all its mappings
python cli.py title remove-key <mapper> <title-key>

# Add a title mapping
python cli.py title add <mapper> <title-key> <maa> <attila> [--size SIZE]

# Remove a title mapping
python cli.py title remove <mapper> <title-key> <maa>

# Batch operations from JSON
python cli.py title batch <mapper> [--input FILE]
```

### Mod Configuration

```bash
python cli.py mod show <mapper>                              # Show current mods
python cli.py mod add-ck3 <mapper> <mod-name> <workshop-id>  # Add CK3 mod (0 = vanilla)
python cli.py mod remove-ck3 <mapper> <mod-name>             # Remove CK3 mod
python cli.py mod add-attila <mapper> <pack-file>            # Add Attila .pack mod
python cli.py mod remove-attila <mapper> <pack-file>         # Remove Attila mod
```

### Import/Export

```bash
# Export mapper to CW XML format (Factions/, Cultures/, Titles/, Mods.xml, etc.)
python cli.py export <mapper> [--tag TAG] [--start DATE] [--end DATE]

# Import from existing CW XML folder
python cli.py import <folder> [--name NAME]
```

Export produces the full folder structure at `custom_mappers/export/<mapper>/`. Default dates: 0-9999.

## Batch JSON Formats

Batch commands accept a JSON array via stdin or `--input FILE`. All operations in a batch share one load-save cycle (efficient for bulk work).

### mapping batch

```json
[
  {"op": "add", "faction": "Norse", "maa": "huscarl", "attila": "att_vik_huscarl", "size": "INFANTRY"},
  {"op": "add", "faction": "Norse", "maa": "GENERAL", "attila": "att_vik_general"},
  {"op": "add", "faction": "Norse", "maa": "KNIGHTS", "attila": "att_vik_knights"},
  {"op": "add", "faction": "Norse", "maa": "LEVY-SPEAR", "attila": "att_vik_levy_spear"},
  {"op": "add", "faction": "Norse", "maa": "LEVY-SWORD", "attila": "att_vik_levy_sword"},
  {"op": "add", "faction": "Norse", "maa": "LEVY-ARCHER", "attila": "att_vik_levy_archer"},
  {"op": "remove", "faction": "Norse", "maa": "longbowmen"},
  {"op": "copy_faction", "from": "Norse", "to": "Western,Eastern"},
  {"op": "set_levy", "faction": "Norse", "levy": "LEVY-SPEAR", "percentage": 50},
  {"op": "set_levy", "faction": "Norse", "levy": "LEVY-SWORD", "percentage": 25},
  {"op": "set_levy", "faction": "Norse", "levy": "LEVY-ARCHER", "percentage": 25}
]
```

Operations:
- **add** — requires `faction`, `maa`, `attila`. Optional `size` (defaults to INFANTRY for regular MAA; auto-set for GENERAL/KNIGHTS/LEVY)
- **remove** — requires `faction`, `maa`
- **copy_faction** — requires `from`, `to` (string comma-separated or JSON array)
- **set_levy** — requires `faction`, `levy`, `percentage` (0-100)

### heritage batch

```json
[
  {"op": "add_parent", "heritage": "heritage_north_germanic", "faction": "Norse"},
  {"op": "add", "heritage": "heritage_north_germanic", "culture": "norse", "faction": "Norse"},
  {"op": "add", "heritage": "heritage_north_germanic", "culture": "anglo_norse", "faction": "Western"},
  {"op": "remove", "heritage": "heritage_north_germanic", "culture": "anglo_norse"},
  {"op": "remove", "heritage": "heritage_north_germanic"}
]
```

Operations:
- **add** — requires `heritage`, `culture`, `faction`. Auto-creates PARENT_KEY entry if heritage is new
- **add_parent** — requires `heritage`, `faction`. Sets heritage-level default faction
- **remove** — requires `heritage`. Optional `culture` (omit to remove entire heritage)

### title batch

```json
[
  {"op": "add_key", "title_key": "e_byzantium", "name": "Byzantine Empire"},
  {"op": "add", "title_key": "e_byzantium", "maa": "GENERAL", "attila": "BYZ_general"},
  {"op": "add", "title_key": "e_byzantium", "maa": "cataphract", "attila": "BYZ_cataphract", "size": "CAVALRY"},
  {"op": "remove", "title_key": "e_byzantium", "maa": "cataphract"},
  {"op": "remove_key", "title_key": "e_byzantium"}
]
```

Operations:
- **add_key** — requires `title_key`, `name`. Registers a title with display name
- **add** — requires `title_key`, `maa`, `attila`. Optional `size`. Rejects LEVY-* keys
- **remove** — requires `title_key`, `maa`
- **remove_key** — requires `title_key`. Removes the title and all its mappings

## Size Types

For `--size` argument or `"size"` field in batch JSON:

| Value | Description |
|-------|-------------|
| `INFANTRY` | Standard infantry size (default for regular MAA) |
| `CAVALRY` | Cavalry size |
| `RANGED` | Ranged unit size |
| `"1200"` | Manual numeric size |
| *(omit)* | Auto-set for special types: GENERAL/KNIGHTS get their type as size, LEVY-* get "LEVY" with default percentages |

### Default Levy Percentages

When adding LEVY-* mappings, percentages default to:

| Levy Key | Default % |
|----------|-----------|
| LEVY-SPEAR | 50 |
| LEVY-SWORD | 25 |
| LEVY-ARCHER | 25 |
| LEVY-SKIRM | 0 |
| LEVY-CAV | 0 |
| LEVY-CUSTOM1/2/3 | 0 |

Use `set_levy` operations or `mapping set-levy` to adjust. All levy percentages for a faction must sum to 100%.

## Output Format

All commands output JSON to stdout. Warnings and status messages go to stderr.

**Query commands** return the data directly:
```json
["huscarl", "heavy_cavalry", "light_infantry"]
```

**Mutation commands** return a status object:
```json
{
  "status": "ok",
  "added": {"maa": "huscarl", "faction": "Norse", "attila": "att_vik_huscarl"}
}
```

**Batch commands** return per-operation results:
```json
{
  "status": "ok",
  "operations": 5,
  "results": [
    {"op": "add", "maa": "huscarl", "faction": "Norse", "status": "ok"},
    {"op": "remove", "maa": "longbow", "faction": "Norse", "status": "not_found"}
  ],
  "warnings": ["Levy percentages for Norse sum to 75%, not 100%"]
}
```

## Default Faction Requirement

**Every MAA added to any faction MUST also have a corresponding mapping in the `Default` faction.** The Default faction is a crash-prevention fallback. When a culture's assigned faction doesn't have a mapping for a specific MAA (e.g. a Norse culture triggers a Chinese MAA that doesn't exist in the Viking faction), CW falls back to the Default faction's mapping for that MAA. Without a Default entry, this causes a crash.

When using the CLI to add MAA mappings, always ensure the same MAA key is also mapped in the Default faction. For batch operations, include Default entries alongside faction-specific entries.

## Interoperability with GUI

The CLI and GUI share the same save format (`custom_mappers/*.txt`). A mapper created in the CLI can be opened and edited in the GUI, and vice versa. Both use the same `utils.py` functions for save/load/export/import.

The GUI's "Export Source Data for CLI" button and the CLI's `source export` command produce identical output in `cli_data/`.
