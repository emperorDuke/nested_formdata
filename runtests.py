import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == '__main__':
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2)
    failures = test_runner.run_tests(['tests.test_app.tests', 'tests.test_nested_form'])
    sys.exit(bool(failures))



