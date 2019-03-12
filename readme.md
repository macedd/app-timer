# App Timer (Parental Control)

Control apps usage time with a command line application.

The python daemon will watch for the apps runtime (with `ps`) and store timing information about it's usage. It can block (`kill`) an app if the usage is off limits.

I'm using this at a raspberry pi gaming station to enforce usage limits.

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
  cp ./timer.service /etc/systemd/system/app-timer.service
  systemctl enable app-timer
```

Update this file to point `ExecStart` into your setup folder.
