import json
import os
from bottle import abort

PATH = os.path.dirname(os.path.realpath(__file__)) + '/../static/required_magento_patches.json'


def patch_requirements_for_version(edition, version):

    with open(PATH) as f:
        patch_matrix = json.loads(f.read())

    try:
        return dict(required=patch_matrix[edition][version])
    except KeyError:
        abort(404, "This Magento edition or version was not found")
