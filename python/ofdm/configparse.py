# encoding: iso8859-1
#
# configparse is distributed under a BSD license.
#
# configparse - Copyright (C)2005 Lars Gust�bel (lars@gustaebel.de)
# All rights reserved.
#
# Permission  is  hereby granted,  free  of charge,  to  any person
# obtaining a  copy of  this software  and associated documentation
# files  (the  "Software"),  to   deal  in  the  Software   without
# restriction,  including  without limitation  the  rights to  use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies  of  the  Software,  and to  permit  persons  to  whom the
# Software  is  furnished  to  do  so,  subject  to  the  following
# conditions:
#
# The above copyright  notice and this  permission notice shall  be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS  IS", WITHOUT WARRANTY OF ANY  KIND,
# EXPRESS OR IMPLIED, INCLUDING  BUT NOT LIMITED TO  THE WARRANTIES
# OF  MERCHANTABILITY,  FITNESS   FOR  A  PARTICULAR   PURPOSE  AND
# NONINFRINGEMENT.  IN  NO  EVENT SHALL  THE  AUTHORS  OR COPYRIGHT
# HOLDERS  BE LIABLE  FOR ANY  CLAIM, DAMAGES  OR OTHER  LIABILITY,
# WHETHER  IN AN  ACTION OF  CONTRACT, TORT  OR OTHERWISE,  ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# $Id: configparse.py 466 2005-08-31 14:00:58Z lars $

import shlex

from optparse import *
from optparse import NO_DEFAULT

from gnuradio.eng_option import eng_option

_OptionParser = OptionParser
_Option = eng_option #Option

__version__ = "0.3"




class Option(_Option):

    # Introduce a new keyword "config" to the constructor.
    ATTRS = _Option.ATTRS + ["config"]

    # Init checker list, it is modified below.
    CHECK_METHODS = _Option.CHECK_METHODS

    # -- Base class method replacements -----------------------------

    # In order to implement options that will only appear in
    # configfiles (config="only"), we have to override the
    # constructor to prevent optparse from complaining about
    # missing option strings.
    def __init__(self, *opts, **attrs):
        if attrs.get("config") != "only":
            _Option.__init__(self, *opts, **attrs)
        else:
            self._short_opts = []
            self._long_opts = []

            # Although it doesn't seem to make sense for config="only"
            # to set options strings (they're not allowed), we do it
            # anyway to give _check_config() the chance to raise the
            # OptionError.
            self._set_opt_strings(opts)

            self._set_attrs(attrs)
            for checker in self.CHECK_METHODS:
                checker(self)

        # FORCE DEFAULT
        if self.action not in ("help", "version", "callback"):
            self.config = "true"

    # Implement a different check method for the "dest" keyword
    # that can handle missing option strings and enforces a
    # value for "dest".
    def _check_dest(self):
        try:
            _Option._check_dest(self)
        except IndexError:
            # config="only" -> no option strings
            raise OptionError("must supply dest for option", self)

    # Replace the base _check_dest method by our own.
    CHECK_METHODS[CHECK_METHODS.index(_Option._check_dest.im_func)] = _check_dest

    # Implement a __str__ method that does die when there are no
    # option strings.
    def __str__(self):
        if getattr(self, "config", None) == "only":
            return "<%s>" % self.dest
        else:
            return _Option.__str__(self)

    # -- Additional methods -----------------------------------------

    # Implement a check method for the values of the "config"
    # keyword.
    def _check_config(self):
        if self.config is not None:
            if self.config not in ("true", "false", "only"):
                raise OptionError(
                    "invalid value %r for config keyword" % self.config, self)
            if self.config == "only" and self._short_opts + self._long_opts:
                raise OptionError(
                    "config-only option must not have option strings", self)
            if self.config != "false" and self.action in ("help", "version", "callback"):
                raise OptionError(
                    "action %r is not allowed for config option" % self.action, self)

    # Add the check method to the list so that it will be
    # executed in the constructor.
    CHECK_METHODS.append(_check_config)


