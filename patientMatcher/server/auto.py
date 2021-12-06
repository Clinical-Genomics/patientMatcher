try:
    from werkzeug.contrib.fixers import ProxyFix
except ModuleNotFoundError:
    # Werkzeug >1.0 moved the library to middleware : https://github.com/pallets/werkzeug/issues/1477
    from werkzeug.middleware.proxy_fix import ProxyFix

from patientMatcher.server import create_app

app = create_app()

app.wsgi_app = ProxyFix(app.wsgi_app)
