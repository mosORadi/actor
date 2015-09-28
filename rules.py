import collections
import logging
import re
import yaml

from plugins import PluginMount, Reporter, Checker, Fixer


class PythonRule(object):
    """Performs custom python rule"""

    __metaclass__ = PluginMount

    def run(self):
        """Evaluates custom python rule"""
        pass

class DeclarativeRule(object):
    """
    Rule given by declarative YAML definition.
    """

    def __init__(self, name):
        self.reporters = []
        self.checkers = []
        self.fixers = []
        self.name = name

    @classmethod
    def from_file(cls, path, actor):
        with open(path, "r") as f:
            definition = yaml.load(f)

        # If the file does not specify name for the rule,
        # use filename
        if 'name' not in definition:
            definition['name'] = os.path.basename(path)

        return cls.from_yaml(definition, actor)

    @classmethod
    def from_yaml(cls, config, actor):

        name = config.get("name")
        reporters_info = config.get("reporters")
        checkers_info = config.get("checkers")
        fixers_info = config.get("fixers", {})
        fixergroups_info = config.get("fixergroups", {})

        assert reporters_info is not None
        assert checkers_info is not None
        assert fixers_info or fixergroups_info

        rule = cls(name=name)

        for plugin_name, options in reporters_info.iteritems():
            options = options or {}
            reporter_plugin = actor.get_plugin(plugin_name,
                                               category=Reporter)
            reporter = reporter_plugin(**options)
            rule.reporters.append(reporter)

        for plugin_name, options in checkers_info.iteritems():
            options = options or {}
            checker_plugin = actor.get_plugin(plugin_name,
                                              category=Checker)
            checker = checker_plugin(**options)
            rule.checkers.append(checker)

        all_checker_names = [checker.export_as for checker in rule.checkers]

        for plugin_name, options in fixers_info.iteritems():
            options = options or {}

            if 'triggered_by' not in options:
                # Since we're using formulas now, we need to construct
                # formula which is valid only if all checkers are true
                all_active_formula = ' and '.join(all_checker_names)
                options['triggered_by'] = all_active_formula

            fixer_plugin = actor.get_plugin(plugin_name,
                                            category=Fixer)
            fixer = fixer_plugin(**options)
            rule.fixers.append(fixer)

        for group_name, group_options in fixergroups_info.iteritems():

            if 'triggered_by' not in group_options:
                # Since we're using formulas now, we need to construct
                # formula which is valid only if all checkers are true
                all_active_formula = ' and '.join(all_checker_names)
                group_options['triggered_by'] = all_active_formula

            if 'fixers' not in group_options:
                raise ValueError("You have to specify fixers "
                                 "for %s in %s" %
                                 (group_name, rule.name))

            for fixer in group_options['fixers']:
                for plugin_name, options in fixer.iteritems():
                    options = options or {}
                    options.update(group_options)
                    options.pop('fixers')

                    fixer_plugin = actor.get_plugin(plugin_name,
                                                category=Fixer)
                    fixer = fixer_plugin(**options)
                    rule.fixers.append(fixer)

        # Check that all reporters and checkers have unique exports
        for plugins_by_type, type_name in [(rule.reporters, 'Reporters'),
                                           (rule.checkers, 'Checkers')]:
            plugin_names_list = [plugin.export_as
                                 for plugin in plugins_by_type]
            duplicates = [k for k, v
                          in collections.Counter(plugin_names_list).items()
                          if v > 1]

            if duplicates:
                raise ValueError("DeclarativeRule %s has name clash in %s for "
                                 "the following identifiers: %s. "
                                 "Use the export_as option to differentiate." %
                                 (rule.name, type_name, duplicates))

        # Check that all checkers and fixers have valid triggers
        token_regex = "(?<![a-z_0-9])(?!and |or |not )(?P<token>[a-z_0-9]+)(?=[ )]|$)"


        for fixer in rule.fixers:
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

        return rule

    def run(self):
        logging.debug("Checking rule %s" % self.name)
        logging.debug("")

        # Generate reports
        reports = {reporter.export_as: reporter.report()
                   for reporter in self.reporters}

        logging.debug("Reports:")
        for k,v in reports.iteritems():
            logging.debug("     %s : %s" % (k, v))
        logging.debug("")

        # Determine which checkers approve the situation
        checker_state = {checker.export_as: checker.check_raw(**reports)
                         for checker in self.checkers}

        logging.debug("Active checkers: %s" %
             ','.join([c for c, s in checker_state.iteritems() if s])
        )

        # Run all the fixers that were triggered
        # By default fixer needs all the checkers defined to be active
        for fixer in self.fixers:
            if eval(fixer.options['triggered_by']):
                fixer.fix_raw(**reports)

