"""
Utilty class for the nested forms and a base class
for extension
"""
from collections.abc import Mapping

from .exceptions import ParseError
from .mixins import UtilityMixin
from .helpers import is_dict, is_list


# Base class for converting nested form data to objects
# ---------------------------------------------------------

class NestedFormBaseClass(UtilityMixin):
    """
    Base nested form class
    """

    def __init__(self, data, **kwargs):
        self._initial_data = self.__setdata__(data)
        self._allow_empty = kwargs.get('allow_empty', False)
        self._allow_blank = kwargs.get('allow_blank', True)

    def __run__(self):
        if not hasattr(self, '_final_data'):
            self._process()

    def __setdata__(self, data):
        """
        Check if data is a MultiValueDIct and 
        convert it to a dict object else return data
        """
        if hasattr(data, 'getlist'):
            _data = {}

            for key, value in dict(data).items():
                if len(value) > 1:
                    _data.setdefault(key, value)
                else:
                    _data.setdefault(key, value[0])

            return _data

        return data
              
    @property
    def data(self):
        """
        Returns the final build
        """
        if not hasattr(self, "_final_data"):
            msg = '`.is_nested()` has to be called before accessing `.data`'
            raise AssertionError(msg)

        return self._final_data

    def _process(self):
        raise NotImplementedError('`_process()` is not implemented')

    def _clean_value(self, value, default=None):
        """
        Replace empty list, dict and empty string with `None`
        """
        if value == '' and not self._allow_blank:
            return default
        elif is_list(value) and not value and not self._allow_empty:
            return default
        elif is_dict(value) and not value and not self._allow_empty:
            return default

        return value

    def is_nested(self, raise_exception=False):
        """
        Checks if the initial data map is a nested object
        """
        is_mapping = isinstance(self._initial_data, Mapping)
        conditions = [is_mapping]

        #############################################################
        # If "is_mapping" is False, code "self._initial_data.keys()"
        # will raise an AttributeError and in result request method
        # will receive an empty QueryDict, instead of parsed data
        # (even if the data could be parsed by another parser in DRF
        # DEFAULT_PARSER_CLASSES!)
        #
        # Example: exception is raised for self._initial_data == [
        #   {
        #       "field1": 1,
        #       "field2": 2
        #   }
        # ]
        #
        if not is_mapping:
            if raise_exception:
                raise ValueError('`data` is not a map type')
            return False
        #############################################################

        matched_keys = [
            self.str_is_nested(key)
            for key in self._initial_data.keys()
        ]

        conditions += [any(matched_keys)]

        #############################################################
        if not any(matched_keys) and raise_exception:
            raise ValueError('`data` is not a nested type')
        #############################################################

        if all(conditions):
            self._validated_data = self._initial_data
            self.__run__()

        return all(conditions)


# converts a nested form data to object
# ---------------------------------------

class NestedForm(NestedFormBaseClass):
    """
    Decode nested forms into python object
    """
    EMPTY_KEY = ''

    def _process(self):
        """
        Initiates the conversion process
        """
        self._final_data = self._get_root_tree(self._validated_data)

    def _grouped_nested_data(self, validated_data):
        """
        Groups nested data based on their type example `namespaced` `list`
        `dict` and `non-nested`
        """
        group, nested_keys = [], list(validated_data.keys())

        def get_key(key):
            if self.str_is_namespaced(key):
                return self.get_namespace(key)

            return self.EMPTY_KEY

        while nested_keys:
            first_key = nested_keys[0]
            other_keys = []
            temporary_map = {}

            for key in nested_keys:
                if self.type_of(key) == self.type_of(first_key):
                    value = validated_data[key]
                    key = self.strip_namespace(key)

                    temporary_map.setdefault(key, value)
                else:
                    other_keys.append(key)

            group.append({get_key(first_key): temporary_map})
            nested_keys = other_keys

        return group

    def _get_root_tree(self, validated_data):
        """
        Gets the final build
        """
        groups = self._grouped_nested_data(validated_data)
        root_tree = self.get_tree(validated_data.keys())

        for group in groups:
            group_key = next(iter(group.keys()))
            group_value = next(iter(group.values()))

            group_tree = self._decode(group_value)

            if is_dict(root_tree):
                if group_key:
                    root_tree.setdefault(group_key, group_tree)
                elif is_dict(group_tree):
                    root_tree.update(group_tree)
                else:
                    root_tree[self.EMPTY_KEY] = group_tree
            else:
                root_tree.extend(group_tree)

        return root_tree

    def _decode(self, nested_data):
        """
        Trys to convert nested data to an object containing primitives
        """
        tree = self.get_tree(nested_data.keys(), use_first_key=True)

        for key, value in nested_data.items():
            value = self._clean_value(self.replace_special(value))

            if self.str_is_nested(key):
                self._build_tree(key, value, tree)
            else:
                # the tree tree is automatically a dict
                tree.setdefault(key, value)

        return tree

    def _build_tree(self, nested_key, value, tree):
        """
        Build the tree for a nested key and insert value
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
            self._build_step_structure(tree, {
                'depth': depth,
                'index': self.get_index(step),
                'value': get_value(depth),
                'keys': get_index_keys(depth)
            })

    def _build_step_structure(self, tree, context, depth=0):
        """
        Insert and updates the tree according to the context passed as
        argument
        """
        ############################################################################
        def create_tree(tree, context):
            if is_list(tree):
                index = abs(len(tree) - context['index'])

                if index > 1000:
                    raise ParseError('too many consecutive empty arrays !')
                elif index > 1 and index <= 1000:
                    # if it is sparse fill gaps with the `None`
                    # followed by the default value
                    tree += [None] * index
                    tree.append(context['value'])
                elif context['value'] and is_list(context['value']):
                    tree.extend(context['value'])
                else:
                    tree.append(context['value'])
            else:
                tree[context['index']] = context['value']
        ###############################################################################

        while context['depth'] != depth:
            tree = tree[context['keys'][depth]]
            depth += 1

        try:
            inner_tree = tree[context['index']]

            if inner_tree:
                if is_list(inner_tree) and context['value']:
                    inner_tree.append(context['value'])
                elif is_dict(inner_tree) and is_dict(context['value']):
                    key = next(iter(context['value'].keys()))

                    if key not in inner_tree:
                        inner_tree.update(context['value'])
            else:
                create_tree(tree, context)
        except (KeyError, IndexError):
            create_tree(tree, context)
