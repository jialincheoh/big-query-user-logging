import httplib2
import pprint
import sys

from apiclient.discovery import build
from apiclient.errors import HttpError

from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run


# Enter your Google Developer Project number
PROJECT_NUMBER = '62608776331'

FLOW = flow_from_clientsecrets('client_secrets.json',
                               scope='https://www.googleapis.com/auth/bigquery')



def main():

  storage = Storage('bigquery_credentials.dat')
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run(FLOW, storage)

  http = httplib2.Http()
  http = credentials.authorize(http)

  bigquery_service = build('bigquery', 'v2', http=http)
  jobs = bigquery_service.jobs()

  page_token=None
  count=0

  while True:
    response = list_jobs_page(jobs, page_token)
    if response['jobs'] is not None:
      for job in response['jobs']:
        count += 1
        print '%d. %s\t%s\t%s' % (count,
                                  job['jobReference']['jobId'],
                                  job['state'],
                                  job['errorResult']['reason'] if job.get('errorResult') else '')
    if response.get('nextPageToken'):
      page_token = response['nextPageToken']
    else:
      break


def list_jobs_page(jobs, page_token=None):
  try:
    jobs_list = jobs.list(projectId=PROJECT_NUMBER,
                          projection='minimal',
                          allUsers=True,
                          maxResults=1000,
                          pageToken=page_token).execute()

    return jobs_list

  except HttpError as err:
    print 'Error:', pprint.pprint(err.content)


if __name__ == '__main__':
  main()
