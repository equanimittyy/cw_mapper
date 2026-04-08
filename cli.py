'''Copyright (c) 2025 equanimittyy. All Rights Reserved.

CLI interface for CW Mapper — designed for collaborative use with Claude Code.
'''

import argparse
import json
import os
import sys

from constants import (
    CUSTOM_MAPPER_DIR, RANK_MAP, ATTILA_EXPORT_DIR,
    CLI_CULTURES_PATH, CLI_MAA_PATH, CLI_TITLE_PATH,
)
from utils import (
    save_mapper, load_mapper, export_xml, import_xml,
    add_map_config, resolve_import_mods, filter_source_list, filter_culture_list,
    init_map_config, build_mapping_entry,
)
from source_data import load_source_data, run_validation, export_cli_source_data

# ============================================================
# Helpers
# ============================================================

def _error(msg):
    print(f'Error: {msg}', file=sys.stderr)
    sys.exit(1)

def _warn(msg):
    print(f'Warning: {msg}', file=sys.stderr)

def _output(data):
    json.dump(data, sys.stdout, indent=2, ensure_ascii=False)
    print()

def _ensure_source_data():
    # Attila keys come from TSVs already in the repo
    if not os.path.exists(ATTILA_EXPORT_DIR) or not any(f.endswith('.tsv') for f in os.listdir(ATTILA_EXPORT_DIR)):
        _error(f'No Attila TSV exports found in {ATTILA_EXPORT_DIR}')
    # CK3 keys come from cli_data/ (exported via GUI or "python cli.py source export")
    missing_ck3 = [p for p in [CLI_CULTURES_PATH, CLI_MAA_PATH, CLI_TITLE_PATH]
                   if not os.path.exists(p)]
    if missing_ck3:
        _error(f'Missing CK3 source data: {", ".join(missing_ck3)}.\n'
               f'Export from GUI ("Export Source Data for CLI") or run: python cli.py source export')
    return load_source_data()

def _validate_name(name, label='Mapper'):
    if not name or not name.strip():
        _error(f'{label} name cannot be empty')
    if os.sep in name or '/' in name or '\\' in name:
        _error(f'{label} name cannot contain path separators')

def _mapper_path(name):
    return os.path.join(CUSTOM_MAPPER_DIR, f'{name}.txt')

def _load_mapper(name):
    path = _mapper_path(name)
    if not os.path.exists(path):
        _error(f"Mapper '{name}' not found at {path}")
    src = _ensure_source_data()
    result = load_mapper(path, src.maa_keys, src.attila_keys, src.cultures_keys, src.title_keys)
    faction_mapping, heritage_mapping, mods, has_diff, missing_keys, title_mapping, title_names, diff_message = result
    if diff_message:
        _warn(diff_message.strip())
    return faction_mapping, heritage_mapping, mods, title_mapping, title_names

def _save_mapper(name, faction_mapping, heritage_mapping, mods, title_mapping, title_names):
    save_mapper(name, faction_mapping, heritage_mapping, mods, title_mapping, title_names)
    add_map_config(name, mods)

def _get_factions(faction_mapping):
    return sorted(set(k[1] for k in faction_mapping.keys()))

def _add_mapping(faction_mapping, maa, faction, attila, size):
    faction_mapping[(maa, faction)] = build_mapping_entry(maa, attila, size)
    return faction_mapping

def _copy_faction_entries(fm, source_faction, destinations):
    """Copy all mappings from source_faction to each destination. Returns count of entries copied."""
    source_entries = {k: v for k, v in fm.items() if k[1] == source_faction}
    count = 0
    for dest in destinations:
        for (maa, _), value in source_entries.items():
            fm[(maa, dest)] = list(value)
            count += 1
    return count

def _set_levy_percentage(fm, levy_key, faction, percentage):
    """Set levy percentage for a specific levy mapping. Returns the updated value."""
    key = (levy_key, faction)
    if key not in fm:
        return None
    value = fm[key]
    if len(value) > 2:
        value[2] = percentage
    else:
        value.append(percentage)
    fm[key] = value
    return value

def _read_json_input(args):
    if hasattr(args, 'input') and args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        data = sys.stdin.read().strip()
        if not data:
            _error('No JSON input provided. Pipe JSON via stdin or use --input FILE.')
        return json.loads(data)

# ============================================================
# Command: validate
# ============================================================

def cmd_validate(args):
    run_validation(on_step=lambda msg: print(msg, file=sys.stderr))
    _output({'status': 'ok', 'message': 'Validation complete. Source CSV reports generated.'})

def cmd_source_export(args):
    export_cli_source_data(on_step=lambda msg: print(msg, file=sys.stderr))
    _output({'status': 'ok', 'message': 'CK3 source data exported to cli_data/. Attila keys read from attila_exports/ TSVs.'})

