from collections.abc import Mapping

from .exceptions import ParseError
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

    def is_nested(self, raise_exception=False):
        """
        Checks if the initial_data map is a nested object
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
            if self.is_nested_string(key):
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
        elif isinstance(value, list) and len(value) == 0 and not self._allow_empty:
            return default
        elif isinstance(value, dict) and len(value) == 0 and not self._allow_empty:
            return default

        return value


# serilizes a nested form data to object
# ---------------------------------------

class NestedForms(BaseClass):
    """
    decode nested forms into python object
    """

    def __process__(self):
        """
        Initiates the conversion process and packages the final data
        """
        data_list, final_build, top_wrapper = self._group_data(), {}, []

        for data in data_list:
            key = list(data.keys())[0]
            value = list(data.values())[0]

            root_tree = self.decode(value)

            if not bool(key):
                if isinstance(root_tree, dict):
                    final_build.update(root_tree)
                elif isinstance(root_tree, list):
                    if final_build:
                        final_build[''] = root_tree
                    else:
                        top_wrapper.append(root_tree)
            else:
                final_build.setdefault(key, root_tree)

        if final_build:
            top_wrapper.append(final_build)

        if len(top_wrapper) == 1:
            self._final_data = top_wrapper[0]
        elif len(top_wrapper) > 1:
            self._final_data = top_wrapper
        else:
            raise ParseError('unexpected empty container')

    def _group_data(self):
        """
        It groups data structures of the same kind and namespaces together
        """
        temp, container, data = {}, [], self.validated_data

        for key, value in data.items():
            if self.is_namespaced(key):
                if self.is_last(key, data, 'N'):
                    temp.setdefault(key, value)
                    container.append({self.get_namespace(key): temp})
                    temp = {}
                else:
                    temp.setdefault(key, value)
            elif self.is_list(self.split(key)[0]):
                if self.is_last(key, data, 'L'):
                    temp.setdefault(key, value)
                    container.append({'': temp})
                    temp = {}
                else:
                    temp.setdefault(key, value)
            elif self.is_dict(self.split(key)[0]):
                if self.is_last(key, data, 'D'):
                    temp.setdefault(key, value)
                    container.append({'': temp})
                    temp = {}
                else:
                    temp.setdefault(key, value)
            else:
                if self.is_last(key, data):
                    temp.setdefault(key, value)
                    container.append({'': temp})
                    temp = {}
                else:
                    temp.setdefault(key, value)

        return container

    def decode(self, validated_data):
        """
        Convert validated_data to an object containing primitives
        """
        self._root_tree = None

        ############# initialize the root_tree ###################

        if self._root_tree is None:
            key = list(validated_data.keys())[0]
            self._root_tree = self.get_container(key)

        #########################################################

        for key, value in validated_data.items():
            if self.is_nested_string(key):
                key = self.strip_namespace(key)
                value = self.replace_specials(value)

                value = self.clean_value(value)
                self.generate_context(key, value, self._root_tree)
            else:
                # the root tree is automatically a dict
                self._root_tree.setdefault(key, value)

        return self._root_tree

    def build(self, root, context, depth=0):
        """
        Insert and updates the root tree according to the context passed as
        argument
        """

        def is_dict(v): return isinstance(v, dict)
        def is_list(v): return isinstance(v, list)

        ######################################################

        def set_root():
            if is_list(root):
                # check the difference between index of the last item in
                # the list and the current index to be added
                diff = abs(len(root) - context['index'])

                if diff > 1000:
                    raise ParseError('too many consecutive empty arrays !')
                elif diff > 1:
                    # if it is sparse
                    # fill gaps with the `None`
                    for _ in range(diff):
                        root.append(None)
                    # append the default value
                    root.append(context['value'])
                elif context['value'] and is_list(context['value']):
                    # if context value is not empty and its a list, transfer
                    # value into the root
                    root.extend(context['value'])
                else:
                    # just append like default
                    root.append(context['value'])
            else:
                root[context['index']] = context['value']

        ######################################################

        if context['depth'] == depth:
            try:
                # check if the root of interest is empty or exist
                value = root[context['index']]
                if value:
                    if is_list(value) and context['value']:
                        value.append(context['value'])
                    elif is_dict(value) and is_dict(context['value']):
                        for key in context['value'].keys():
                            # if the key already exist do nothing
                            if key in value:
                                continue
                            else:
                                # transfer all the value to the root or value
                                value.update(context['value'])
                    else:
                        pass
                else:
                    set_root()
            except (KeyError, IndexError):
                set_root()
        else:
            # if not depth of interest unpack the root object with keys
            # provided by context['keys']
            key = context['keys'][depth]
            self.build(root[key], context, depth=depth + 1)

    def generate_context(self, key, value, root_tree):
        """
        Generates a context for every key
        """
        sub_keys = self.split(key)
        index_keys = []

        def get_index(key):
            if self.is_dict(key):
                return self.strip_bracket(key)
            elif self.is_empty_list(key):
                # an empty list always has it index as '0'
                # unless the key is repeated, then it will
                # have an array of values attached to the same key
                return 0

            return self.extract_index(key)

        def get_value(index):
            if index < len(sub_keys):
                if self.is_dict(sub_keys[index]):
                    # at this time the value of the dict is unknown
                    # so `None` is used
                    return {self.strip_bracket(sub_keys[index]): None}
                else:
                    return []

            return value

        def get_index_keys(index):
            if index >= 0:
                index_keys.append(get_index(sub_keys[index]))
                return index_keys

            return index_keys

        #########################################################

        for i, sub_key in enumerate(sub_keys):

            next_i = i + 1
            prev_i = i - 1

            context = {
                'depth': i,
                'index': get_index(sub_key),
                'value': get_value(next_i),
                'keys': get_index_keys(prev_i)
            }

            self.build(root_tree, context)
