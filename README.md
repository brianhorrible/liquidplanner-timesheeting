# LiquidPlanner Timesheeting

Python git hook that allows you to apply time to Liquidplanner tasks based on your GIT branch name.

### Requirements:
  - Requests library v1.0 or later <http://docs.python-requests.org/en/latest/index.html>
  

# How to Use It
  - Create a quick sh script in .git/hooks/ called pre-push that calls


    $ python /path/to/lp-timesheeting.py
  - Every time you try to push to origin, it will prompt you to log your time to a task matched against the branch name. 
  - If one does not exist, the program will exit but the script can easily be modified to create a new task if one does not exist. The function call is present.