# ============================================================
# Command: source
# ============================================================

def cmd_source_maa(args):
    src = _ensure_source_data()
    result = filter_source_list(src.maa_keys, 'ck3_maa', 'ck3_source', args.source or 'ALL', args.search or '')
    _output(result)

def cmd_source_attila(args):
    src = _ensure_source_data()
    result = filter_source_list(src.attila_keys, 'attila_map_key', 'attila_source', args.source or 'ALL', args.search or '')
    _output(result)

def cmd_source_cultures(args):
    src = _ensure_source_data()
    result = filter_culture_list(src.cultures_keys, args.source or 'ALL', args.search or '')
    _output(result)

def cmd_source_titles(args):
    src = _ensure_source_data()
    filtered = list(src.title_keys)
    if args.source and args.source != 'ALL':
        filtered = [item for item in filtered if item['ck3_source'] == args.source]
    if args.rank:
        rank_name = RANK_MAP.get(args.rank, args.rank)
        filtered = [item for item in filtered if item['title_rank'] == rank_name]
    if args.search:
        search_lower = args.search.lower()
        filtered = [item for item in filtered if search_lower in item['title_key'].lower()]
    filtered.sort(key=lambda x: x['title_key'])
    _output(filtered)

def cmd_source_list_sources(args):
    src = _ensure_source_data()
    _output({
        'ck3_sources': sorted(set(src.ck3_sources)),
        'attila_sources': sorted(set(src.attila_sources)),
        'title_sources': sorted(set(src.title_sources)),
    })

# ============================================================
# Command: mapper
# ============================================================

def cmd_mapper_list(args):
    os.makedirs(CUSTOM_MAPPER_DIR, exist_ok=True)
    mappers = [os.path.splitext(f)[0] for f in sorted(os.listdir(CUSTOM_MAPPER_DIR)) if f.endswith('.txt')]
    _output(mappers)

def cmd_mapper_create(args):
    _validate_name(args.name)
    path = _mapper_path(args.name)
    if os.path.exists(path):
        _error(f"Mapper '{args.name}' already exists")
    save_mapper(args.name, {}, {}, {'CK3': [], 'Attila': []})
    init_map_config()
    add_map_config(args.name, {'CK3': [], 'Attila': []})
    _output({'status': 'ok', 'message': f"Mapper '{args.name}' created"})

def cmd_mapper_show(args):
    fm, hm, mods, tm, tn = _load_mapper(args.name)
    section = args.section or 'all'

    result = {}

    if section in ('all', 'factions'):
        result['factions'] = _get_factions(fm)

    if section in ('all', 'mappings'):
        mappings = {}
        for (maa, faction), value in sorted(fm.items(), key=lambda x: (x[0][1], x[0][0])):
            if args.faction and faction != args.faction:
                continue
            if faction not in mappings:
                mappings[faction] = []
            entry = {'maa': maa, 'attila': value[0], 'size': value[1]}
            if len(value) > 2:
                entry['percentage'] = value[2]
            mappings[faction].append(entry)
        result['mappings'] = mappings

    if section in ('all', 'heritage'):
        heritages = {}
        for (heritage, culture), faction in sorted(hm.items()):
            if heritage not in heritages:
                heritages[heritage] = {}
            heritages[heritage][culture] = faction
        result['heritage'] = heritages

    if section in ('all', 'titles'):
        titles = {}
        for (maa, title_key), value in sorted(tm.items(), key=lambda x: (x[0][1], x[0][0])):
            if title_key not in titles:
                titles[title_key] = {'name': tn.get(title_key, title_key), 'mappings': []}
            entry = {'maa': maa, 'attila': value[0], 'size': value[1]}
            titles[title_key]['mappings'].append(entry)
        result['titles'] = titles

    if section in ('all', 'mods'):
        result['mods'] = mods

    _output(result)

def cmd_mapper_delete(args):
    path = _mapper_path(args.name)
    if not os.path.exists(path):
        _error(f"Mapper '{args.name}' not found")
    os.remove(path)
    _output({'status': 'ok', 'message': f"Mapper '{args.name}' deleted"})

def cmd_mapper_copy(args):
    fm, hm, mods, tm, tn = _load_mapper(args.source)
    dest_path = _mapper_path(args.dest)
    if os.path.exists(dest_path):
        _error(f"Mapper '{args.dest}' already exists")
    _save_mapper(args.dest, fm, hm, mods, tm, tn)
    _output({'status': 'ok', 'message': f"Mapper '{args.source}' copied to '{args.dest}'"})

# ============================================================
# Command: mapping
# ============================================================

