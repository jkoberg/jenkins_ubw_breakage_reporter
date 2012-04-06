import pythoncom
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket




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


class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "TestService"
    _svc_display_name_ = "Test Service"

    def __init__(self,args):
        self.stop = False
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.stop = True
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        self.main()

    def main(self):
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
              
        

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)
    

