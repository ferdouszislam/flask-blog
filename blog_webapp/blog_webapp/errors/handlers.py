from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(404)
def error_404(error):
    print(f'404 error {str(error)}')
    return render_template('errors/404.html'), 404


@errors.app_errorhandler(403)
def error_403(error):
    print(f'403 error {str(error)}')
    return render_template('errors/403.html'), 403


@errors.app_errorhandler(500)
def error_500(error):
    print(f'500 error {str(error)}')
    return render_template('errors/500.html'), 500
