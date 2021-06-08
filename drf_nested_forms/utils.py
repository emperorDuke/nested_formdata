from collections.abc import Mapping

from .exceptions import ParseException
from .mixins import UtilityMixin


# Base serilizer for converting nested formdata to objects
# ---------------------------------------------------------

class BaseClass(UtilityMixin):

    def __init__(self, data, *args, **kwargs):
        self._initial_data = data
        self._allow_empty = kwargs.get('allow_empty', False)
        self._allow_blank = kwargs.get('allow_blank', True)

    def __process__(self):
        raise NotImplementedError('`__process__()` is not implemented')

    def __run__(self):
        if not hasattr(self, '_final_data'):
            self.__process__()

    @property
    def data(self):
        """
        Returns the final build
        """
        if not hasattr(self, '_final_data'):
            msg = '`.is_nested()` has to be called before accessing `.data`'
            raise AssertionError(msg)

        return self._final_data

    @property
    def validated_data(self):
        if not hasattr(self, '_validated_data'):
            msg = '`.is_nested()` has to be called before accessing `.validated_data`'
            raise AssertionError(msg)

        return self._validated_data

    @staticmethod
    def is_dict(obj):
        """
        Check if object is a dictionary
        """
        return isinstance(obj, dict)

    @staticmethod
    def is_list(obj):
        """
        Check if object is a list
        """
        return isinstance(obj, list)

    def is_nested(self, raise_exception=False):
        """
        Checks if the initial data map is a nested object
        """

        ###### Check if initial_data is a MultiValueDIct ############
        ###### Convert it to a dict object ##########################
        if hasattr(self._initial_data, 'getlist'):
            raw_data = {}

            for key, value in dict(self._initial_data).items():
                if len(value) > 1:
                    raw_data[key] = value
                else:
                    raw_data[key] = value[0]

            self._initial_data = raw_data
        #############################################################

        is_mapping = isinstance(self._initial_data, Mapping)
        conditions = [is_mapping]

        #############################################################
        if not is_mapping and raise_exception:
            raise ValueError('`data` is not a map type')
        #############################################################

        matched_keys = []

        for key in self._initial_data.keys():
            if self.str_is_nested(key):
                matched_keys.append(True)
                break
            else:
                matched_keys.append(False)

        conditions += [any(matched_keys)]

        #############################################################
        if not any(matched_keys) and raise_exception:
            raise ValueError('`data` is not a nested type')
        #############################################################

        if all(conditions):
            self._validated_data = self._initial_data
            self.__run__()

        return all(conditions)

    def clean_value(self, value, default=None):
        """
        Replace empty list, dict and empty string with `None`
        """
        if value == '' and not self._allow_blank:
            return default
        elif self.is_list(value) and len(value) == 0 and not self._allow_empty:
            return default
        elif self.is_dict(value) and len(value) == 0 and not self._allow_empty:
            return default

        return value


# serilizes a nested form data to object
# ---------------------------------------

