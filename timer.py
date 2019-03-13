import os, time
import subprocess

from yaml import load, dump, Loader, Dumper

CONFIG_PATH = os.path.dirname(os.path.abspath(__file__))

def shell(cmd):
    # cmd = cmd.split(' ')
    p = subprocess.Popen(cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True)
    # p.communicate()
    return p.stdout.read()


class Usage(object):
    """
    Apps Usage Control.
    Will store and inform about timers run time and limits.
    """
    timer = None
    file = None

    def __init__(self, timer):
        super(Usage, self).__init__()
        self.timer = timer
        self.file = '%s/usage/%s' % (CONFIG_PATH, self.timer.name)

    @property
    def current(self):
        '''Current usage of this timer in minutes'''
        if not os.path.isfile(self.file):
            return 0
        with open(self.file, 'r') as f:
            current = f.read()
        return int(current) if current else 0

    def increment(self, time):
        '''Increment this timer usage'''
        usage = self.current + int(time)
        with open(self.file, 'w') as f:
            f.write(str(usage))

    def release(self):
        '''Remove the timer usage to restart the counter'''
        os.remove(self.file)

    def isOffLimit(self):
        '''Is the timer usage off its limits'''
        time_limit = self.timer.timeLimit
        if (time_limit < 0):
            return False
        if self.current > time_limit:
            return True

    def isOffInterval(self):
        '''Is the timer usage expired'''
        limit_interval = self.timer.limitInterval
        if (limit_interval < 0):
            return False
        if not os.path.exists(self.file):
            return False
        usage_started = os.path.getctime(self.file)
        usage_expiry = usage_started + (limit_interval * 60 * 60)
        return time.time() >= usage_expiry


class Timer(object):
    """
    Apps Timer Setup.
    Will manage a timer and proxy its configuration
    """
    item = None
    name = None
    usage = None

    def __init__(self, name, item):
        super(Timer, self).__init__()
        self.name = name
        self.item = item
        self.usage = Usage(self)

    @property
    def timeLimit(self):
        time_limit = self.item.get('time-limit', -1)
        return int(time_limit)
    @property
    def limitInterval(self):
        limit_interval = self.item.get('limit-interval', -1)
        return float(limit_interval)

    @property
    def apps(self):
        item_apps = self.item.get('apps', [])
        if not isinstance(item_apps, list):
            item_apps = [item_apps]
        apps = [app.strip() for app in item_apps]
        return apps

    def isRunning(self):
        running = False
        for app in self.apps:
            cmd = 'ps aux | grep -v grep | grep "%s"' % app
            res = shell(cmd)
            if len(res):
                running = True
        return running

    def block(self):
        for app in self.apps:
            cmd = 'killall "%s"' % app
            shell(cmd)


class Config(object):
    """
    Config Parser.
    Read and normalize the configuration objects
    """
    data = None
    timers = None
    mtime = 0

    def __init__(self):
        super(Config, self).__init__()
        self.file = '%s/config.yaml' % CONFIG_PATH
        self.reload()

    def hasChanges(self):
        '''Check if the config file has changes'''
        mtime = os.path.getmtime(self.file)
        return self.mtime != mtime

    def reload(self):
        '''Reload config file data'''
        self.mtime = os.path.getmtime(self.file)
        self.data = self.read()
        self.timers = self.getTimers()

    def read(self):
        '''Read the config file yaml object'''
        with open(self.file, 'r') as f:
            data = load(f, Loader=Loader)
        return data

    def getTimers(self):
        '''Gets a generator of Timer objects'''
        config_timers = self.data.get('timers', {})
        timers = []
        for name, item in config_timers.items():
            timers.append(Timer(name, item))
        return timers

    @property
    def checkInterval(self):
        '''How often the usage check should happen'''
        interval = self.data.get('check-interval', 1)
        return int(interval)


def check_timers(config):
    '''Will check every timer setup for it's usage and limits'''
    for timer in config.timers:
        # restore timers after interval
        if timer.usage.isOffInterval():
            print('Timer %s is off interval' % timer.name)
            timer.usage.release()
        if not timer.isRunning():
            continue
        print('Timer %s is running' % timer.name)
        # check for off limit apps
        if timer.usage.isOffLimit():
            print('Timer %s is off limit' % timer.name)
            timer.block()
        # increment running apps timer
        timer.usage.increment(config.checkInterval)


config = Config()
while True:
    # check config changes
    if config.hasChanges():
        print('Config has changes')
        config.reload()
    # check app timers
    check_timers(config)
    # wait interval in minutes
    time.sleep(-time.time() % (config.checkInterval * 60))
