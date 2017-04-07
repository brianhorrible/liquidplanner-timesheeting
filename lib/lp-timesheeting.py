# /usr/bin/python

import json
import os
import requests
import sys
from pprint import pprint

# Valid for LiquidPlanner API version: 3.0.0
# You need the Requests library, found at:
# http://docs.python-requests.org/en/latest/index.html
# note that Requests version 1.0 or later is required

# The following get-env only works in Unix environments and thus this script does not currently support Windows.
authentication_token_location = (os.getenv('HOME') + '/.lp-time/auth-token')


def check_if_auth_token_directory_exists():
    try:
        os.makedirs(os.path.dirname(authentication_token_location))
    except OSError:
        pass


def check_authentication_token():
    check_if_auth_token_directory_exists()
    try:
        authentication_token = (open(authentication_token_location, 'r')).read().strip()
        return authentication_token
    except IOError:
        print(
            '\nAuthentication token does not exist. Please go to Liquidplanner >> Settings >> My API Tokens and generate a key.')
        auth_input = raw_input(
            '\nPlease enter a valid API key now. We will automatically save this token for future use.\n')
        authentication_token = save_new_authentication_token(auth_input)
        return authentication_token


def save_new_authentication_token(auth_input):
    with open(authentication_token_location, 'w') as f:
        f.write(auth_input)
    return auth_input


def get_branch_name():
    try:
        branch_name = os.popen('git rev-parse --symbolic --abbrev-ref HEAD').read().strip()
        return branch_name
    except Exception:
        print('Could not retrieve GIT branch name. Are you sure that you are in the right location?')


class LiquidPlanner:
    lp_url = 'https://app.liquidplanner.com/api'
    task_url = 'https://app.liquidplanner.com/space'
    authentication_token = None
    workspace_id = None

    def __init__(self, authentication_token):
        self.authentication_token = authentication_token

    def validate_authentication_token(self):
        if self.get('/account').status_code == 200:
            pass
        else:
            raise Exception(
                '\n\nInvalid API key was passed in or LiquidPlanner is down. Please double check keys in ' + authentication_token_location)

    def get(self, uri, options={}):
        return requests.get(self.lp_url + uri,
                            data=options,
                            headers={'Authorization': 'Bearer ' + self.authentication_token,
                                     'Content-Type': 'application/json'}
                            )

    def post(self, uri, options={}):
        return requests.post(self.lp_url + uri,
                             data=options,
                             headers={'Authorization': 'Bearer ' + self.authentication_token,
                                      'Content-Type': 'application/json'}
                             )

    def put(self, uri, options={}):
        return requests.put(self.lp_url + uri,
                            data=options,
                            headers={'Authorization': 'Bearer ' + self.authentication_token,
                                     'Content-Type': 'application/json'}
                            )

    def get_workspace_id(self):
        return self.workspace_id

    def set_workspace_id(self, workspace_id):
        self.workspace_id = workspace_id

    # Returns a dictionary with information on the current user
    def account(self):
        return json.loads(self.get('/account').content)

    # Returns a list of dictionaries with information on all workspaces that the user is a member of
    def workspaces(self):
        return json.loads(self.get('/workspaces').content)

    # Returns a list of dictionaries with each project in a given workspace
    def projects(self):
        return json.loads(self.get('/workspaces/' + str(self.workspace_id) +
                                   '/projects').content)

    # Returns a list of dictionaries with each task in a given workspace
    def tasks(self):
        return json.loads(self.get('/workspaces/' + str(self.workspace_id) +
                                   '/tasks').content)

    def activities(self):
        return json.loads(self.get('/workspaces/' + str(self.workspace_id) +
                                   '/activities').content)

    def members(self):
        return json.loads(self.get('/workspaces/' + str(self.workspace_id) +
                                   '/members').content)

    def retrieve_activities(self):
        json_dict = self.activities()
        activities = {}

        for i in json_dict:
            activities[i['name']] = str(i['id'])

        return activities

    def retrieve_default_activity_id(self,account_id):
        json_dict = self.members()
        member_list = {}

        for i in json_dict:
            member_list[i['id']] = str(i['default_activity_id'])

        default_activity_id= member_list[account_id]
        return default_activity_id

    # Creates a task given a provided task name.
    def create_task(self, task_name):
        data = {'name': task_name}
        return json.loads(self.post('/workspaces/' + str(self.workspace_id)
                          + '/tasks',
                          json.dumps(data)).content)

    # Returns a dictionary with information on the most recent ACTIVE tasks found by fuzzy-matching a name
    def find_activity_by_fuzzy_name(self, task_name):
        return json.loads(self.get('/workspaces/' + str(self.workspace_id) +
                                   '/tasks?' + 'filter[]=' + 'name contains ' + task_name
                                   + '&' + 'filter[]=' + 'is_done is false'
                                   + '&' + 'order=updated_at'
                                   ).content)

    # Returns a dictionary with information on a particular ACTIVE task found by using the exact CASE-SENSITIVE name
    def find_activity_by_exact_name(self, task_name):
        return json.loads(self.get('/workspaces/' + str(self.workspace_id) +
                                   '/tasks?' + 'filter[]=' + 'name =' + task_name
                                   + '&' + 'filter[]=' + 'is_done is false'
                                   + '&' + 'order=updated_at'
                                   ).content)

    def track_time_to_task(self, activity_id, task_id, hours):
        data = {'activity_id': activity_id, 'work': str(hours), 'is_done': 'false'}

        return json.loads(self.post('/workspaces/' + str(self.workspace_id) +
                                    '/tasks/' + str(task_id) + '/track_time',
                                    json.dumps(data)).content)

    def show_task_url(self, task_id):
        url = (self.task_url + '/' + str(self.workspace_id) + '/projects' + '/show/' + str(task_id))
        return url


def main():
    try:
        authentication_token = check_authentication_token()

        # Setup workspaces
        LP = LiquidPlanner(authentication_token)
        LP.validate_authentication_token()

        workspace = LP.workspaces()[0]
        LP.set_workspace_id(workspace['id'])

        account_id= LP.account()['id']

        try:
            activity_id = LP.retrieve_default_activity_id(account_id)
        except Exception:
            print ("No Default Activity for your user found. Please select activity.")
            activity_list = LP.retrieve_activities()
            pprint(activity_list)
            activity_id = raw_input('No default activity found for your user. Please enter an activity ID.\n>')

        task_name = get_branch_name()
        task_data = LP.find_activity_by_fuzzy_name(task_name)

        # Grabbing the first and most recent active task returned.
        try:
            task_id = task_data[0]['id']
        except Exception:
            print('COULDN\'T FIND TASK.')
            sys.exit(1)

        print('Task found:' + task_data[0]['name'])
        print('LP URL:' + LP.show_task_url(task_id))
        print('If this is not the task you wanted, please hit CTRL+C to exit')

        hours = input('Please enter number of hours for your timesheet. \n>')
        if type(hours) == float or int:
            LP.track_time_to_task(activity_id, task_id, hours)
            print("Time successfully tracked for %s" % task_data[0]['name'])
        else:
            print('Entry must be a positive number. Not entering any time. Please update your timesheet manually!')
    except KeyboardInterrupt:
        print('Shutdown requested ... exiting')


if __name__ == '__main__':
    main()