def cmd_mapping_add(args):
    fm, hm, mods, tm, tn = _load_mapper(args.mapper)
    _add_mapping(fm, args.maa, args.faction, args.attila, args.size)
    _save_mapper(args.mapper, fm, hm, mods, tm, tn)
    _output({'status': 'ok', 'added': {'maa': args.maa, 'faction': args.faction, 'attila': args.attila}})

def cmd_mapping_remove(args):
    fm, hm, mods, tm, tn = _load_mapper(args.mapper)
    key = (args.maa, args.faction)
    if key not in fm:
        _error(f"Mapping ({args.maa}, {args.faction}) not found")
    del fm[key]
    _save_mapper(args.mapper, fm, hm, mods, tm, tn)
    _output({'status': 'ok', 'removed': {'maa': args.maa, 'faction': args.faction}})

def cmd_mapping_copy_faction(args):
    fm, hm, mods, tm, tn = _load_mapper(args.mapper)
    if not any(k[1] == args.source_faction for k in fm):
        _error(f"No mappings found for faction '{args.source_faction}'")
    destinations = [d.strip() for d in args.dest_factions.split(',') if d.strip()]
    if not destinations:
        _error('No valid destination factions provided')
    count = _copy_faction_entries(fm, args.source_faction, destinations)
    _save_mapper(args.mapper, fm, hm, mods, tm, tn)
    _output({'status': 'ok', 'copied': count, 'from': args.source_faction, 'to': destinations})

def cmd_mapping_set_levy(args):
    if not 0 <= args.percentage <= 100:
        _error(f'Percentage must be between 0 and 100, got {args.percentage}')
    fm, hm, mods, tm, tn = _load_mapper(args.mapper)
    result = _set_levy_percentage(fm, args.levy_key, args.faction, args.percentage)
    if result is None:
        _error(f"Levy mapping ({args.levy_key}, {args.faction}) not found")
    _save_mapper(args.mapper, fm, hm, mods, tm, tn)

    # Check total
    total = sum(
        v[2] for (m, f), v in fm.items()
        if f == args.faction and m.startswith('LEVY-') and len(v) > 2
    )
    result = {'status': 'ok', 'set': {'levy': args.levy_key, 'faction': args.faction, 'percentage': args.percentage}}
    if total != 100:
        result['warning'] = f'Levy percentages for {args.faction} sum to {total}%, not 100%'
        _warn(result['warning'])
    _output(result)

def cmd_mapping_batch(args):
    fm, hm, mods, tm, tn = _load_mapper(args.mapper)
    ops = _read_json_input(args)
    results = []

    for i, op in enumerate(ops):
        op_type = op.get('op')
        try:
            if op_type == 'add':
                _add_mapping(fm, op['maa'], op['faction'], op['attila'], op.get('size'))
                results.append({'op': 'add', 'maa': op['maa'], 'faction': op['faction'], 'status': 'ok'})
            elif op_type == 'remove':
                key = (op['maa'], op['faction'])
                if key in fm:
                    del fm[key]
                    results.append({'op': 'remove', 'maa': op['maa'], 'faction': op['faction'], 'status': 'ok'})
                else:
                    results.append({'op': 'remove', 'maa': op['maa'], 'faction': op['faction'], 'status': 'not_found'})
            elif op_type == 'copy_faction':
                destinations = [d.strip() for d in op['to'].split(',') if d.strip()] if isinstance(op['to'], str) else op['to']
                count = _copy_faction_entries(fm, op['from'], destinations)
                results.append({'op': 'copy_faction', 'from': op['from'], 'to': destinations, 'copied': count, 'status': 'ok'})
            elif op_type == 'set_levy':
                result = _set_levy_percentage(fm, op['levy'], op['faction'], op['percentage'])
                if result is not None:
                    results.append({'op': 'set_levy', 'levy': op['levy'], 'faction': op['faction'], 'status': 'ok'})
                else:
                    results.append({'op': 'set_levy', 'levy': op['levy'], 'faction': op['faction'], 'status': 'not_found'})
            else:
                results.append({'op': op_type, 'index': i, 'status': 'unknown_op'})
        except KeyError as e:
            results.append({'op': op_type, 'index': i, 'status': 'error', 'message': f'Missing key: {e}'})

    _save_mapper(args.mapper, fm, hm, mods, tm, tn)

    # Check levy totals per faction
    warnings = []
    levy_factions = set(k[1] for k in fm.keys() if k[0].startswith('LEVY-'))
    for faction in levy_factions:
        total = sum(v[2] for (m, f), v in fm.items() if f == faction and m.startswith('LEVY-') and len(v) > 2)
        if total != 100:
            warnings.append(f'Levy percentages for {faction} sum to {total}%, not 100%')
            _warn(warnings[-1])

    _output({'status': 'ok', 'operations': len(ops), 'results': results, 'warnings': warnings})