class OptionParser(_OptionParser):

    # -- Override OptionParser methods ------------------------------

    # If option_class is not defined it defaults to configparse's
    # Option object instead of optparse's.
    def __init__(self,
                 usage=None,
                 option_list=None,
                 option_class=Option,       # our Option subclass
                 version=None,
                 conflict_handler="error",
                 description=None,
                 formatter=None,
                 add_help_option=True,
                 prog=None,
                 error_handler="error"):    # add error_handler
        _OptionParser.__init__(self, usage, option_list,
                option_class, version, conflict_handler,
                description, formatter, add_help_option,
                prog)
        self.set_error_handler(error_handler)

    # When errors are encountered in configfiles there are three
    # possible reactions: terminate with an error message, show
    # an error message for every error, ignore all errors.
    def set_error_handler(self, handler):
        if handler not in ("error", "warn", "ignore"):
            raise ValueError("invalid error_handler value %r" % handler)
        self.error_handler = handler

    # Allow adding options without defining option strings.
    def add_option(self, *args, **kwargs):
        if not args:
            if kwargs.get("config") != "only":
                raise TypeError, "invalid arguments"
            kwargs["help"] = SUPPRESS_HELP
            option = self.option_class(**kwargs)
            _OptionParser.add_option(self, option)
        else:
            _OptionParser.add_option(self, *args, **kwargs)

    # Add parsing of configfiles to parse_args(). The "files"
    # argument is optional and must be a list of filenames or
    # file objects that will be read one after the other.
    def parse_args(self, args=None, values=None, files=None):
        if values is None:
            values = self.get_default_values()

        for file_or_name in files or []:
            try:
                self._process_file(file_or_name, values)
            except EnvironmentError:
                continue

        return _OptionParser.parse_args(self, args, values)

    # -- Additional methods -----------------------------------------

    def write(self, fobj):
        """Write a representation of the parser's Values object
           to file object 'file'.
        """

        for opt, val in self.values.__dict__.iteritems():
            try:
                options = self._get_config_opts(opt)
            except BadOptionError:
                continue

            option = self._get_most_tolerant_opt(options)

            if val is not None and val != self.defaults[opt]:
                print >> fobj, opt, "=", self._pack_value(val)

    # -- Config-parsing methods -------------------------------------

    def _process_file(self, file_or_name, values):
        if type(file_or_name) is str:
            name = file_or_name
            fobj = file(file_or_name)

        else:
            if hasattr(file_or_name, "read"):
                name = getattr(file_or_name, "name", "<file>")
                fobj = file_or_name
            else:
                raise ValueError("argument must be a filename or file object!")

        lineno = 1
        for line in fobj:
            line = line.strip()
            if line and line[0] not in '#;':
                try:
                    self._process_line(line, values)
                except (BadOptionError, OptionValueError), err:
                    msg = "file %s, line %d: %s" % (name, lineno, err)
                    if self.error_handler == "error":
                        self.error(msg)
                    elif self.error_handler == "warn":
                        print >> sys.stderr, msg
            lineno += 1

    def _process_line(self, line, values):
        lexer = shlex.shlex(line, posix=True)
        lexer.wordchars += "."    # allow floats
        lexer.commenters = "#;"   # allow comments
        tokens = list(lexer)

        if len(tokens) < 3 or tokens[1] != "=":
            raise BadOptionError("line is malformed")

        opt = tokens[0]
        value = tokens[2:]

        options = self._get_config_opts(opt)
        option = self._get_most_tolerant_opt(options)

        if option.action != "append":
            if option.nargs is None or option.nargs == 1:
                value = value[0]
            elif len(value) % option.nargs:
                raise OptionValueError(
                    "need %d arguments" % option.nargs)

        if option.action in ("store_true", "store_false"):
            # Boolean options do not expect a value, so we fill
            # it in by hand.
            setattr(values, opt, self._parse_boolean(value))

        elif option.action == "count":
            # Because count options are increased by the number
            # of occurrences and do not take values, we must
            # fill in the value by hand.
            try:
                setattr(values, opt, int(value))
            except ValueError:
                raise OptionValueError("%r is no integer" % value)

        elif option.action == "store_const":
            # We have no other choice than to compare the
            # value obtained from the configfile (a string)
            # with the string representation of all consts to
            # find the right const. It is really awkward and
            # will work only for str, int, long, float.
            for o in options:
                if value == str(o.const):
                    setattr(values, opt, o.const)
                    break
            else:
                raise OptionValueError("%r is invalid" % value)

        elif option.action == "append":
            # We reset the config option everytime we come across
            # it.
            option.default = NO_DEFAULT

            for a in xrange(0, len(value), option.nargs + 1):
                # Parse a list of items separated by commas and
                # let the Option object process them the usual
                # way.
                b = a + option.nargs
                try:
                    v = value[a:b]
                except IndexError:
                    raise OptionValueError(
                        "config option %s requires %d arguments" % (opt, option.nargs))

                if b < len(value) and value[b] != ",":
                    raise OptionValueError("value is malformed")

                if option.nargs == 1:
                    v = v[0]

                option.process(opt, v, values, self)

        else:
            # All the other options (excluding those which are
            # disallowed anyway) can process their value the
            # standard way.
            option.process(opt, value, values, self)

    def _pack_value(self, value):
        if type(value) in (str, int, long, float, complex, bool):
            value = str(value)
            if " " in value:
                return '"%s"' % value.replace('"', '\\"')
            return value

        elif type(value) is tuple:
            return " ".join([self._pack_value(v) for v in value])

        elif type(value) is list:
            return ", ".join([self._pack_value(v) for v in value])

        else:
            raise ValueError("unable to write value %r" % value)

    def _get_most_tolerant_opt(self, options):
        # Return the Option object from the options list that puts the
        # least restrictions on the type of the value.
        #
        # This tries to deal with the fact that option values need not
        # be of consistent types. An example:
        #
        #   add_option("-a", action="store_const", const=True, dest="foo", ...)
        #   add_option("-b", action="store", type="int", dest="foo", ...)
        #   add_option("-c", action="store", type="string", dest="foo", ...)
        #
        # Both options manipulate the 'foo' destination differently which
        # is allowed by optparse. So we cannot put the restriction of the
        # const option or the int option on the value, because strings are
        # allowed too.

        option = None
        for o in options:
            if o.action in ("store_true", "store_false"):
                option = option or o
            elif o.action == "store_const":
                option = option or o
            elif o.choices is not None:
                option = option or o
            elif o.type != "string":
                option = option or o
            else:
                option = o
        return option

    def _parse_boolean(self, val):
        # A True boolean value is either a natural number or the
        # strings "true" or "yes". False is defined by either
        # "false" or "no".
        try:
            return bool(int(val))
        except (ValueError, TypeError):
            if val.lower() in ("true", "yes"):
                return True
            elif val.lower() in ("false", "no"):
                return False
            else:
                raise OptionValueError(
                        "%r is no boolean value" % val)

    def _get_config_opts(self, opt):
        # Return a list of Option objects that use opt as
        # destination and are marked as for configfiles.
        
        options = []
        for o in self.option_list:
            if opt == o.dest and o.config in ("true", "only"):
                options.append(o)

        for g in self.option_groups:
            for o in g.option_list:
                if opt == o.dest and o.config in ("true", "only"):
                    options.append(o)

        if not options:
            raise BadOptionError("unknown option %r" % opt)

        return options


