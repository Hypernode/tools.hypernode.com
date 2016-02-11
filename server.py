from bottle import request
import bottle
import views.patches
import views.modules


# make available to UWSGI
app = application = bottle.Bottle()

# Propagate exceptions to uwsgi
app.catchall = False


@app.post('/modules/magerun<format:re:\.?(json|txt)?>')
def magerun_module_check(format='.json'):
    format = format.lstrip('.').lower()
    return views.modules.magerun(request, format)


@app.get('/patches/<edition>/<version>')
def find_required_patches_for_magento_version(edition, version):
    edition = edition.title()
    return views.patches.patch_requirements_for_version(edition, version)


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True, reloader=True)