# ============================================================
# Command: heritage
# ============================================================

def cmd_heritage_add(args):
    fm, hm, mods, tm, tn = _load_mapper(args.mapper)
    # Auto-create PARENT_KEY if heritage is new
    parent_key = (args.heritage, 'PARENT_KEY')
    if parent_key not in hm:
        hm[parent_key] = ''
    hm[(args.heritage, args.culture)] = args.faction
    _save_mapper(args.mapper, fm, hm, mods, tm, tn)
    _output({'status': 'ok', 'added': {'heritage': args.heritage, 'culture': args.culture, 'faction': args.faction}})

def cmd_heritage_add_parent(args):
    fm, hm, mods, tm, tn = _load_mapper(args.mapper)
    hm[(args.heritage, 'PARENT_KEY')] = args.faction
    _save_mapper(args.mapper, fm, hm, mods, tm, tn)
    _output({'status': 'ok', 'added': {'heritage': args.heritage, 'PARENT_KEY': args.faction}})

def cmd_heritage_remove(args):
    fm, hm, mods, tm, tn = _load_mapper(args.mapper)
    if args.culture:
        key = (args.heritage, args.culture)
        if key not in hm:
            _error(f"Heritage mapping ({args.heritage}, {args.culture}) not found")
        del hm[key]
    else:
        # Remove all entries for this heritage
        keys_to_remove = [k for k in hm if k[0] == args.heritage]
        if not keys_to_remove:
            _error(f"No heritage mappings found for '{args.heritage}'")
        for k in keys_to_remove:
            del hm[k]
    _save_mapper(args.mapper, fm, hm, mods, tm, tn)
    _output({'status': 'ok', 'removed': {'heritage': args.heritage, 'culture': args.culture or 'ALL'}})

def cmd_heritage_batch(args):
    fm, hm, mods, tm, tn = _load_mapper(args.mapper)
    ops = _read_json_input(args)
    results = []

    for i, op in enumerate(ops):
        op_type = op.get('op')
        try:
            if op_type == 'add':
                parent_key = (op['heritage'], 'PARENT_KEY')
                if parent_key not in hm:
                    hm[parent_key] = ''
                hm[(op['heritage'], op['culture'])] = op['faction']
                results.append({'op': 'add', 'heritage': op['heritage'], 'culture': op['culture'], 'status': 'ok'})
            elif op_type == 'add_parent':
                hm[(op['heritage'], 'PARENT_KEY')] = op['faction']
                results.append({'op': 'add_parent', 'heritage': op['heritage'], 'status': 'ok'})
            elif op_type == 'remove':
                culture = op.get('culture')
                if culture:
                    key = (op['heritage'], culture)
                    if key in hm:
                        del hm[key]
                        results.append({'op': 'remove', 'heritage': op['heritage'], 'culture': culture, 'status': 'ok'})
                    else:
                        results.append({'op': 'remove', 'heritage': op['heritage'], 'culture': culture, 'status': 'not_found'})
                else:
                    keys_to_remove = [k for k in hm if k[0] == op['heritage']]
                    for k in keys_to_remove:
                        del hm[k]
                    results.append({'op': 'remove', 'heritage': op['heritage'], 'removed': len(keys_to_remove), 'status': 'ok'})
            else:
                results.append({'op': op_type, 'index': i, 'status': 'unknown_op'})
        except KeyError as e:
            results.append({'op': op_type, 'index': i, 'status': 'error', 'message': f'Missing key: {e}'})

    _save_mapper(args.mapper, fm, hm, mods, tm, tn)
    _output({'status': 'ok', 'operations': len(ops), 'results': results})

# ============================================================
# Command: title
# ============================================================

def cmd_title_add_key(args):
    fm, hm, mods, tm, tn = _load_mapper(args.mapper)
    tn[args.title_key] = args.display_name
    _save_mapper(args.mapper, fm, hm, mods, tm, tn)
    _output({'status': 'ok', 'added': {'title_key': args.title_key, 'name': args.display_name}})

def cmd_title_remove_key(args):
    fm, hm, mods, tm, tn = _load_mapper(args.mapper)
    if args.title_key not in tn:
        _error(f"Title key '{args.title_key}' not found")
    del tn[args.title_key]
    # Also remove all mappings for this title
    keys_to_remove = [k for k in tm if k[1] == args.title_key]
    for k in keys_to_remove:
        del tm[k]
    _save_mapper(args.mapper, fm, hm, mods, tm, tn)
    _output({'status': 'ok', 'removed': {'title_key': args.title_key, 'mappings_removed': len(keys_to_remove)}})

