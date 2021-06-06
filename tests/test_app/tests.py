from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.test import APITestCase


class TestViewTestCase(APITestCase):

    def test_multipart_view(self):

        data_2 = {
            'user_address': 1,
            'products[0][quantity]': 2,
            'products[0][attributes][0][code]': 'color',
            'products[0][attributes][0][value]': 'Pink',
            'products[0][attributes][1][code]': 'size',
            'products[0][attributes][1][value]': '6.0',
            'products[0][attributes][2][code]': 'multi-pack',
            'products[0][attributes][2][value]': 'No',
            'products[0][images][0][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg'),
            'products[0][images][1][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg'),
            'products[0][images][2][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg'),
            'products[0][images][3][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg'),
            'products[0][images][4][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg'),
            'orderer': 3,
        }

        response = self.client.post(
            '/test-multipart/', data_2, format='multipart')

        expected_output = {
            'user_address': 1,
            'products': [
                {
                    'quantity': 2,
                    'attributes': [
                        {'code': 'color', 'value': 'Pink'},
                        {'code': 'size', 'value': '6.0'},
                        {'code': 'multi-pack', 'value': 'No'}
                    ],
                    'images': [
                        {'image': response.data['products']
                            [0]['images'][0]['image']},
                        {'image': response.data['products']
                            [0]['images'][1]['image']},
                        {'image': response.data['products']
                            [0]['images'][2]['image']},
                        {'image': response.data['products']
                            [0]['images'][3]['image']},
                        {'image': response.data['products']
                            [0]['images'][4]['image']},
                    ]
                }
            ],
            'orderer': 3
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_output)

    def test_multipart_view_2(self):

        data = {
            'user_address': 1,
            'products[0][quantity]': 22,
            'products[0][attributes][0][code]': 'color',
            'products[0][attributes][0][value]': 'Pink',
            'products[0][attributes][1][code]': 'multi-pack',
            'products[0][attributes][1][value]': 'No',
            'products[0][images][0][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic1', content_type='image/jpeg'),
            'products[0][images][1][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic1', content_type='image/jpeg'),
            'products[1][quantity]': 33,
            'products[1][attributes][0][code]': 'color',
            'products[1][attributes][0][value]': 'Green',
            'products[1][attributes][1][code]': 'multi-pack',
            'products[1][attributes][1][value]': 'Yes',
            'products[1][images][0][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic2', content_type='image/jpeg'),
            'products[1][images][1][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic2', content_type='image/jpeg'),
            'orderer': 42,
        }

        response = self.client.post('/test-multipart/', data, format='multipart')

        expected_output = {
            'user_address': 1,
            'products': [
                {
                    'quantity': 22,
                    'attributes': [
                        {'code': 'color', 'value': 'Pink'},
                        {'code': 'multi-pack', 'value': 'No'}
                    ],
                    'images': [
                        {'image': response.data['products'][0]['images'][0]['image']},
                        {'image': response.data['products'][0]['images'][1]['image']},
                    ]
                },
                {
                    'quantity': 33,
                    'attributes': [
                        {'code': 'color', 'value': 'Green'},
                        {'code': 'multi-pack', 'value': 'Yes'}
                    ],
                    'images': [
                        {'image': response.data['products'][1]['images'][0]['image']},
                        {'image': response.data['products'][1]['images'][1]['image']},
                    ]
                }
            ],
            'orderer': 42
        }

        self.assertEqual(response.status_code, 200)
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
            '[1][logo]': 235
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
