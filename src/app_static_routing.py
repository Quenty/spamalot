from flask import send_from_directory


def init_routes(app):
    @app.route('/js/bootstrap/<path:path>')
    def send_bootstrap_js(path):
        return send_from_directory('../node_modules/bootstrap/dist/js', path)

    @app.route('/css/bootstrap/<path:path>')
    def send_bootstrap_css(path):
        return send_from_directory('../node_modules/bootstrap/dist/css', path)

    @app.route('/js/sweetalert2/<path:path>')
    def send_sweetalert_js(path):
        return send_from_directory('../node_modules/sweetalert2/dist', path)

    @app.route('/css/sweetalert2/<path:path>')
    def send_sweetalert_css(path):
        return send_from_directory('../node_modules/sweetalert2/dist', path)

    @app.route('/js/jquery/<path:path>')
    def send_jquery(path):
        return send_from_directory('../node_modules/jquery/dist', path)

    @app.route('/css/<path:path>')
    def send_css(path):
        return send_from_directory('static/css', path)