def cmd_title_add(args):
    try:
        entry = build_mapping_entry(args.maa, args.attila, args.size, is_title=True)
    except ValueError as e:
        _error(str(e))
    fm, hm, mods, tm, tn = _load_mapper(args.mapper)
    tm[(args.maa, args.title_key)] = entry
    _save_mapper(args.mapper, fm, hm, mods, tm, tn)
    _output({'status': 'ok', 'added': {'maa': args.maa, 'title_key': args.title_key, 'attila': args.attila}})

def cmd_title_remove(args):
    fm, hm, mods, tm, tn = _load_mapper(args.mapper)
    key = (args.maa, args.title_key)
    if key not in tm:
        _error(f"Title mapping ({args.maa}, {args.title_key}) not found")
    del tm[key]
    _save_mapper(args.mapper, fm, hm, mods, tm, tn)
    _output({'status': 'ok', 'removed': {'maa': args.maa, 'title_key': args.title_key}})

def cmd_title_batch(args):
    fm, hm, mods, tm, tn = _load_mapper(args.mapper)
    ops = _read_json_input(args)
    results = []

    for i, op in enumerate(ops):
        op_type = op.get('op')
        try:
            if op_type == 'add_key':
                tn[op['title_key']] = op['name']
                results.append({'op': 'add_key', 'title_key': op['title_key'], 'status': 'ok'})
            elif op_type == 'add':
                maa = op['maa']
                try:
                    entry = build_mapping_entry(maa, op['attila'], op.get('size'), is_title=True)
                except ValueError as e:
                    results.append({'op': 'add', 'maa': maa, 'index': i, 'status': 'error', 'message': str(e)})
                    continue
                tm[(maa, op['title_key'])] = entry
                results.append({'op': 'add', 'maa': maa, 'title_key': op['title_key'], 'status': 'ok'})
            elif op_type == 'remove':
                key = (op['maa'], op['title_key'])
                if key in tm:
                    del tm[key]
                    results.append({'op': 'remove', 'maa': op['maa'], 'title_key': op['title_key'], 'status': 'ok'})
                else:
                    results.append({'op': 'remove', 'maa': op['maa'], 'title_key': op['title_key'], 'status': 'not_found'})
            elif op_type == 'remove_key':
                tk = op['title_key']
                if tk in tn:
                    del tn[tk]
                keys_to_remove = [k for k in tm if k[1] == tk]
                for k in keys_to_remove:
                    del tm[k]
                results.append({'op': 'remove_key', 'title_key': tk, 'mappings_removed': len(keys_to_remove), 'status': 'ok'})
            else:
                results.append({'op': op_type, 'index': i, 'status': 'unknown_op'})
        except KeyError as e:
            results.append({'op': op_type, 'index': i, 'status': 'error', 'message': f'Missing key: {e}'})

    _save_mapper(args.mapper, fm, hm, mods, tm, tn)
    _output({'status': 'ok', 'operations': len(ops), 'results': results})

# ============================================================
# Command: mod
# ============================================================

def cmd_mod_show(args):
    fm, hm, mods, tm, tn = _load_mapper(args.mapper)
    _output(mods)

def cmd_mod_add_ck3(args):
    fm, hm, mods, tm, tn = _load_mapper(args.mapper)
    if 'CK3' not in mods:
        mods['CK3'] = []
    entry = f'{args.mod_name}:{args.workshop_id}'
    if entry not in mods['CK3']:
        mods['CK3'].append(entry)
    _save_mapper(args.mapper, fm, hm, mods, tm, tn)
    _output({'status': 'ok', 'added': entry})

def cmd_mod_remove_ck3(args):
    fm, hm, mods, tm, tn = _load_mapper(args.mapper)
    if 'CK3' not in mods:
        _error('No CK3 mods configured')
    matches = [m for m in mods['CK3'] if m.startswith(f'{args.mod_name}:')]
    if not matches:
        _error(f"CK3 mod '{args.mod_name}' not found")
    for m in matches:
        mods['CK3'].remove(m)
    _save_mapper(args.mapper, fm, hm, mods, tm, tn)
    _output({'status': 'ok', 'removed': matches})

def cmd_mod_add_attila(args):
    fm, hm, mods, tm, tn = _load_mapper(args.mapper)
    if 'Attila' not in mods:
        mods['Attila'] = []
    if args.pack_file not in mods['Attila']:
        mods['Attila'].append(args.pack_file)
    _save_mapper(args.mapper, fm, hm, mods, tm, tn)
    _output({'status': 'ok', 'added': args.pack_file})

def cmd_mod_remove_attila(args):
    fm, hm, mods, tm, tn = _load_mapper(args.mapper)
    if 'Attila' not in mods or args.pack_file not in mods['Attila']:
        _error(f"Attila mod '{args.pack_file}' not found")
    mods['Attila'].remove(args.pack_file)
    _save_mapper(args.mapper, fm, hm, mods, tm, tn)
    _output({'status': 'ok', 'removed': args.pack_file})

