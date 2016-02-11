import json
import os
from bottle import abort

PATH = os.path.dirname(os.path.realpath(__file__)) + '/../fixtures/required_magento_patches.json'

with open(PATH) as f:
    SOURCE = json.loads(f.read())

def patch_requirements_for_version(edition, version):
    try:
        return dict(required=SOURCE[edition][version])
    except KeyError:
        abort(404, "This Magento edition or version was not found")
