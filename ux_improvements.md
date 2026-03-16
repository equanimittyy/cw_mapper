# UX Improvements Backlog

Remaining UX improvements for the Crusader Wars Mapper GUI, organized by priority.
The high-priority items (unsaved changes warning, save feedback, XML import auto-load,
levy validation, wrong popup title) have already been implemented.

---

## Robustness / Edge Case Fixes

### Narrow save exception handler
The `except Exception` on the save button (line ~1652) catches all exceptions including
programming bugs (TypeError, AttributeError). Should be narrowed to `(OSError, json.JSONDecodeError)`
so actual code bugs surface as tracebacks during development instead of generic "save error" popups.

### Shallow copy for change detection is fragile
`dict(current_title_mappings)` (line ~1807) creates a shallow copy — the list values are shared
with the original. Currently safe because `title_window` replaces values with new lists rather
than mutating in-place, but any future in-place mutation would silently defeat the comparison.
Using `copy.deepcopy()` for the "before" snapshot would be more robust. Same pattern applies
to heritage mappings (line ~1815), though that one is safe since values are strings.

### Partial load sets `has_unsaved_changes = False` incorrectly
When `FILE_LOAD_KEY` fires and `loaded_faction_mapping` is empty/falsy (line ~1668), the mapper
name and `has_unsaved_changes` flag still update even though the actual data wasn't replaced.
This leaves the editor in an inconsistent state: old data with a new mapper name and no unsaved
changes flag. Should only reset `has_unsaved_changes` and `MAPPER_NAME` when data is actually loaded.

### Duplicate popup on XML import validation
After XML import, `load_mapper()` is called for missing-key validation (line ~1857). But
`load_mapper` internally shows a `sg.popup()` warning about missing sources (line ~1538).
The import code then also updates the `SUBTEXT` label. This means the user sees two warnings
about the same issue. Consider adding a `silent` parameter to `load_mapper` or extracting the
validation logic into a separate function.

### Non-atomic file writes risk data loss
`save_mapper` opens with `'w'` mode which truncates the existing file before writing. If the
write fails mid-way (disk full, process killed), the original mapper file is destroyed. Consider
writing to a `.tmp` file first then using `os.replace()` for an atomic swap.

### Levy percentage type inconsistency
Line ~179 uses `sum([int(row[2]) for row in data])` (with explicit `int()` cast) but line ~210
uses `sum([row[2] for row in data])` without the cast. Both should be consistent — if a
non-integer value ever slips in from a corrupted mapper file, line 210 would silently break.

### XML button warns about import even for export
The unsaved-changes dialog on `XML_BUTTON` (line ~1822) says "Importing will discard them" but
the popup offers both Import and Export. Exporting doesn't discard anything. Consider rewording
or moving the check to after the user chooses Import vs Export.

### `WIN_CLOSED` + confirmation popup is fragile
In `popup_levy_percentage`, showing `popup_yes_no` after receiving `WIN_CLOSED` then calling
`continue` to re-enter `window.read()` (line ~209) works in FreeSimpleGUI but is a fragile
pattern — the window handle may be partially destroyed. Consider handling `WIN_CLOSED` separately
from the `Exit` button.

### Empty faction list after import shows "DEFAULT"
If an imported mapper has no faction mappings, `FACTION_LIST` is `[]` and `current_faction`
falls back to `'DEFAULT'` (line ~1849). The combo dropdown shows no options but displays
`'DEFAULT'` — a faction that doesn't exist. Edge case but confusing if encountered.

---

## Medium Priority

### Duplicated search/filter logic
The CK3 and Attila search+filter handling is copy-pasted 4 times across the main mapper
(`mapping_window()` lines ~1558-1617) and title mapper (`title_window()` lines ~1102-1152).
If a new filter behaviour is ever added, it must be updated in 4 places. Extracting a shared
helper function would reduce maintenance burden and prevent inconsistency.

### No keyboard shortcuts
Power users creating hundreds of mappings must click "Add Mapping" every time. Adding
keyboard shortcuts (e.g. Enter to add, Delete to remove) would significantly speed up
workflow in the main mapper and title mapper windows.

### Heritage window ">>>"/"<<<" buttons are cryptic
In `heritage_window()` (line ~856), the ">>>" and "<<<" buttons are not self-explanatory.
Renaming them to "Add >>>" and "<<< Remove" (or adding tooltips) would help new users
understand which direction moves items.

### No progress indicator during validation
"Refresh Current Mappers" (`main_window()` line ~1852) blocks the UI while running
`mapping_validation()` + `summary()`. On large mod sets this can hang for several seconds
with no visual feedback. A spinner, progress bar, or status text update would help.

---

## Lower Priority

### No "Save As" option
Currently you can only save to the current mapper name or set a name once. There is no way
to fork a mapper under a new name without manually renaming the file on disk. A "Save As"
button that prompts for a new name would support this workflow.

### Heritage window has no search/filter
The CK3 MAA and Attila unit lists both have search bars and source filters, but the heritage
list (which can be equally long with many cultures) has no search capability. Adding a search
bar to `heritage_window()` would improve usability for large mod sets.

### Faction list editing is text-based
`popup_faction_list()` (line ~283) uses a raw multiline text field for editing factions.
A listbox with Add/Remove/Rename buttons would be less error-prone, avoiding issues with
accidental whitespace, empty lines, or formatting mistakes.

### Missing keys popup reuses wrong element key name
In `popup_missing_keys()` (line ~249), the table uses `key='LEVY_PERCENTAGE_TABLE'` - a
copy-paste leftover from the levy popup. Not functionally broken since the popup has no
event handling, but confusing for maintenance. Should be renamed to something like
`'MISSING_KEYS_TABLE'`.

### Export workflow requires too many sequential popups
The export path in `popup_xml_import_export()` (line ~517) chains 4 popups in a row:
file picker, tag input, start date, and end date. Consolidating these into a single export
configuration dialog with all fields visible at once would be a smoother experience.

### No visual distinction for special unit types in mapping list
GENERAL, KNIGHTS, and LEVY entries in the mappings listbox look identical to regular MAA
entries. Color-coding or grouping special types would improve scannability when reviewing
a faction's mappings.
