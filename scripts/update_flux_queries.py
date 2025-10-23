#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / 'grafana' / 'provisioning' / 'dashboards' / 'Full Metrics.json'

MEAS_MAP = {
    'pac2200': 'meter_inst',
    'pac2200_avg1': 'meter_avg1',
    'pac2200_avg2': 'meter_avg2',
}

# base field replacements (no stage)
BASE_FIELD_MAP = {
    'PF_L1': 'power_factor_phase_1',
    'PF_L2': 'power_factor_phase_2',
    'PF_L3': 'power_factor_phase_3',
    'PF_SUM': 'power_factor_total',
    'VA_SUM': 'apparent_power_total',
    'VA_L1': 'apparent_power_phase_1',
    'VA_L2': 'apparent_power_phase_2',
    'VA_L3': 'apparent_power_phase_3',
    'V_L1': 'voltage_phase_1',
    'V_L2': 'voltage_phase_2',
    'V_L3': 'voltage_phase_3',
    'V_L12': 'voltage_line_12',
    'V_L23': 'voltage_line_23',
    'V_L31': 'voltage_line_31',
    'P_SUM': 'active_power_total',
    'P_L1': 'active_power_phase_1',
    'P_L2': 'active_power_phase_2',
    'P_L3': 'active_power_phase_3',
    'I_L1': 'current_phase_1',
    'I_L2': 'current_phase_2',
    'I_L3': 'current_phase_3',
    'VARQ1_SUM': 'reactive_power_q1_total',
    'VARQ1_L1': 'reactive_power_q1_phase_1',
    'VARQ1_L2': 'reactive_power_q1_phase_2',
    'VARQ1_L3': 'reactive_power_q1_phase_3',
    'FREQ': 'frequency',
}


def replace_measurement(q: str) -> str:
    # replace measurement comparisons
    def repl(m):
        old = m.group(1)
        return f'r._measurement == "{MEAS_MAP.get(old, old)}"'

    q = re.sub(r'r\._measurement == "([^"]+)"', repl, q)
    return q


def replace_fields(q: str) -> str:
    # determine stage from measurement
    stage = None
    if 'meter_avg1' in q:
        stage = 'stage1'
    elif 'meter_avg2' in q:
        stage = 'stage2'

    # replace occurrences inside contains(...) set lists and equality checks
    # first replace tokens inside quoted identifiers
    def map_token(tok: str) -> str:
        if stage == 'stage1':
            # try stage1 variants
            if tok.endswith('_SUM'):
                return BASE_FIELD_MAP.get(tok, tok) + '_stage1' if tok in BASE_FIELD_MAP else tok
            if tok in BASE_FIELD_MAP:
                return BASE_FIELD_MAP[tok] + '_stage1'
        if stage == 'stage2':
            if tok.endswith('_SUM'):
                return BASE_FIELD_MAP.get(tok, tok) + '_stage2' if tok in BASE_FIELD_MAP else tok
            if tok in BASE_FIELD_MAP:
                return BASE_FIELD_MAP[tok] + '_stage2'
        # no stage
        return BASE_FIELD_MAP.get(tok, tok)

    # replace inside contains set arrays: find all quoted tokens and map them
    def replace_in_set(match):
        inner = match.group(1)
        # split by comma, strip quotes/spaces
        parts = re.findall(r'"([^"]+)"', inner)
        mapped = [map_token(p) for p in parts]
        new = ', '.join(f'"{m}"' for m in mapped)
        return f'contains(value: r._field, set: [{new}])'

    q = re.sub(r'contains\(value: r\._field, set: \[([^\]]+)\]\)', replace_in_set, q)

    # replace equality checks r._field == "FOO"
    def replace_eq(m):
        tok = m.group(1)
        return f'r._field == "{map_token(tok)}"'

    q = re.sub(r'r\._field == "([^"]+)"', replace_eq, q)

    return q


def main():
    data = json.loads(DB_PATH.read_text())
    changed = 0
    for panel in data.get('panels', []):
        for target in panel.get('targets', []):
            q = target.get('query')
            if not q or 'from(bucket:' not in q:
                continue
            newq = q
            newq = replace_measurement(newq)
            newq = replace_fields(newq)
            if newq != q:
                target['query'] = newq
                changed += 1

    if changed:
        DB_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    print(f'Updated {changed} query strings in {DB_PATH}')


if __name__ == '__main__':
    main()
