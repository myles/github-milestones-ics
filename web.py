import os
import re
from datetime import datetime

import pytz
from icalendar import Calendar, Event, vCalAddress, vText

from flask import Flask, Response, render_template

from flask.ext.github import GitHub
from flask.ext.dotenv import DotEnv

app = Flask(__name__)

if os.path.exists(os.path.join(os.getcwd(), ".env")):
    env = DotEnv(app)
else:
    app.config.setdefault('AUTH_USERNAME', os.environ.get('AUTH_USERNAME'))
    app.config.setdefault('AUTH_PASSWORD', os.environ.get('AUTH_PASSWORD'))
    app.config.setdefault('GITHUB_USERNAME', os.environ.get('GITHUB_USERNAME'))
    app.config.setdefault('GITHUB_ORGS', os.environ.get('GITHUB_ORGS'))
    app.config.setdefault('GITHUB_CLIENT_ID',
                          os.environ.get('GITHUB_CLIENT_ID'))
    app.config.setdefault('GITHUB_CLIENT_SECRET',
                          os.environ.get('GITHUB_CLIENT_SECRET'))
    app.config.setdefault('GITHUB_OAUTH_TOKEN',
                          os.environ.get('GITHUB_OAUTH_TOKEN'))

github = GitHub(app)

from auth import requires_auth
from client import Client

re_url_info = re.compile('^https://github.com/(?P<name>.*)/(?P<repo>.*)' +
                         '/milestones/(?P<milestone>.*)$')


@app.route('/')
def index():
    return 'Hello, World!'


@app.route('/github-calendar.ics')
@requires_auth
def ics_file():
    cal = Calendar()
    cal.add('prodid', '-//GitHub Milestone ICS Feed//herokuapp.com//')
    cal.add('version', '2.0')

    for milestone in Client(github).milestones():
        if milestone.get('due_on'):
            creator = milestone.get('creator')
            dtstart = datetime.strptime(milestone['due_on'],
                                        '%Y-%m-%dT%H:%M:%SZ')
            created = datetime.strptime(milestone['created_at'],
                                        '%Y-%m-%dT%H:%M:%SZ')
            updated = datetime.strptime(milestone['updated_at'],
                                        '%Y-%m-%dT%H:%M:%SZ')

            name, repo, m = re_url_info.findall(milestone.get('html_url'))[0]

            event = Event()
            event.add('summary', "%s/%s - %s" % (name, repo,
                                                 milestone.get('title')))
            event.add('description', milestone.get('description'))

            event.add('dtstart', dtstart.date())
            event.add('dtend', dtstart.date())
            event.add('dtstamp', dtstart.date())
            event.add('created', created.replace(tzinfo=pytz.utc))
            event.add('last-modified', updated.replace(tzinfo=pytz.utc))

            event.add('uid', milestone.get('id'))

            event.add('url', milestone.get('html_url'))

            organizer = vCalAddress('MAILTO:%s@users.noreply.github.com' %
                                    creator.get('login'))
            organizer.params['cn'] = vText(creator.get('login'))

            event['organizer'] = organizer

            cal.add_component(event)

    mimetype = 'text/x-calendar'
    headers = {
        'Content-Disposition': 'attachment;filename=github-calendar.ics'
    }

    return Response(response=cal.to_ical(),
                    status=200,
                    mimetype=mimetype,
                    headers=headers)


@app.route('/login')
def login():
    return github.authorize(scope='repo,read:org')


@app.route('/github-test')
def github_test():
    repo_dict = Client(github).milestones()
    return str(len(repo_dict))


@app.route('/github-callback')
@github.authorized_handler
def authorized(oauth_token):
    if oauth_token is None:
        flash("Authorization failed.")
        print('GitHub authorization failed.')

    print('GITHUB_OAUTH_TOKEN=%s' % oauth_token)


@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
