import os
import sys

import django
from django.test.runner import DiscoverRunner


class NoDbTestRunner(DiscoverRunner):

    def setup_databases(self, **kwargs):
        pass

    def teardown_databases(self, config, **kwargs):
        pass


if __name__ == '__main__':
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
    django.setup()
    test_runner = NoDbTestRunner()
    failures = test_runner.run_tests(['tests'])
    sys.exit(bool(failures))
