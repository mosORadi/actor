AcTor
-----

![AcTor](https://raw.githubusercontent.com/tbabej/actor/master/actor-logo.png  "Activity moniTor daemon")

AcTor, or Activity Monitor Daemon, is a extremely pluggable deamon that
monitors activity on your computer and executes user-defined actions 
depending on the input.

Basic architecture. Do not skip this!
-------------------------------------

On a high level, AcTor is a tool that enforces user-defined rules.

Each rule:
1. takes defined input, which is
2. evaluated using defined conditions,
3. and depending on these conditions specific actions are undertaken.

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


Attribution
-----------

The AcTor logo is based on icons from thenounproject, that were released under public domain.
