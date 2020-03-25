from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.test import APITestCase
from rest_framework import status

from .test_app.views import TestView


class TestViewTestCase(APITestCase):

    data_1 = {
        '[0][attribute]': 'size',
        '[0][verbose][0]': 'bazz',
        '[0][verbose][1]': 'foo',
        '[0][variant][vendor_metric]': '456',
        '[0][variant][metric_verbose_name]': 'Large',
        '[0][foo][baaz]': 'ggg',
        '[1][attribute]': 'size',
        '[1][verbose]': 'size',
        '[1][variant][vendor_metric]': 'L',
        '[1][variant][metric_verbose_name][foo][baaz][]': 'Large',
        '[1][foo][baaz]': 'true',
        '[1][logo]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg')
    }

    def test_post(self):

        response = self.client.post('/test/', self.data_1)
        
        expected_output = [
            {
                'attribute': 'size', 
                'verbose': ['bazz', 'foo'], 
                'variant': {
                    'vendor_metric': 456, 
                    'metric_verbose_name': 'Large'
                }, 
                'foo': { 'baaz': 'ggg' }
            }, 
            {
                'attribute': 'size', 
                'verbose': 'size', 
                'variant': {
                    'vendor_metric': 'L', 
                    'metric_verbose_name': { 'foo': { 'baaz': ['Large'] } }
                }, 
                'foo': { 'baaz': True },
                'logo': response.data[1]['logo']
            }
        ]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data, expected_output)