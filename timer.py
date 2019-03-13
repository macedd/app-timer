import os, time

from lib import Config

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
