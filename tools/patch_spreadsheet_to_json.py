#!/usr/bin/env python3

import json
import os
import gspread  # this is a modified version! see requirements.txt
import logging

SPREADSHEET_ID = '1MTbU9Bq130zrrsJwLIB9d8qnGfYZnkm4jBlfNaBF19M'
PATH = os.path.dirname(os.path.realpath(__file__))

debug = False

if debug:
    import requests_cache
    requests_cache.install_cache(
        'cache',
        backend='sqlite',
        allowable_methods=('GET', 'POST'),
        allowable_codes=(200, 401, 403, 404, 502, 503, 301, 302, 303),
    )


def find_patches_for_row(row, patches):
    required_patches = set()
    for col_id, cell in enumerate(row):
        if cell in ('', 'Not Required', 'Not Supported', 'Under investigation', 'Ask support'):
            continue
        elif cell.startswith('Replaced by'):
            continue
        elif cell == 'Required':
            patch = patches[col_id]
        elif cell.startswith('Use '):
            patch = cell[4:]
        else:
            logging.warning("Unsupported status: %s" % cell)
            continue

        required_patches.add(patch)
    return sorted(required_patches)


gc = gspread.public()
document = gc.open_by_key(SPREADSHEET_ID)

giant_blob = {}

for sheet in document.worksheets():
    matrix = sheet.get_all_values()
    assert matrix[1][0] == 'Version'

    edition = matrix[2][0]  # Community or Enterprise
    patches = matrix[1][2:]  # skip first 2 cols

    giant_blob[edition] = {}

    for row_id in range(3, 50):
        version = matrix[row_id][0]
        # break on first empty row
        if not version:
            break
        required_patches = find_patches_for_row(matrix[row_id][2:], patches)
        giant_blob[edition][version] = required_patches

assert 'SUPEE-7405' not in giant_blob['Enterprise']['1.6.x']
assert 'SUPEE-6788' in giant_blob['Enterprise']['1.6.x']
assert 'SUPEE-6079' not in giant_blob['Enterprise']['1.14.2.0']

assert 'SUPEE-7405' in giant_blob['Community']['1.4.0.0']
assert 'SUPEE-3762' not in giant_blob['Community']['1.4.0.0']

#print(json.dumps(giant_blob, indent=2))

with open(PATH + '/../fixtures/required_magento_patches.json', 'w') as f:
    f.write(json.dumps(giant_blob, indent=2))
