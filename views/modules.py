import os
import redis
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
        if not module['Version'] or not LooseVersion(module['Version']):
            print("Cannot parse version '%(Version)s' for module '%(Name)s', skipping" % module)
            continue

        try:
            latest = store_and_get_latest_version(module)
        except (TypeError, AttributeError) as e:
            # LooseVersion is not very good
            print("oeps, exception for module", e, module)
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
    print("Storing version for name, version, return:", name, version, rv)
    return rv
