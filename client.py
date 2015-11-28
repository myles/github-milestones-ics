from flask import current_app


class Client(object):

    def __init__(self, github, app=current_app):
        self.app = app
        self.github = github

        self.token = self.app.config['GITHUB_OAUTH_TOKEN']

        self.user = self.app.config.get('GITHUB_USERNAME')
        self.orgs = self.app.config.get('GITHUB_ORGS')

    def _get(self, resource, **kwargs):
        return self.github.get(resource, access_token=self.token, **kwargs)

    def user_repos(self, username):
        return self._get('users/%s/repos' % username)

    def org_repos(self, org):
        return self._get('orgs/%s/repos' % org)

    def repos(self):
        repos = []

        if self.user:
            repos += self.user_repos(self.user)

        if self.orgs:
            for org in self.orgs.split(','):
                repos += self.org_repos(org)

        return repos

    def milestones_urls(self):
        milestone_urls = []

        for repo in self.repos():
            if repo.get('has_issues'):
                milestone_url = 'repos/%s/milestones' % repo.get('full_name')
                milestone_urls += [milestone_url]

        return milestone_urls

    def milestones(self):
        milestones = []

        for milestone_url in self.milestones_urls():
            milestones += self._get(milestone_url)

        return milestones
