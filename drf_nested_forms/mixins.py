import re

# Nested Form data deserializer utility class
# --------------------------------------------


class UtilityMixin(object):

    _nested_re = (
        re.compile(r'(.+)((\[(.*)\])+)'),
        re.compile(r'(\[(.*)\]){2,}')
    )
    _namespace_re = re.compile(r'^([\w]+)(?=\[)')
    _list_re = re.compile(r'\[([0-9]{1,3})\]')
    _number_re = re.compile(r'[\0-9]+')
    _empty_list_re = re.compile(r'\[\]')
    _empty_dict_re = re.compile(r'\{\}')
    _dict_re = (
        re.compile(r'\[([^0-9]+)\]'),
        re.compile(r'\[([^0-9].)\]'),
        re.compile(r'\[(.[^0-9])\]'),
        re.compile(r'\[([\w]{4,})\]')
    )

    @staticmethod
    def strip_bracket(string=''):
        return string.replace('[', '').replace(']', '')

    @staticmethod
    def split(string=''):
        """
        Split the formData key into substrings
        """
        subkeys = [key + ']' for key in string.split(']') if key is not '']

        assert len(subkeys) > 0, ('Cannot split this key `%s`' % (string))

        return subkeys

    def is_dict(self, string=''):
        """
        Checks if the string passed is a dict object
        """
        condition = [
            bool(pattern.fullmatch(string))
            for pattern in self._dict_re
        ]

        return any(condition)

    def is_list(self, string=''):
        return bool(self._list_re.fullmatch(string))

    def is_number(self, string=''):
        return bool(self._number_re.fullmatch(string))

    def is_empty_list(self, string=''):
        return bool(self._empty_list_re.fullmatch(string))

    def is_empty_dict(self, string=''):
        return bool(self._empty_dict_re.fullmatch(string))

    def is_nested_string(self, string=''):
        condition = [
            bool(pattern.fullmatch(string))
            for pattern in self._nested_re
        ]

        return any(condition)

    def is_namespaced(self, string=''):
        return bool(self._namespace_re.match(string))

    def get_namespace(self, string=''):
        namespace = self._namespace_re.match(string)

        if namespace:
            return namespace.group(0)

        return None

    def strip_namespace(self, string=''):
        """
        Strip namespace from key if any 
        """
        namespace = self._namespace_re.match(string)

        if namespace:
            splited_str = string.split(namespace.group(1))

            assert len(splited_str) > 0, (
                'Cannot strip namespace from' 'this key `%s`' % (string)
            )

            string = ''.join(splited_str)

            return string

        return string

    def extract_index(self, string=''):
        number = self._number_re.search(string)

        if number:
            return int(number.group(0))

        return None

    def replace_specials(self, string):
        """
        Checks for and replaces special characters like null, booleans
        also changes numbers from string to integer
        """
        # the incoming value may not be a string sometimes
        if not isinstance(string, str):
            return string

        if string == 'null':
            return None
        elif string == 'true':
            return True
        elif string == 'false':
            return False
        elif self.is_number(string):
            return int(string)
        elif self.is_empty_list(string):
            return []
        elif self.is_empty_dict(string):
            return {}
        else:
            return string

    def get_container(self, key, index=0):
        """
        It return the appropiate container `[]`|`{}`
        based on the key provided
        """
        sub_keys = self.split(key)

        if self.is_list(sub_keys[index]):
            return []
        elif self.is_dict(sub_keys[index]):
            return {}
        else:
            return None

    def is_last(self, current_key, data, is_type_of):
        """
        Checks if current key is the last in the data
        """
        keys = list(data.keys())
        current_index = keys.index(current_key)
        next_index = current_index + 1

        def object_type(is_obj):
            try:
                next_key = self.split(keys[next_index])[0]
                if is_obj(next_key):
                    is_last = False
                else:
                    is_last = True
            except IndexError:
                is_last = True

            return is_last

        def namespace():
            try:
                next_key = keys[next_index]
                if self.is_namespaced(next_key):
                    current_namespace = self.get_namespace(current_key)
                    next_namespace = self.get_namespace(next_key)

                    if current_namespace == next_namespace:
                        is_last = False
                    else:
                        is_last = True
                else:
                    is_last = True
            except IndexError:
                is_last = True

            return is_last

        def ordinary():
            try:
                if not self.is_namespaced(keys[next_index]):
                    next_k = self.split(keys[next_index])[0]

                    if not self.is_list(next_k) and not self.is_dict(next_k):
                        is_last = False
                    else:
                        is_last = True
                else:
                    is_last = True
            except IndexError:
                is_last = True

            return is_last

        if is_type_of == 'L':
            return object_type(self.is_list)
        elif is_type_of == 'N':
            return namespace()
        elif is_type_of == 'D':
            return object_type(self.is_dict)
        else:
            return ordinary()
