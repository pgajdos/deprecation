# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# As we unfortunately support Python 2.7, it lacks TestCase.subTest which
# is in 3.4+ or in unittest2
import unittest
if not hasattr(unittest.TestCase, "subTest"):
    import unittest2 as unittest
import warnings

import deprecation
from datetime import date


class Test_deprecated(unittest.TestCase):

    def test_args_set_on_base_class(self):
        args = (1, 2, 3, 4)
        dw = deprecation.DeprecatedWarning(*args)
        self.assertEqual(dw.args, args)

    def test_removing_without_deprecating(self):
        self.assertRaises(TypeError, deprecation.deprecated,
                          deprecated_in=None, removed_in="1.0")

    def test_docstring(self):
        for test in [{"args": {},
                      "__doc__": "docstring\n\n.. deprecated::"},
                     {"args": {"deprecated_in": "1.0"},
                      "__doc__": "docstring\n\n.. deprecated:: 1.0"},
                     {"args": {"deprecated_in": "1.0", "removed_in": "2.0"},
                      "__doc__": "docstring\n\n.. deprecated:: 1.0"
                                 "\n   This will be removed in 2.0."},
                     {"args": {"deprecated_in": "1.0", "removed_in": "2.0",
                               "details": "some details"},
                      "__doc__": "docstring\n\n.. deprecated:: 1.0"
                                 "\n   This will be removed in 2.0. "
                                 "some details"},
                     {"args": {"deprecated_in": "1.0", "removed_in": date(2200, 5, 20)},
                      "__doc__": "docstring\n\n.. deprecated:: 1.0"
                                 "\n   This will be removed on 2200-05-20."},
                     {"args": {"deprecated_in": "1.0", "removed_in": date(2100, 3, 15),
                               "details": "some details"},
                      "__doc__": "docstring\n\n.. deprecated:: 1.0"
                                 "\n   This will be removed on 2100-03-15. "
                                 "some details"}]:
            with self.subTest(**test):
                @deprecation.deprecated(**test["args"])
                def fn():
                    """docstring"""

                self.assertEqual(fn.__doc__, test["__doc__"])

    def test_multiline_docstring(self):
        docstring = "summary line\n\ndetails\nand more details\n"
        for test in [{"args": {},
                      "__doc__": "%s\n\n.. deprecated::"},
                     {"args": {"deprecated_in": "1.0"},
                      "__doc__": "%s\n\n.. deprecated:: 1.0"},
                     {"args": {"deprecated_in": "1.0", "removed_in": "2.0"},
                      "__doc__": "%s\n\n.. deprecated:: 1.0"
                                 "\n   This will be removed in 2.0."},
                     {"args": {"deprecated_in": "1.0", "removed_in": "2.0",
                               "details": "some details"},
                      "__doc__": "%s\n\n.. deprecated:: 1.0"
                                 "\n   This will be removed in 2.0. "
                                 "some details"},
                     {"args": {"deprecated_in": "1.0", "removed_in": date(2200, 11, 20)},
                      "__doc__": "%s\n\n.. deprecated:: 1.0"
                                 "\n   This will be removed on 2200-11-20."},
                     {"args": {"deprecated_in": "1.0", "removed_in": date(2100, 3, 15),
                               "details": "some details"},
                      "__doc__": "%s\n\n.. deprecated:: 1.0"
                                 "\n   This will be removed on 2100-03-15. "
                                 "some details"}]:
            with self.subTest(**test):
                @deprecation.deprecated(**test["args"])
                def fn():
                    """summary line

                    details
                    and more details
                    """

                self.assertEqual(fn.__doc__, test["__doc__"] % (docstring))

    def test_multiline_docstring_top(self):
        summary = "summary line"
        content = "\n\ndetails\nand more details\n"
        for test in [{"args": {},
                      "__doc__": "%s\n\n.. deprecated::%s"},
                     {"args": {"deprecated_in": "1.0"},
                      "__doc__": "%s\n\n.. deprecated:: 1.0%s"},
                     {"args": {"deprecated_in": "1.0", "removed_in": "2.0"},
                      "__doc__": "%s\n\n.. deprecated:: 1.0"
                                 "\n   This will be removed in 2.0.%s"},
                     {"args": {"deprecated_in": "1.0", "removed_in": "2.0",
                               "details": "some details"},
                      "__doc__": "%s\n\n.. deprecated:: 1.0"
                                 "\n   This will be removed in 2.0. "
                                 "some details%s"},#####
                     {"args": {"deprecated_in": "1.0", "removed_in": date(2200, 11, 20)},
                      "__doc__": "%s\n\n.. deprecated:: 1.0"
                                 "\n   This will be removed on 2200-11-20.%s"},
                     {"args": {"deprecated_in": "1.0", "removed_in": date(2100, 3, 15),
                               "details": "some details"},
                      "__doc__": "%s\n\n.. deprecated:: 1.0"
                                 "\n   This will be removed on 2100-03-15. "
                                 "some details%s"}]:
            with self.subTest(**test):
                deprecation.message_location = "top"

                @deprecation.deprecated(**test["args"])
                def fn():
                    """summary line

                    details
                    and more details
                    """

                self.assertEqual(fn.__doc__, test["__doc__"] % (summary,
                                                                content))

    def test_multiline_fallback(self):
        docstring = "summary line\n\ndetails\nand more details\n"
        for test in [{"args": {"deprecated_in": "1.0"},
                      "__doc__": "%s\n\n.. deprecated:: 1.0"}]:
            with self.subTest(**test):
                deprecation.message_location = "pot"

                @deprecation.deprecated(**test["args"])
                def fn():
                    """summary line

                    details
                    and more details
                    """

                self.assertEqual(fn.__doc__, test["__doc__"] % (docstring))

    def test_warning_raised(self):
        ret_val = "lololol"

        for test in [{"args": {},  # No args just means deprecated
                      "warning": deprecation.DeprecatedWarning,
                      "message": "method is deprecated"},
                     {"args": {"details": "do something else."},
                      "warning": deprecation.DeprecatedWarning,
                      "message": "method is deprecated. do something else."},
                     {"args": {"deprecated_in": "1.0",
                               "current_version": "2.0"},
                      "warning": deprecation.DeprecatedWarning,
                      "message": "method is deprecated as of 1.0."},
                     {"args": {"deprecated_in": "1.0",
                               "removed_in": "3.0",
                               "current_version": "2.0"},
                      "warning": deprecation.DeprecatedWarning,
                      "message": ("method is deprecated as of 1.0 "
                                  "and will be removed in 3.0.")},
                     {"args": {"deprecated_in": "1.0",
                               "removed_in": "2.0",
                               "current_version": "2.0"},
                      "warning": deprecation.UnsupportedWarning,
                      "message": "method is unsupported as of 2.0."},
                     {"args": {"deprecated_in": "1.0",
                               "removed_in": "2.0",
                               "current_version": "2.0",
                               "details": "do something else."},
                      "warning": deprecation.UnsupportedWarning,
                      "message": ("method is unsupported as of 2.0. "
                                  "do something else.")},
                     {"args": {"deprecated_in": "1.0",
                               "removed_in": date(2100, 4, 19),
                               "current_version": "2.0"},
                      "warning": deprecation.DeprecatedWarning,
                      "message": ("method is deprecated as of 1.0 "
                                  "and will be removed on 2100-04-19.")},
                     {"args": {"deprecated_in": "1.0",
                               "removed_in": date.today(),
                               "current_version": "2.0"},
                      "warning": deprecation.UnsupportedWarning,
                      "message": "method is unsupported as of %s." % date.today()},
                     {"args": {"deprecated_in": "1.0",
                               "removed_in": date(2020, 1, 30),
                               "current_version": "2.0",
                               "details": "do something else."},
                      "warning": deprecation.UnsupportedWarning,
                      "message": ("method is unsupported as of 2020-01-30. "
                                  "do something else.")}]:
            with self.subTest(**test):
                class Test(object):
                    @deprecation.deprecated(**test["args"])
                    def method(self):
                        return ret_val

                with warnings.catch_warnings(record=True) as caught_warnings:
                    warnings.simplefilter("always")

                    sot = Test()
                    self.assertEqual(ret_val, sot.method())

                self.assertEqual(len(caught_warnings), 1)
                self.assertEqual(caught_warnings[0].category, test["warning"])
                self.assertEqual(str(caught_warnings[0].message),
                                 test["message"])

    def test_DeprecatedWarning_not_raised(self):
        ret_val = "lololol"

        class Test(object):
            @deprecation.deprecated(deprecated_in="2.0",
                                    removed_in="3.0",
                                    current_version="1.0")
            def method(self):
                """method docstring"""
                return ret_val

        with warnings.catch_warnings(record=True):
            # If a warning is raised it'll be an exception, so we'll fail.
            warnings.simplefilter("error")

            sot = Test()
            self.assertEqual(sot.method(), ret_val)


class Test_fail_if_not_removed(unittest.TestCase):

    @deprecation.deprecated(deprecated_in="1.0", current_version="2.0")
    def _deprecated_method(self):
        pass

    @deprecation.deprecated(deprecated_in="1.0", removed_in="2.0",
                            current_version="2.0")
    def _unsupported_method(self):
        pass

    def test_UnsupportedWarning_causes_failure(self):
        with self.assertRaises(AssertionError):
            @deprecation.fail_if_not_removed
            def fn():
                self._unsupported_method()

            fn()

    def test_DeprecatedWarning_doesnt_fail(self):
        @deprecation.fail_if_not_removed
        def fn():
            self._deprecated_method()

        try:
            fn()
        except AssertionError:
            self.fail("A DeprecatedWarning shouldn't cause a failure")

    @unittest.expectedFailure
    @deprecation.fail_if_not_removed
    def test_literal_UnsupportedWarning(self):
        self._unsupported_method()

    @deprecation.fail_if_not_removed
    def test_literal_DeprecatedWarning(self):
        self._deprecated_method()
