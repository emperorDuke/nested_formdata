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
        data_map, final_build, top_wrapper = self.grouped_nested_data(), {}, []

        for data in data_map:
            group_key = next(iter(data))
            nested_struct = next(iter(data.values()))

            root_tree = self.decode(nested_struct)

            if group_key:
                final_build.setdefault(group_key, root_tree)
            else:
                if self.is_dict(root_tree):
                    final_build.update(root_tree)
                elif self.is_list(root_tree) and final_build:
                    final_build[self.EMPTY_KEY] = root_tree
                else:
                    top_wrapper.append(root_tree)

        self.set_final_build(final_build, top_wrapper)

    def grouped_nested_data(self):
        """
        It groups nested structures of the same kind and namespaces together
        """
        temp, container, data = {}, [], self.validated_data

        for key, value in data.items():
            if self.str_is_namespaced(key):
                if self.key_is_last(key, data, 'namespace'):
                    temp.setdefault(key, value)
                    container.append({self.get_namespace(key): temp})
                    temp = {}
                else:
                    temp.setdefault(key, value)
            elif self.str_is_list(self.split_nested_str(key)[0]):
                if self.key_is_last(key, data, 'list'):
                    temp.setdefault(key, value)
                    container.append({self.EMPTY_KEY: temp})
                    temp = {}
                else:
                    temp.setdefault(key, value)
            elif self.str_is_dict(self.split_nested_str(key)[0]):
                if self.key_is_last(key, data, 'dict'):
                    temp.setdefault(key, value)
                    container.append({self.EMPTY_KEY: temp})
                    temp = {}
                else:
                    temp.setdefault(key, value)
            else:
                if self.key_is_last(key, data):
                    temp.setdefault(key, value)
                    container.append({self.EMPTY_KEY: temp})
                    temp = {}
                else:
                    temp.setdefault(key, value)

        return self.merger(container)

    def merger(self, grouped_data):
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
                        data_value = next(iter(data.values()))

                        map_value.update(data_value)
                        break
            else:
                merged_map.append(data)

        return merged_map

    def set_final_build(self, final_build, top_wrapper):
        """
        Set the final build
        """
        if final_build:
            top_wrapper.append(final_build)

        if len(top_wrapper) == 1:
            self._final_data = top_wrapper[0]
        elif len(top_wrapper) > 1:
            self._final_data = top_wrapper
        else:
            raise ParseException('unexpected empty container')

    def decode(self, nested_data):
        """
        Trys to Convert nested data to an object containing primitives
        """
        root_tree = None

        ############# initialize the root_tree ###################
        if root_tree is None:
            key = list(nested_data.keys())[0]
            root_tree = self.get_container(key)
        #########################################################

        for key, value in nested_data.items():
            value = self.replace_specials(value)

            if self.str_is_nested(key):
                key = self.strip_namespace(key)
                value = self.clean_value(value)

                self.build_object(key, value, root_tree)
            else:
                # the root tree is automatically a dict
                root_tree.setdefault(key, value)

        return root_tree

    def build_root(self, root, context):
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

    def build_step_structure(self, root, context, depth=0):
        """
        Insert and updates the root tree according to the context passed as
        argument
        """
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
                    self.build_root(root, context)
            except (KeyError, IndexError):
                self.build_root(root, context)
        else:
            # if not depth of interest unpack the root object with keys
            # provided by context['keys']
            key = context['keys'][depth]
            self.build_step_structure(root[key], context, depth=depth + 1)

    def get_index(self, key):
        """
        Get the nested sub key index
        """
        if self.str_is_dict(key):
            return self.strip_bracket(key)
        elif self.str_is_empty_list(key):
            # an empty list always has it index as '0'
            # unless the key is repeated, then it will
            # have an array of values attached to the same key
            return 0

        return self.extract_index(key)

    def get_value(self, depth, steps, value):
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

    def get_index_keys(self, depth, index_keys, steps):
        """
        Get and store all the index keys for the nested key
        """
        prev_depth = depth - 1

        if prev_depth >= 0:
            index_keys.append(self.get_index(steps[prev_depth]))
            return index_keys

        return index_keys

    def build_object(self, nested_key, value, root_tree):
        """
        Build the data structure for a nested key and insert value
        """
        steps = self.split_nested_str(nested_key)
        steps_index_keys = []

        for depth, step in enumerate(steps):
            self.build_step_structure(root_tree, {
                'depth': depth,
                'index': self.get_index(step),
                'value': self.get_value(depth, steps, value),
                'keys': self.get_index_keys(depth, steps_index_keys, steps)
            })
