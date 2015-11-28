# GitHub Milestones ICS Feed

A Heroku app to get an iCalendar feed of your GitHub Milestones.

## Usage

You will need to add a bunch of Heroku variables.

For the authtication of the ICS feed:

	$ heroku config:add AUTH_USERNAME=username
	$ heroku config:add AUTH_PASSWORD=password

What GitHub user and organization you want to get the milestones from (both are optional and you can have mutiple organizations sperated by a comma):

	$ heroku config:add GITHUB_USERNAME=githubusername
	$ heroku config:add GITHUB_ORGS=org1,org2

Next [register a new application at GitHub](https://github.com/settings/applications/new) and add your client ID and secret keys:

	$ heroku config:add GITHUB_CLIENT_ID=1234567890
	$ heroku config:add GITHUB_CLIENT_SECRET=1234567890

Go to `/login` and you will get the `GITHUB_OAUTH_TOKEN` in your `heroku logs`

Now add that:

	$ heroku config:add GITHUB_OAUTH_TOKEN=1234567890
