AcTor
-----

![AcTor](https://raw.githubusercontent.com/tbabej/actor/master/actor-logo.png  "Activity moniTor daemon")

AcTor, or Activity Monitor Daemon, is a extremely pluggable deamon that
monitors activity on your computer and executes user-defined actions 
depending on the input.

What can actor do
-----------------

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

Basic installation steps are:

```
git clone https://github.com/tbabej/actor.git
cp ~/.config/systemd/user/actor.service
systemctl --user enable actor.service  # Makes AcTor run at startup
```

To make AcTor actually enforce something, we need to define a rule:

```
mkdir config
cd config
vim exercise-break.yaml
```

AcTor recognizes any .yaml files in the config directory. This must
be valid yaml file, in the format as example below.

You also need to define few local configuration values:

```
cp local_config.py.in local_config.py
vim local_config.py
```

Now you're all set. Start actor with:

```
systemctl --user start actor.service
```

Basic architecture. Do not skip this!
-------------------------------------

On a high level, AcTor is a tool that enforces user-defined rules.

Each rule:

1. takes defined input, which is
1. evaluated using defined conditions,
1. and depending on these conditions specific actions are undertaken.

Each of this part of functionality is taken care of by a specific type of
plugin:

1. Input is provided by *reporters*
1. Values from reporters are given to *checkers* which change their state
   to false or true, depending on the values from the reporters. We call a
   checker with state 'true' an *active checker*.
1. Active checkers trigger fixers that are configured to be triggered by
   these active checkers. Fixers interact with your system.

Time for a explanatory example
------------------------------

There's a big chance you suffer from lack of physical exercise. Let's
demonstrate an example which will get you away from your computer!

    - Morning exercise break:
        reporters:
        - TimeReporter:
        checkers:
        - TimeIntervalChecker:
            start: "9.30"
            end: "10.00"
        fixers:
        - LockScreenFixer:

The example above takes input from one reporter (namely TimeReporter),
plugs the output to the only specified checker (TimeIntervalChecker)
and if this checker evaluates to true, the only fixer specified
(LockScreenFixer) is run. Say goodbye to your computer from 9.30
to 10.00. It's time for a little exercise!

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