class NestedForms(BaseClass):
    """
    Decode nested forms into python object
    """
    EMPTY_KEY = ''

    def __process__(self):
        """
        Initiates the conversion process and packages the final data
        """
        self._final_data = self._get_build()

    def _create_groups(self):
        groups, temporary_map = [], {}

        def get_map(key, type):
            if type == 'namespace':
                return {self.get_namespace(key): temporary_map}

            return {self.EMPTY_KEY: temporary_map}

        def group(key, data, value, type='non_nested'):
            nonlocal temporary_map

            if self.key_is_last(key, data, type):
                temporary_map.setdefault(self.strip_namespace(key), value)
                groups.append(get_map(key, type))
                temporary_map = {}
            else:
                temporary_map.setdefault(self.strip_namespace(key), value)

        return (groups, group)

    def _grouped_nested_data(self):
        """
        It groups nested structures of the same kind and namespaces together
        """
        data, (groups, group) = self.validated_data, self._create_groups()

        for key, value in data.items():
            if self.str_is_namespaced(key):
                group(key, data, value, 'namespace')
            elif self.str_is_list(self.split_nested_str(key)[0]):
                group(key, data, value, 'list')
            elif self.str_is_dict(self.split_nested_str(key)[0]):
                group(key, data, value, 'dict')
            else:
                group(key, data, value)

        return self._merge(groups)

    def _merge(self, grouped_data):
        """
        Merge grouped nested data with the same key
        """
        merged_map = []

        for data in grouped_data:
            group_key = next(iter(data))

            if len(merged_map) > 1 and group_key != self.EMPTY_KEY:
                for map in merged_map:
                    map_key = next(iter(map))

                    if group_key == map_key:
                        map_value = next(iter(map.values()))
                        group_data_value = next(iter(data.values()))

                        map_value.update(group_data_value)
                        break
            else:
                merged_map.append(data)

        return merged_map

    def _get_build(self):
        """
        gets the final build
        """
        data_map, final_build, top_wrapper = self._grouped_nested_data(), {}, []

        for data in data_map:
            group_key = next(iter(data))
            nested_struct = next(iter(data.values()))

            root_tree = self._decode(nested_struct)

            if group_key:
                final_build.setdefault(group_key, root_tree)
            else:
                if self.is_dict(root_tree):
                    final_build.update(root_tree)
                elif self.is_list(root_tree) and final_build:
                    final_build[self.EMPTY_KEY] = root_tree
                else:
                    top_wrapper.append(root_tree)

        if final_build:
            top_wrapper.append(final_build)

        if len(top_wrapper) == 1:
            return top_wrapper[0]
        elif len(top_wrapper) > 1:
            return top_wrapper
        else:
            raise ParseException('unexpected empty container')

    def _decode(self, nested_data):
        """
        Trys to Convert nested data to an object containing primitives
        """
        root_tree = self.get_container(next(iter(nested_data)))

        for key, value in nested_data.items():
            value = self.clean_value(self.replace_specials(value))

            if self.str_is_nested(key):
                self._build_object(key, value, root_tree)
            else:
                # the root tree is automatically a dict
                root_tree.setdefault(key, value)

        return root_tree

    def _build_step_structure(self, root, context, depth=0):
        """
        Insert and updates the root tree according to the context passed as
        argument
        """
        ############################################################################
        def build_root(root):
            """
            Build the data root structure using the context
            """
            if self.is_list(root):
                # check the difference between index of the last item in
                # the list and the current index to be added
                undefined_count = abs(len(root) - context['index'])

                if undefined_count > 1000:
                    raise ParseException('too many consecutive empty arrays !')
                elif undefined_count > 1 and undefined_count <= 1000:
                    # if it is sparse
                    # fill gaps with the `None`
                    root += [None] * undefined_count
                    # append the default value
                    root.append(context['value'])
                elif context['value'] and self.is_list(context['value']):
                    # if context value is not empty and its a list, transfer
                    # value into the root
                    root.extend(context['value'])
                else:
                    # just append like default
                    root.append(context['value'])
            else:
                root[context['index']] = context['value']
        ###############################################################################

        if context['depth'] == depth:
            try:
                # check if the root of interest is empty or exist
                inner_root = root[context['index']]

                if inner_root:
                    if self.is_list(inner_root) and context['value']:
                        inner_root.append(context['value'])
                    elif self.is_dict(inner_root) and self.is_dict(context['value']):
                        #  get keys that are not in inner root
                        # transfer their values to inner_root
                        for key in context['value'].keys():
                            if key not in inner_root:
                                inner_root.update(context['value'])
                else:
                    build_root(root)
            except (KeyError, IndexError):
                build_root(root)
        else:
            # if not depth of interest unpack the root object with keys
            # provided by context['keys']
            key = context['keys'][depth]
            self._build_step_structure(root[key], context, depth=depth + 1)

    def _build_object(self, nested_key, value, root_tree):
        """
        Build the data structure for a nested key and insert value
        """
        steps = self.split_nested_str(nested_key)
        steps_index_keys = []

        def get_index_keys(depth):
            """
            Get and store all the index keys for the nested key
            """
            prev_depth = depth - 1

            if prev_depth >= 0:
                steps_index_keys.append(self.get_index(steps[prev_depth]))
                return steps_index_keys

            return steps_index_keys

        def get_value(depth):
            """
            Get the nested sub key value
            """
            next_depth = depth + 1

            if next_depth < len(steps):
                if self.str_is_dict(steps[next_depth]):
                    # at this time the value of the dict is unknown
                    # so `None` is used
                    return {self.strip_bracket(steps[next_depth]): None}
                else:
                    return []

            return value

        for depth, step in enumerate(steps):
            self._build_step_structure(root_tree, {
                'depth': depth,
                'index': self.get_index(step),
                'value': get_value(depth),
                'keys': get_index_keys(depth)
            })
