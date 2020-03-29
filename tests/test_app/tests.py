from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.test import APITestCase
from rest_framework import status


class TestViewTestCase(APITestCase):

    def test_multipart_view(self):

        data = {
            '[0][attribute]': 'true',
            '[0][verbose][0]': 'bazz',
            '[0][verbose][1]': 'foo',
            '[0][variant][vendor_metric]': 'null',
            '[0][variant][metric_verbose_name]': 'Large',
            '[0][foo][baaz]': 'false',
            '[1][attribute]': 'size',
            '[1][verbose]': '[]',
            '[1][variant][vendor_metric]': '{}',
            '[1][variant][metric_verbose_name][foo][baaz][]': 'Large',
            '[1][foo][baaz]': '',
            '[1][logo]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg')
        }

        response = self.client.post(
            '/test-multipart/', data, format='multipart')

        expected_output = [
            {
                'attribute': True,
                'verbose': ['bazz', 'foo'],
                'variant': {
                    'vendor_metric': None,
                    'metric_verbose_name': 'Large'
                },
                'foo': {'baaz': False}
            },
            {
                'attribute': 'size',
                'verbose': None,
                'variant': {
                    'vendor_metric': None,
                    'metric_verbose_name': {'foo': {'baaz': ['Large']}}
                },
                'foo': {'baaz': ''},
                'logo': response.data[1]['logo']
            }
        ]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data, expected_output)

    def test_json_view(self):

        data = {
            '[0][attribute]': 'true',
            '[0][verbose][0]': 'bazz',
            '[0][verbose][1]': 'foo',
            '[0][variant][vendor_metric]': 'null',
            '[0][variant][metric_verbose_name]': 'Large',
            '[0][foo][baaz]': 'false',
            '[1][attribute]': 'size',
            '[1][verbose]': '[]',
            '[1][variant][vendor_metric]': '{}',
            '[1][variant][metric_verbose_name][foo][baaz][]': 'Large',
            '[1][foo][baaz]': '',
            '[1][logo]': '235'
        }

        response = self.client.post('/test-json/', data, format='json')

        expected_output = [
            {
                'attribute': True,
                'verbose': ['bazz', 'foo'],
                'variant': {
                    'vendor_metric': None,
                    'metric_verbose_name': 'Large'
                },
                'foo': {'baaz': False}
            },
            {
                'attribute': 'size',
                'verbose': None,
                'variant': {
                    'vendor_metric': None,
                    'metric_verbose_name': {'foo': {'baaz': ['Large']}}
                },
                'foo': {'baaz': ''},
                'logo': 235
            }
        ]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data, expected_output)
