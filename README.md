AcTor
-----
[![Travis build status](https://travis-ci.org/tbabej/actor.svg?branch=master)](https://travis-ci.org/tbabej/actor)
[![Coverage Status](https://coveralls.io/repos/tbabej/actor/badge.svg?branch=master)](https://coveralls.io/r/tbabej/actor?branch=master)
[![Code Health](https://landscape.io/github/tbabej/actor/master/landscape.svg?style=flat)](https://landscape.io/github/tbabej/actor/master)

![AcTor](https://raw.githubusercontent.com/tbabej/actor/master/actor-logo.png  "Activity moniTor daemon")

Actor (or ACTivity monitOR), is an extremely pluggable deamon that
monitors activity on your computer and executes user-defined actions
depending on the input.

What can actor do for you
-------------------------

Examples include (but are not limited to):

* Enforcing sleep schedule (by hibernating PC at curfue)
* Forbidding you to visit time-wasting websites
* Allowing you to check email only at designated times
* Whitelisting allowed applications accroding to the day schedule
* Reminding you about not having tracked daily's expenses yet
* Reminding you about not having set goals for the next day
...

The list continues on and on. You are not limited to these examples,
AcTor can evaluate complex conditions and perform arbitrary actions
on your computer. To understand how AcTor works, read the Basic architecture
section.

Install
-------

To install Actor, you only need to run:

```
$ sudo pip install -U https://github.com/tbabej/actor/archive/master.zip
```

After that, you can run Actor easily by:

```
$ actor-daemon
```

This will, however, run make actor run directly in the terminal where you ran
the command. To make it run at every session startup, like it should, you can
use simple systemd service file (if your distribution uses systemd):

```
$ wget https://raw.githubusercontent.com/tbabej/actor/master/actor.service -O ~/.config/systemd/user/actor.service
$ systemctl --user enable actor.service
$ systemctl --user start actor.service
```

Usage
-----

While it's running, Actor evaluates three different groups of user-defined
plugins:

* **Flows**. A flow is a sequence of activities, with defined duration. Actor
  automatically shrinks the durations to accomodate the available time window,
  switches them when their respetive time is up and notifies you about it. A
  typical morning work flow might consist of: read emails (30 min), prepare
  plan for the day (15 min), code (2 hours), coffee break (10 min).
* **Activities**. An activity describes a particular general activity you're
  usually doing, i.e. development, book reading or writing. Actor supports
  plethora of options when defining activities, so you can automatically track
  time, perform starup actions, restrict allowed applications and much more.
* **Rules**. In the most of basic use cases, a rule defines what should happen
  when, i.e. my computer should suspend if it's sleep time. It's most flexible
  kind of a plugin.

Examples: A sleep curfue rule!
------------------------------

Currently, writing a rule (or an activity/flow) requires writing a simple
python class. Here's one that willmake sure you do not work on your computer
past your bed time.

```python
from actor.core.plugins import Rule

class SleepCurfue(Rule):
    def run(self):
        if self.check('time_interval', '22.00', '05.00'):
            self.fix('suspend')
```

However, you might want some warning before your computer denies you access.
Here's a more advanced version that will also display a notification.

```python
from actor.core.plugins import Rule

class SleepCurfue(Rule):
    def run(self):
        if self.check('time_interval', '21.45', '22.00'):
            self.fix('notify', message="You should brush your teeth and stuff!")
        if self.check('time_interval', '22.00', '05.00'):
            self.fix('suspend')
```

This file should be created in ```~/.actor/``` directory, i.e. ```~/.actor/sleep.py```.

Examples: A morning creative workflow
-------------------------------------

Flows and acitivities are easier to define than rules (since they are less
flexible). A flow or activity is just an empty python class with attributes. A
heavily commented example follows:

```python
from actor.core.activities import Activity, Flow

class CreativeFlow(Flow):

    # Use this to start the flow via CLI: $ actor flow-start creative
    identifier = 'creative'

    # List of activities and their durations
    activities = (
        ('actor_development', 55),
        ('health_break', 5),
        ('writing', 55),
        ('health_break', 5),
    )


class ActorDevel(Activity):

    # Identifier used to start the activity
    identifier = 'actor_development'

    # The category under which the activity should be tracked
    timetracking_id = "development"

    # Allowed and disallowed commands
    whitelisted_commands = ('firefox', 'xfce4-terminal')
    blacklisted_commands = ('mutt', 'newsbeuter')

    # Notification
    notification_headline = "Actor: Actor development"
    notification = ("Hack on Actor and make it a better tool that will serve its users.")

    # Display notifications after 50%, 75% and 90% of time passes
    progress_notifications = True


class HealthBreak(Activity):

    # Identifier used to start the activity
    identifier = 'health_break'

    # The category under which the activity should be tracked
    timetracking_id = 'healthbreak'

    # Block all activity on computer and display this message
    overlay_header = "Actor: Health break"
    overlay_message = ("Standup and stretch some. If possible, do some squats and pushups. ")


class Writing(Activity):

    # Identifier used to start the activity
    identifier = 'writing'

    # The category under which the activity should be tracked
    timetracking_id = "writing"

    # Allowed and disallowed commands
    whitelisted_commands = ('firefox', 'xfce4-terminal')
    blacklisted_commands = ('mutt', 'newsbeuter')

    # Notification
    notification_headline = "Actor: Book writing"
    notification = ("Develop your story. Make sure to not walk in circles. "
                    "Paint a scene, or connect plotlines.")

    # Display notifications after 50%, 75% and 90% of time passes
    progress_notifications = True
```

This file should be created in ```~/.actor/``` directory, i.e. ```~/.actor/creative.py```.

Command line controls
---------------------

Usually you want to decide when to start particular flow or activity manually.
To do that, use ```actor``` command:

```bash
$ actor flow-start morning
Flow 'morning' started.
$ actor flow-stop
$ actor activity-start running
Activity 'running' started.
$ actor pause 4
Actor paused for 4 minutes.
```

Available plugins
-----------------

As basic architecture section explains, each part of the AcTor functionality
is handled via plugins. The current set of plugins provides integration with:

* Reporters (sources of information)
  * Active windows
    * Active window process name
    * Active window PID
    * Active window title
  * Files
    * File content
  * Hamster time tracker
    * Current activity
    * Daily totals for activities
  * Time
    * Current time
    * Current weekday
  * D-Bus
    * D-Bus signals
  * Pidgin/finch
    * Incoming IM messages authors

* Checkers (available conditions)
  * Countdown
  * Confirmation
  * Regular expressions
  * Time intervals
  * Health checkers (False until all of it's HP is not taken by HealthDecreaseFixer)
  * Tautology (always True, useful for testing)
  * Hamster activity/category duration
* Fixers (available responses)
  * Killing processes
  * Locking sreen
  * Suspending PC
  * Sending D-BUS notifications
  * Setting Hamster activities
  * Reducing health count of HealtChecker number of HP
  * Emiting D-BUS signals

(note: the list may be incomplete)

Each plugin is fairly small, self-contained python file. A developement
of your own plugin should be a easy task! Please, consider contributing your
custom plugin via a pull request.

Attribution
-----------

The AcTor logo is based on icons from thenounproject, that were released under public domain.
