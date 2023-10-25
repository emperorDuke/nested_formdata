from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.test import APITestCase


class TestViewTestCase(APITestCase):

    def test_multipart_view_nested_dict(self):

        data_2 = {
            'user_address': 1,
            '[products][0][quantity]': 2,
            '[products][0][attributes][0][code]': 'color',
            '[products][0][attributes][0][value]': 'Pink',
            '[products][0][attributes][0][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg'),
            '[products][0][attributes][1][code]': 'size',
            '[products][0][attributes][1][value]': '6.0',
            '[products][0][attributes][1][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg'),
            '[products][0][attributes][2][code]': 'multi-pack',
            '[products][0][attributes][2][value]': 'No',
            '[products][0][attributes][2][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg'),
            '[products][0][images][0][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg'),
            '[products][0][images][1][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg'),
            '[products][0][images][2][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg'),
            '[products][1][quantity]': 3,
            '[products][1][attributes][0][code]': 'color',
            '[products][1][attributes][0][value]': 'Green',
            '[products][1][attributes][1][code]': 'multi-pack',
            '[products][1][attributes][1][value]': 'Yes',
            '[products][1][images][0][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic2', content_type='image/jpeg'),
            '[products][1][images][1][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic2', content_type='image/jpeg'),
            '[products][1][images][2][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg'),
            'orderer': 11,
        }

        response = self.client.post(
            '/test-multipart/', data_2, format='multipart')

        expected_output = {
            'user_address': 1,
            'products': [
                {
                    'quantity': 2,
                    'attributes': [
                        {'code': 'color', 'value': 'Pink',
                            'image': response.data['products'][0]['attributes'][0]['image']},
                        {'code': 'size', 'value': '6.0',
                            'image': response.data['products'][0]['attributes'][1]['image']},
                        {'code': 'multi-pack', 'value': 'No',
                            'image': response.data['products'][0]['attributes'][2]['image']}
                    ],
                    'images': [
                        {'image': response.data['products']
                            [0]['images'][0]['image']},
                        {'image': response.data['products']
                            [0]['images'][1]['image']},
                        {'image': response.data['products']
                            [0]['images'][2]['image']},
                    ],
                },
                {
                    'quantity': 3,
                    'attributes': [
                        {'code': 'color', 'value': 'Green'},
                        {'code': 'multi-pack', 'value': 'Yes'}
                    ],
                    'images': [
                        {'image': response.data['products']
                            [1]['images'][0]['image']},
                        {'image': response.data['products']
                            [1]['images'][1]['image']},
                        {'image': response.data['products']
                            [1]['images'][2]['image']},
                    ]
                }
            ],
            'orderer': 11,
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_output)

    def test_multipart_view_nested_namespace(self):

        data_2 = {
            'user_address': 1,
            'products[0][quantity]': 2,
            'products[0][attributes][0][code]': 'color',
            'products[0][attributes][0][value]': 'Pink',
            'products[0][attributes][0][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg'),
            'products[0][attributes][1][code]': 'size',
            'products[0][attributes][1][value]': '6.0',
            'products[0][attributes][1][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg'),
            'products[0][attributes][2][code]': 'multi-pack',
            'products[0][attributes][2][value]': 'No',
            'products[0][attributes][2][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg'),
            'products[0][images][0][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg'),
            'products[0][images][1][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg'),
            'products[0][images][2][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg'),
            'products[1][quantity]': 3,
            'products[1][attributes][0][code]': 'color',
            'products[1][attributes][0][value]': 'Green',
            'products[1][attributes][1][code]': 'multi-pack',
            'products[1][attributes][1][value]': 'Yes',
            'products[1][images][0][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic2', content_type='image/jpeg'),
            'products[1][images][1][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic2', content_type='image/jpeg'),
            'products[1][images][2][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg'),
            'orderer': 11,
        }

        response = self.client.post(
            '/test-multipart/', data_2, format='multipart')

        expected_output = {
            'user_address': 1,
            'products': [
                {
                    'quantity': 2,
                    'attributes': [
                        {'code': 'color', 'value': 'Pink',
                            'image': response.data['products'][0]['attributes'][0]['image']},
                        {'code': 'size', 'value': '6.0',
                            'image': response.data['products'][0]['attributes'][1]['image']},
                        {'code': 'multi-pack', 'value': 'No',
                            'image': response.data['products'][0]['attributes'][2]['image']}
                    ],
                    'images': [
                        {'image': response.data['products']
                            [0]['images'][0]['image']},
                        {'image': response.data['products']
                            [0]['images'][1]['image']},
                        {'image': response.data['products']
                            [0]['images'][2]['image']},
                    ],
                },
                {
                    'quantity': 3,
                    'attributes': [
                        {'code': 'color', 'value': 'Green'},
                        {'code': 'multi-pack', 'value': 'Yes'}
                    ],
                    'images': [
                        {'image': response.data['products']
                            [1]['images'][0]['image']},
                        {'image': response.data['products']
                            [1]['images'][1]['image']},
                        {'image': response.data['products']
                            [1]['images'][2]['image']},
                    ]
                }
            ],
            'orderer': 11,
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_output)

    def test_multipart_view_nested_list(self):

        data_2 = {
            'user_address': 1,
            '[0][quantity]': 2,
            '[0][attributes][0][code]': 'color',
            '[0][attributes][0][value]': 'Pink',
            '[0][attributes][0][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg'),
            '[0][attributes][1][code]': 'size',
            '[0][attributes][1][value]': '6.0',
            '[0][attributes][1][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg'),
            '[0][attributes][2][code]': 'multi-pack',
            '[0][attributes][2][value]': 'No',
            '[0][attributes][2][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg'),
            '[0][images][0][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg'),
            '[0][images][1][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg'),
            '[0][images][2][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg'),
            '[1][quantity]': 3,
            '[1][attributes][0][code]': 'color',
            '[1][attributes][0][value]': 'Green',
            '[1][attributes][1][code]': 'multi-pack',
            '[1][attributes][1][value]': 'Yes',
            '[1][images][0][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic2', content_type='image/jpeg'),
            '[1][images][1][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic2', content_type='image/jpeg'),
            '[1][images][2][image]': SimpleUploadedFile('hp.jpeg', b'hp_pic', content_type='image/jpeg'),
            'orderer': 11,
        }

        response = self.client.post(
            '/test-multipart/', data_2, format='multipart')

        expected_output = {
            'user_address': 1,
            '': [
                {
                    'quantity': 2,
                    'attributes': [
                        {'code': 'color', 'value': 'Pink',
                            'image': response.data[''][0]['attributes'][0]['image']},
                        {'code': 'size', 'value': '6.0',
                            'image': response.data[''][0]['attributes'][1]['image']},
                        {'code': 'multi-pack', 'value': 'No',
                            'image': response.data[''][0]['attributes'][2]['image']}
                    ],
                    'images': [
                        {'image': response.data['']
                            [0]['images'][0]['image']},
                        {'image': response.data['']
                            [0]['images'][1]['image']},
                        {'image': response.data['']
                            [0]['images'][2]['image']},
                    ],
                },
                {
                    'quantity': 3,
                    'attributes': [
                        {'code': 'color', 'value': 'Green'},
                        {'code': 'multi-pack', 'value': 'Yes'}
                    ],
                    'images': [
                        {'image': response.data['']
                            [1]['images'][0]['image']},
                        {'image': response.data['']
                            [1]['images'][1]['image']},
                        {'image': response.data['']
                            [1]['images'][2]['image']},
                    ]
                }
            ],
            'orderer': 11,
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
