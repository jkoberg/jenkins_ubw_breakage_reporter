import urllib2, json, time

#import feedparser
#jenkins_recent_build_feed = "http://ci-server/view/Core/job/Core-developing/rssAll"
#feed = feedparser.parse( jenkins_recent_build_feed )

last_success_url = "http://ci-server/job/%s/lastSuccessfulBuild/api/json"
last_fail_url = "http://ci-server/job/%s/lastUnsuccessfulBuild/api/json"



def get_json( url ):
  return json.load(urllib2.urlopen(url))


def get_monitored_job_names(apiurl="http://ci-server/view/monitoredBuilds/api/json"):
  monitored_builds_data = get_json(apiurl)
  return [job['name'] for job in monitored_builds_data['jobs']]


def check_if_failed(jobname):
  run_success = get_json(last_success_url % jobname)
  run_fail = get_json(last_fail_url % jobname)  
  if run_fail['timestamp'] > run_success['timestamp']:
    return true



import ubw_driver

def main():
  with ubw_driver.UBW('COM8') as ubw:
    ubw.set_to_output('A0')
    while True:
      for job in get_monitored_job_names():
        if check_if_failed(job):
          print "Detected failure on " + job
          ubw.turn_on('A0')
        else:
          ubw.turn_off('A0')
      time.sleep(120)
    
    
if __name__ == "__main__":
  main()
  
