from flask import render_template
from . import main


@main.app_errorhandler(404)
def page_not_found(e):
    #  TODO setup an personalized page for 404 error return page+message error
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def page_not_found(e):
    #  TODO setup an personalized page for 500 error
    return render_template('500.html'), 500
