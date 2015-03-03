#!/usr/bin/python

import collections
import os
import logging
import hashlib
import traceback
import re
import importlib

import gobject
import dbus
import dbus.mainloop.glib
import yaml

from plugins import IReporter, IChecker, IFixer

from config import CONFIG_DIR, HOME_DIR
from local_config import SLEEP_HASH


class Actor(object):

    def __init__(self):
        self.activities = []

    def main(self):
        # Start dbus mainloop
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        # Load the plugins
        self.import_plugins()

        # Load the Actor configuration
        self.load_configuration()

        # Start the main loop
        loop = gobject.MainLoop()
        gobject.timeout_add(2000, self.check_everything)
        logging.info("AcTor started.")
        loop.run()

    def setup_logging(self, daemon_mode=False, level=logging.WARNING):
        # Setup Actor logging
        config = dict(format='%(asctime)s: %(levelname)s: %(message)s',
                      datefmt='%m/%d/%Y %I:%M:%S %p',
                      level=level)

        if daemon_mode:
            config.update(dict(filename=os.path.join(HOME_DIR, 'actor.log')))

        logging.basicConfig(**config)

    def log_exception(self, exception_type, value, tb):
        logging.error("Exception: %s", exception_type)
        logging.error("Value: %s", value)
        logging.error("Traceback: %s", traceback.format_exc())

    def import_plugins(self):
        import reporters, checkers, fixers
        categories = [reporters, checkers, fixers]

        for category in categories:
            for module in category.__all__:
                try:
                    module_id = "{0}.{1}".format(category.__name__, module)
                    importlib.import_module(module_id)
                    logging.debug(module_id + " loaded successfully.")
                except Exception, e:
                    logging.warning("The {0} {1} module could not be loaded. "
                                    "Increase verbosity level to see more "
                                    "information."
                                    .format(module, category.__name__[:-1]))
                    logging.info(str(e))

    def get_plugin(self, name, category):
        plugin_candidates = [plugin for plugin in category.plugins
                             if plugin.__name__ == name]

        if plugin_candidates:
            return plugin_candidates[0]
        else:
            raise ValueError("Could not find %s plugin of name: %s"
                              % (category.__name__, name))

    def load_configuration(self):
        # Create the config directory, if it does not exist
        if not os.path.exists(CONFIG_DIR):
            os.mkdir(CONFIG_DIR)

        yaml_config_paths = [os.path.join(CONFIG_DIR, path)
                             for path in os.listdir(CONFIG_DIR)
                             if path.endswith('.yaml')]

        if not yaml_config_paths:
            logging.warning("No YAML activity configuration available")

        for path in yaml_config_paths:
            with open(path, "r") as f:
                activity_definitions = yaml.load(f)

                for config in activity_definitions:
                    activity = Activity.from_yaml(config, self)
                    self.activities.append(activity)

    def check_sleep_file(self):
        """
        You can create one sleep file in your home directory.
        It immediately suspends AcTor.
        """

        sleep_file_path = os.path.join(HOME_DIR, 'actor-sleep')
        if os.path.exists(sleep_file_path):
            with open(sleep_file_path, 'r') as f:
                content = f.readlines()[0].strip()
                content_hash = hashlib.sha1(content).hexdigest()

            return content_hash == SLEEP_HASH

    def check_everything(self):
        if self.check_sleep_file():
            logging.warning('Sleep file exists, skipping.')
            return True

        for activity in self.activities:
            logging.debug("%s: Checking activity %s" % (activity.name,
                                                        activity.name))
            logging.debug("")

            # Generate reports
            reports = {reporter.export_as: reporter.report()
                       for reporter in activity.reporters}

            logging.debug("%s: Reports:" % activity.name)
            for k,v in reports.iteritems():
                logging.debug("%s:     %s : %s" % (activity.name, k, v))
            logging.debug("")

            # Determine which checkers approve the situation
            checker_state = {checker.export_as: checker.check_raw(**reports)
                             for checker in activity.checkers}

            logging.debug("%s: Active checkers: %s" % (
                 activity.name,
                 ','.join([c for c, s in checker_state.iteritems() if s])
            ))

            # Run all the fixers that were triggered
            # By default fixer needs all the checkers defined to be active
            for fixer in activity.fixers:
                if eval(fixer.options['triggered_by']):
                    fixer.fix_raw(**reports)

        return True


