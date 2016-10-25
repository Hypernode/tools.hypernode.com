#!/usr/bin/env python3

import json
import os
from collections import defaultdict

import gspread  # this is a modified version! see requirements.txt
import logging

# https://docs.google.com/spreadsheets/d/1MTbU9Bq130zrrsJwLIB9d8qnGfYZnkm4jBlfNaBF19M/pubhtml
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
    required_patches = defaultdict(set)
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

        # requires different patch id's per mag version, so not usable for automatic parsing
        if 'APPSEC' in patch:
            continue

        if 'SUPEE' in patch:
            patch_id, _, patch_version = patch.partition(' ')
        else:
            # "Zend Security Update"
            patch_id, patch_version = patch, ''

        required_patches[patch_id].add(patch_version.lower())



    # sort patches alphabetically on patch version and take the latest (v2 over v1.1)
    required_patches = [k + ' ' + sorted(required_patches[k], reverse=True)[0] for k in required_patches]
    required_patches = [k.strip() for k in required_patches]
    return required_patches



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

try:
    assert 'SUPEE-6788' in giant_blob['Enterprise']['1.6.x']
    assert 'SUPEE-7405 v1.1' in giant_blob['Enterprise']['1.14.2.1']

    assert 'SUPEE-7405' not in giant_blob['Enterprise']['1.6.x']
    assert 'SUPEE-6079' not in giant_blob['Enterprise']['1.14.2.0']
    assert 'SUPEE-7405' not in giant_blob['Enterprise']['1.14.2.1']
    assert 'SUPEE-3762' not in giant_blob['Community']['1.4.0.0']
except AssertionError:
    print("Patch parsing didn't work out. Result is:\n%s" % json.dumps(giant_blob, indent=2))
    raise

with open(PATH + '/../static/required_magento_patches.json', 'w') as f:
    f.write(json.dumps(giant_blob, indent=2))
