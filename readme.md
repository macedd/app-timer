# App Timer (Parental Control)

Control apps usage time with a command line application.

The python daemon will watch for the apps executable and store usage time for them. It can block an app if the usage is off limits.

I'm using this at a raspberry pi gaming station (retropie) to enforce usage limits. Other use cases are very plausible, like any other gaming platform or even enforcing a pomodoro timer for your coding time. Be creative and let me know.

## Config

```yaml
# how often should the script check for apps runtime?
check-interval: 1
# timers: list of apps that will be watched
timers:
  # the app name (list key)
  gaming:
    # list of the app executables
    apps:
      - retroarch
      - minecraft
    # how many minutes of usage
    time-limit: 60
    # within how many hours of interval
    limit-interval: 12
```

## Installation

There's a systemd service file ready for use.

```bash
  # download the sources
  cd /opt/
  git clone https://github.com/thiagof/app-timer
  cd app-timer
  # yaml dependency
  sudo -H pip3 install -r requirements.txt
  # setup the daemon
  sudo cp ./app-timer.service /etc/systemd/system/app-timer.service
  sudo systemctl enable app-timer
  # check the service
  sudo systemctl status app-timer
```
