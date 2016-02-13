import os
import redis
import re
import logging
from bottle import abort
from distutils.version import LooseVersion

"""

magerun --skip-root-check --root-dir=/data/web/public --no-interaction sys:modules:list --status=active --format=json  | curl -d @- -X POST -H "Content-Type: application/json" http://modules.hypernode.com/query.txt

"""


POSTDATA_PATH = os.path.dirname(os.path.realpath(__file__)) + '/../fixtures/magerundumps'
REDIS_VERSION_HASH = 'magmodules'
REDIS_HOST = 'localhost'

redis_client = redis.Redis(
        host=REDIS_HOST,
        decode_responses=True,
)


def magerun(request, format):
    ip = request.environ.get('REMOTE_ADDR')

    # temp for debugging erroneous magerun output
    with open(POSTDATA_PATH + '/' + ip, 'wb') as f:
        f.write(request.body.read())

    try:
        decoded_json = request.json
        assert decoded_json
    except:
        abort(400, "Invalid post data, could not decode JSON")

    latest_versions = store_and_find_latest_versions(decoded_json.values())

    if format == 'json':
        return dict(versions=latest_versions)
    else:
        return versions_to_text(latest_versions)

def store_and_find_latest_versions(modules):
    latest_versions = []
    for module in modules:

        # empty or invalid version
        if not is_valid_version(module['Version']):
            logging.warning("Cannot parse version '%(Version)s' for module '%(Name)s', skipping" % module)
            continue

        try:
            latest = store_and_get_latest_version(module)
        except (TypeError, AttributeError) as e:
            # LooseVersion is not very good
            logging.error("oeps, exception for module: %s %s" % (e, module))
            continue


        # do this after storing, because i am interested in gathering core versions as well
        if module['codePool'] == 'core':
            continue

        latest_versions.append(latest)

    return sorted(latest_versions, key=lambda x: x['name'])

def versions_to_text(versions):
    lines = []
    for v in versions:
        if v['latest'] != v['current']:
            lines.append("%(name)-32s %(current)-12s %(latest)-12s\n" % v)

    if not lines:
        return "All local/community modules seem up to date!\n"

    header = [
        "%-32s %-12s %-12s\n" % ('Name', 'Current', 'Latest known'),
        "==============================================================\n"
    ]

    return ''.join(header + lines)

def is_valid_version(v):
    if not v:
        return False

    if not LooseVersion(v):
        return False

    return re.match('^[\.\w\d\-\_]+$', v)

def store_and_get_latest_version(module):
    """
    module =
    {
        "codePool": "community",
        "Name": "Phoenix_Moneybookers",
        "Version": "1.6.0.0",
        "Status": "active"
    }
    """
    name = module['Name']
    given = module['Version']
    stored = get_version(name)

    if not stored or LooseVersion(given) > LooseVersion(stored):
        # print("Storing new version! Name, old, new:", name, old, new)
        store_version(name, given)
        latest = given
    else:
        latest = stored

    return dict(name=name, latest=latest, current=given)

def get_version(name):
    return redis_client.hget(REDIS_VERSION_HASH, name)

def store_version(name, version):
    rv = redis_client.hset(REDIS_VERSION_HASH, name, version)
    logging.info("Storing version for %(name)s, %(version)s, %(rv)s" % locals())
    return rv


if __name__ == '__main__':
    assert is_valid_version('1.0.1')
    assert is_valid_version('1.03-patch')
    assert not is_valid_version('1.0\nrm%20-rf /')
    assert not is_valid_version('')
    assert not is_valid_version(None)