# ============================================================
# Command: export / import
# ============================================================

def cmd_export(args):
    path = _mapper_path(args.mapper)
    if not os.path.exists(path):
        _error(f"Mapper '{args.mapper}' not found")
    tag = args.tag or ''
    s_date = args.start or '0'
    e_date = args.end or '9999'
    export_dir = export_xml(path, tag, s_date, e_date)
    _output({'status': 'ok', 'export_dir': export_dir})

def cmd_import(args):
    if not os.path.exists(args.folder):
        _error(f"Import folder '{args.folder}' not found")
    mappings, heritage_mappings, imported_mods, title_mappings, title_names = import_xml(args.folder)
    name = args.name or os.path.basename(args.folder.rstrip('/\\'))
    imported_mods, found = resolve_import_mods(name, imported_mods)
    if not found:
        _warn(f"No CK3 mod config found for '{name}' in mod_config.json")
    _save_mapper(name, mappings, heritage_mappings, imported_mods, title_mappings, title_names)
    _output({'status': 'ok', 'mapper': name, 'factions': len(set(k[1] for k in mappings.keys())),
             'heritage_entries': len(heritage_mappings), 'title_entries': len(title_mappings)})

# ============================================================
# Argparse setup
# ============================================================

def build_parser():
    parser = argparse.ArgumentParser(
        prog='cli.py',
        description='CW Mapper CLI — collaborative mapping interface for Claude Code',
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # --- validate ---
    p_validate = subparsers.add_parser('validate', help='Run CW validation pipeline and generate source CSV reports')
    p_validate.set_defaults(func=cmd_validate)

    # --- source ---
    p_source = subparsers.add_parser('source', help='Query available source keys')
    source_sub = p_source.add_subparsers(dest='source_command', required=True)

    p_src_maa = source_sub.add_parser('maa', help='List CK3 Man-at-Arms keys')
    p_src_maa.add_argument('--source', help='Filter by source (e.g. CK3, mod name)')
    p_src_maa.add_argument('--search', help='Search term (case-insensitive)')
    p_src_maa.set_defaults(func=cmd_source_maa)

    p_src_attila = source_sub.add_parser('attila', help='List Attila unit keys')
    p_src_attila.add_argument('--source', help='Filter by source')
    p_src_attila.add_argument('--search', help='Search term (case-insensitive)')
    p_src_attila.set_defaults(func=cmd_source_attila)

    p_src_cultures = source_sub.add_parser('cultures', help='List CK3 cultures with heritage info')
    p_src_cultures.add_argument('--source', help='Filter by source')
    p_src_cultures.add_argument('--search', help='Search term (matches culture or heritage)')
    p_src_cultures.set_defaults(func=cmd_source_cultures)

    p_src_titles = source_sub.add_parser('titles', help='List CK3 title keys')
    p_src_titles.add_argument('--source', help='Filter by source')
    p_src_titles.add_argument('--search', help='Search term (case-insensitive)')
    p_src_titles.add_argument('--rank', choices=['e', 'k', 'd', 'c'], help='Filter by rank (e=Empire, k=Kingdom, d=Duchy, c=County)')
    p_src_titles.set_defaults(func=cmd_source_titles)

    p_src_list = source_sub.add_parser('list-sources', help='List all available source names')
    p_src_list.set_defaults(func=cmd_source_list_sources)

    p_src_export = source_sub.add_parser('export', help='Export source key CSVs from game data (faster than full validate)')
    p_src_export.set_defaults(func=cmd_source_export)

    # --- mapper ---
    p_mapper = subparsers.add_parser('mapper', help='Manage mappers')
    mapper_sub = p_mapper.add_subparsers(dest='mapper_command', required=True)

    p_map_list = mapper_sub.add_parser('list', help='List all saved mappers')
    p_map_list.set_defaults(func=cmd_mapper_list)

    p_map_create = mapper_sub.add_parser('create', help='Create a new empty mapper')
    p_map_create.add_argument('name', help='Mapper name')
    p_map_create.set_defaults(func=cmd_mapper_create)

    p_map_show = mapper_sub.add_parser('show', help='Show mapper contents')
    p_map_show.add_argument('name', help='Mapper name')
    p_map_show.add_argument('--section', choices=['all', 'factions', 'mappings', 'heritage', 'titles', 'mods'], default='all')
    p_map_show.add_argument('--faction', help='Filter mappings to specific faction')
    p_map_show.set_defaults(func=cmd_mapper_show)

    p_map_delete = mapper_sub.add_parser('delete', help='Delete a mapper')
    p_map_delete.add_argument('name', help='Mapper name')
    p_map_delete.set_defaults(func=cmd_mapper_delete)

    p_map_copy = mapper_sub.add_parser('copy', help='Copy a mapper')
    p_map_copy.add_argument('source', help='Source mapper name')
    p_map_copy.add_argument('dest', help='Destination mapper name')
    p_map_copy.set_defaults(func=cmd_mapper_copy)

    # --- mapping ---
    p_mapping = subparsers.add_parser('mapping', help='Manage faction MAA mappings')
    mapping_sub = p_mapping.add_subparsers(dest='mapping_command', required=True)

    p_mmap_add = mapping_sub.add_parser('add', help='Add a single mapping')
    p_mmap_add.add_argument('mapper', help='Mapper name')
    p_mmap_add.add_argument('faction', help='Faction name')
    p_mmap_add.add_argument('maa', help='CK3 MAA key (or GENERAL, KNIGHTS, LEVY-*)')
    p_mmap_add.add_argument('attila', help='Attila unit key')
    p_mmap_add.add_argument('--size', help='Size type: INFANTRY, CAVALRY, RANGED, or a number')
    p_mmap_add.set_defaults(func=cmd_mapping_add)

    p_mmap_rm = mapping_sub.add_parser('remove', help='Remove a mapping')
    p_mmap_rm.add_argument('mapper', help='Mapper name')
    p_mmap_rm.add_argument('faction', help='Faction name')
    p_mmap_rm.add_argument('maa', help='CK3 MAA key')
    p_mmap_rm.set_defaults(func=cmd_mapping_remove)

    p_mmap_copy = mapping_sub.add_parser('copy-faction', help='Copy all mappings from one faction to others')
    p_mmap_copy.add_argument('mapper', help='Mapper name')
    p_mmap_copy.add_argument('source_faction', help='Source faction name')
    p_mmap_copy.add_argument('dest_factions', help='Destination faction(s), comma-separated')
    p_mmap_copy.set_defaults(func=cmd_mapping_copy_faction)

    p_mmap_levy = mapping_sub.add_parser('set-levy', help='Set levy percentage for a faction')
    p_mmap_levy.add_argument('mapper', help='Mapper name')
    p_mmap_levy.add_argument('faction', help='Faction name')
    p_mmap_levy.add_argument('levy_key', help='Levy key (e.g. LEVY-SPEAR)')
    p_mmap_levy.add_argument('percentage', type=int, help='Percentage (0-100)')
    p_mmap_levy.set_defaults(func=cmd_mapping_set_levy)

    p_mmap_batch = mapping_sub.add_parser('batch', help='Batch mapping operations from JSON')
    p_mmap_batch.add_argument('mapper', help='Mapper name')
    p_mmap_batch.add_argument('--input', help='JSON file path (default: stdin)')
    p_mmap_batch.set_defaults(func=cmd_mapping_batch)

    # --- heritage ---
    p_heritage = subparsers.add_parser('heritage', help='Manage heritage-culture-faction assignments')
    heritage_sub = p_heritage.add_subparsers(dest='heritage_command', required=True)

    p_her_add = heritage_sub.add_parser('add', help='Add a heritage-culture-faction mapping')
    p_her_add.add_argument('mapper', help='Mapper name')
    p_her_add.add_argument('heritage', help='Heritage name')
    p_her_add.add_argument('culture', help='Culture name')
    p_her_add.add_argument('faction', help='Faction name')
    p_her_add.set_defaults(func=cmd_heritage_add)

    p_her_parent = heritage_sub.add_parser('add-parent', help='Add/set heritage-level default faction')
    p_her_parent.add_argument('mapper', help='Mapper name')
    p_her_parent.add_argument('heritage', help='Heritage name')
    p_her_parent.add_argument('faction', help='Faction name')
    p_her_parent.set_defaults(func=cmd_heritage_add_parent)

    p_her_rm = heritage_sub.add_parser('remove', help='Remove heritage or culture mapping')
    p_her_rm.add_argument('mapper', help='Mapper name')
    p_her_rm.add_argument('heritage', help='Heritage name')
    p_her_rm.add_argument('culture', nargs='?', help='Culture name (omit to remove entire heritage)')
    p_her_rm.set_defaults(func=cmd_heritage_remove)

    p_her_batch = heritage_sub.add_parser('batch', help='Batch heritage operations from JSON')
    p_her_batch.add_argument('mapper', help='Mapper name')
    p_her_batch.add_argument('--input', help='JSON file path (default: stdin)')
    p_her_batch.set_defaults(func=cmd_heritage_batch)

    # --- title ---
    p_title = subparsers.add_parser('title', help='Manage title mappings')
    title_sub = p_title.add_subparsers(dest='title_command', required=True)

    p_tit_addkey = title_sub.add_parser('add-key', help='Register a title key with display name')
    p_tit_addkey.add_argument('mapper', help='Mapper name')
    p_tit_addkey.add_argument('title_key', help='Title key (e.g. e_byzantium)')
    p_tit_addkey.add_argument('display_name', help='Display name (e.g. Byzantine Empire)')
    p_tit_addkey.set_defaults(func=cmd_title_add_key)

    p_tit_rmkey = title_sub.add_parser('remove-key', help='Remove a title key and all its mappings')
    p_tit_rmkey.add_argument('mapper', help='Mapper name')
    p_tit_rmkey.add_argument('title_key', help='Title key')
    p_tit_rmkey.set_defaults(func=cmd_title_remove_key)

    p_tit_add = title_sub.add_parser('add', help='Add a title mapping')
    p_tit_add.add_argument('mapper', help='Mapper name')
    p_tit_add.add_argument('title_key', help='Title key')
    p_tit_add.add_argument('maa', help='CK3 MAA key (or GENERAL, KNIGHTS — no LEVY)')
    p_tit_add.add_argument('attila', help='Attila unit key')
    p_tit_add.add_argument('--size', help='Size type: INFANTRY, CAVALRY, RANGED, or a number')
    p_tit_add.set_defaults(func=cmd_title_add)

    p_tit_rm = title_sub.add_parser('remove', help='Remove a title mapping')
    p_tit_rm.add_argument('mapper', help='Mapper name')
    p_tit_rm.add_argument('title_key', help='Title key')
    p_tit_rm.add_argument('maa', help='CK3 MAA key')
    p_tit_rm.set_defaults(func=cmd_title_remove)

    p_tit_batch = title_sub.add_parser('batch', help='Batch title operations from JSON')
    p_tit_batch.add_argument('mapper', help='Mapper name')
    p_tit_batch.add_argument('--input', help='JSON file path (default: stdin)')
    p_tit_batch.set_defaults(func=cmd_title_batch)

    # --- mod ---
    p_mod = subparsers.add_parser('mod', help='Manage mod configuration')
    mod_sub = p_mod.add_subparsers(dest='mod_command', required=True)

    p_mod_show = mod_sub.add_parser('show', help='Show mod configuration')
    p_mod_show.add_argument('mapper', help='Mapper name')
    p_mod_show.set_defaults(func=cmd_mod_show)

    p_mod_ck3_add = mod_sub.add_parser('add-ck3', help='Add a CK3 mod')
    p_mod_ck3_add.add_argument('mapper', help='Mapper name')
    p_mod_ck3_add.add_argument('mod_name', help='Mod name')
    p_mod_ck3_add.add_argument('workshop_id', help='Steam Workshop ID (0 for vanilla)')
    p_mod_ck3_add.set_defaults(func=cmd_mod_add_ck3)

    p_mod_ck3_rm = mod_sub.add_parser('remove-ck3', help='Remove a CK3 mod')
    p_mod_ck3_rm.add_argument('mapper', help='Mapper name')
    p_mod_ck3_rm.add_argument('mod_name', help='Mod name')
    p_mod_ck3_rm.set_defaults(func=cmd_mod_remove_ck3)

    p_mod_att_add = mod_sub.add_parser('add-attila', help='Add an Attila mod pack')
    p_mod_att_add.add_argument('mapper', help='Mapper name')
    p_mod_att_add.add_argument('pack_file', help='Pack file name (e.g. my_mod.pack)')
    p_mod_att_add.set_defaults(func=cmd_mod_add_attila)

    p_mod_att_rm = mod_sub.add_parser('remove-attila', help='Remove an Attila mod pack')
    p_mod_att_rm.add_argument('mapper', help='Mapper name')
    p_mod_att_rm.add_argument('pack_file', help='Pack file name')
    p_mod_att_rm.set_defaults(func=cmd_mod_remove_attila)

    # --- export ---
    p_export = subparsers.add_parser('export', help='Export mapper to CW XML format')
    p_export.add_argument('mapper', help='Mapper name')
    p_export.add_argument('--tag', help='Tag identifier (default: mapper name)')
    p_export.add_argument('--start', help='Start date (default: 0)')
    p_export.add_argument('--end', help='End date (default: 9999)')
    p_export.set_defaults(func=cmd_export)

    # --- import ---
    p_import = subparsers.add_parser('import', help='Import mapper from CW XML folder')
    p_import.add_argument('folder', help='Path to XML folder (containing Cultures/, Factions/, etc.)')
    p_import.add_argument('--name', help='Mapper name (default: folder name)')
    p_import.set_defaults(func=cmd_import)

    return parser


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