class Activity(object):

    def __init__(self, name):
        self.reporters = []
        self.checkers = []
        self.fixers = []
        self.name = name

    @classmethod
    def from_yaml(cls, config, actor):
        definitions = [(name, details) for (name, details)
                                       in config.iteritems()]
        assert len(definitions) == 1
        name = definitions[0][0]
        details = definitions[0][1]

        reporters_info = details.get("reporters")
        checkers_info = details.get("checkers")
        fixers_info = details.get("fixers")
        fixergroups_info = details.get("fixergroups")

        assert reporters_info is not None
        assert checkers_info is not None
        assert fixers_info is not None or fixergroups_info is not None

        activity = cls(name=name)

        for reporter_info in reporters_info:
            for plugin_name, options in reporter_info.iteritems():
                options = options or {}
                options['activity_name'] = activity.name

                reporter_plugin = actor.get_plugin(plugin_name,
                                                   category=IReporter)
                reporter = reporter_plugin(**options)
                activity.reporters.append(reporter)

        for checker_info in checkers_info:
            for plugin_name, options in checker_info.iteritems():
                options = options or {}
                options['activity_name'] = activity.name

                checker_plugin = actor.get_plugin(plugin_name,
                                                  category=IChecker)
                checker = checker_plugin(**options)
                activity.checkers.append(checker)

        all_checker_names = [checker.export_as for checker in activity.checkers]

        if fixers_info is not None:
            for fixer_info in fixers_info:
                for plugin_name, options in fixer_info.iteritems():
                    options = options or {}
                    options['activity_name'] = activity.name

                    if 'triggered_by' not in options:
                        # Since we're using formulas now, we need to construct
                        # formula which is valid only if all checkers are true
                        all_active_formula = ' and '.join(all_checker_names)
                        options['triggered_by'] = all_active_formula

                    fixer_plugin = actor.get_plugin(plugin_name,
                                                    category=IFixer)
                    fixer = fixer_plugin(**options)
                    activity.fixers.append(fixer)

        if fixergroups_info is not None:
            for group_info in fixergroups_info:
                for group_name, group_options in group_info.iteritems():

                    if 'triggered_by' not in group_options:
                        # Since we're using formulas now, we need to construct
                        # formula which is valid only if all checkers are true
                        all_active_formula = ' and '.join(all_checker_names)
                        group_options['triggered_by'] = all_active_formula

                    if 'fixers' not in group_options:
                        raise ValueError("You have to specify fixers "
                                         "for %s in %s" %
                                         (group_name, activity.name))

                    for fixer in group_options['fixers']:
                        for plugin_name, options in fixer.iteritems():
                            options = options or {}
                            options['activity_name'] = activity.name
                            options.update(group_options)
                            options.pop('fixers')

                            fixer_plugin = actor.get_plugin(plugin_name,
                                                        category=IFixer)
                            fixer = fixer_plugin(**options)
                            activity.fixers.append(fixer)

        # Check that all reporters and checkers have unique exports
        for plugins_by_type, type_name in [(activity.reporters, 'Reporters'),
                                           (activity.checkers, 'Checkers')]:
            plugin_names_list = [plugin.export_as
                                 for plugin in plugins_by_type]
            duplicates = [k for k, v
                          in collections.Counter(plugin_names_list).items()
                          if v > 1]

            if duplicates:
                raise ValueError("Activity %s has name clash in %s for "
                                 "the following identifiers: %s. "
                                 "Use the export_as option to differentiate." %
                                 (activity.name, type_name, duplicates))

        # Check that all checkers and fixers have valid triggers
        token_regex = "(?<![a-z_0-9])(?!and |or |not )(?P<token>[a-z_0-9]+)(?=[ )]|$)"


        for fixer in activity.fixers:
            trigger = fixer.options['triggered_by']

            references = set(re.findall(token_regex, trigger))
            checkers_set = set(all_checker_names)

            # Check if any reference is not a checker name
            if references - checkers_set:
                raise ValueError("The following references are "
                                 "not checker names: %s" %
                                 ', '.join(references - checkers_set))

            trigger = re.sub(token_regex, "checker_state.get('\g<token>')", trigger)
            fixer.options['triggered_by'] = trigger

        return activity

if __name__ == "__main__":
    actor = Actor()
    actor.setup_logging()
    actor.main()
