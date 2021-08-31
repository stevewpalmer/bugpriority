# Script to download bugs from the Bugzilla Mozilla database.

import requests
import sys
import os

product = 'firefox'
opened_after = '2020-01-01'
opened_before = '2020-04-30'
fields = 'id,description,priority,status,resolution,nick'

# The API key needs to be obtained by creating an account on bugzilla.mozilla.org
# and requesting a key from the account settings.

api_key = os.getenv('BUGZILLA_API_KEY')
if (not api_key):
    print('error: BUGZILLA_API_KEY must be set before running this script', file=sys.stderr)
    exit()

URL = 'https://bugzilla.mozilla.org/rest/bug?product=' + product + '&opened_after=' + opened_after + '&opened_before=' + opened_before + '&include_fields=' + fields

headers = {"Content-type": "application/json"}
params = {
    "api_key": api_key,
}

print(URL, file=sys.stderr)
resp = requests.get(URL, headers=headers, params=params)

if resp.status_code != 200:
    print('error: ' + str(resp.status_code), file=sys.stderr)
else:
    print(resp.text)

