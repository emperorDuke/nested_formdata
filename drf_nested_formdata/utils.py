import re

from collections.abc import Mapping

from .exception import ParseError

from .mixins import UtilityMixin


# Base serilizer for converting nested formdata to objects
#----------------------------------------------------------

class Base(UtilityMixin):

    def __init__(self, data, *args, **kwargs):
        self._initial_data = data
        self._allow_empty = kwargs.get('allow_empty', False)
        self._allow_blank = kwargs.get('allow_blank', True)

    def __run__(self):
        if not hasattr(self, '_has_ran'):
            self.process()
            setattr(self, '_has_ran', True)

    def __create_raw_data__(self, data):
        raw_data = {}

        for key, value in dict(data).items():
            if len(value) > 1:
                raw_data[key] = value
            else:
                raw_data[key] = value[0]

        self._initial_data = raw_data

    @property
    def data(self): 
        """
        Returns the final build
        """
        if not hasattr(self, '_final_data'):
            msg = '`.is_valid()` has to be called before accessing `.data`'
            raise AssertionError(msg)
        
        return self._final_data

    @property
    def validated_data(self):
        if not hasattr(self, '_validated_data'):
            msg = '`.is_valid()` has to be called before accessing `.data`'
            raise AssertionError(msg)

        return self._validated_data

    def serialize(self, validated_data):
        raise NotImplementedError('`serializer()` is not implemented')


    def is_valid(self, raise_exception=False):
        """
        Checks if the initial_data data is a dict and a nested object
        """

        if hasattr(self._initial_data, 'getlist'):
            # if true then it is a QueryDict
            self.__create_raw_data__(self._initial_data)

        conditions = [isinstance(self._initial_data, Mapping)]

        if not isinstance(self._initial_data, Mapping):
            msg = '`data` is not a map type'
            if raise_exception: raise ValueError(msg)
        else:
            matched_keys = [
                bool(self.is_nested(key)) 
                for key in self._initial_data.keys()
                ]

            conditions.append(any(matched_keys))

            if not any(matched_keys):
                msg = '`data` is not a nested type'
                if raise_exception: raise ValueError(msg)
            else:
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
#--------------------------------------- 

class NestedFormDataSerializer(Base):
    """
    Serialize a nested form-data object into its primitive data structure
    """
    def __init__(self, data, *args, **kwargs):
        super().__init__(data, *args, **kwargs) 

    def process(self):
        """
        Initiates the conversion process and packages the final data
        """
        data_list, build, top = self.pre_process_data(), {}, []

        for data in data_list:
            key = list(data.keys())[0]
            value = list(data.values())[0]
            
            root_tree = self.serialize(value)
        
            if not bool(key):
                # although it support having different data structure
                # it is not recommended.
                if isinstance(root_tree, dict):
                    build.update(root_tree)
                elif isinstance(root_tree, list):
                    if build:
                        build[''] = root_tree
                    else:
                        top.append(root_tree)
            else:
                build.setdefault(key, root_tree)
                
        if build: top.append(build)

        if len(top) == 1:
            setattr(self, '_final_data', top[0])
        elif len(top) > 1:
            setattr(self, '_final_data', top)
        else:
            raise ParseError('unexpected empty container')


    def serialize(self, validated_data):
        """
        Convert validated_data to an object containing primitives
        """
        self._root_tree = None

        ############# initialize the root_tree ###################

        key = list(validated_data.keys())[0]

        if self._root_tree is None:
            if self.is_nested(key):
                key = self.strip_namespace(key)
                self._root_tree = self.get_container(key)
            else:
                self._root_tree = {}

        #########################################################

        for key, value in validated_data.items():
            if self.is_nested(key):
                key = self.strip_namespace(key)
                value = self.replace_specials(value)
                
                value = self.clean_value(value)
                self.generate_context(key, value, self._root_tree)
            else:
                # the root tree is automatically a dict
                self._root_tree.setdefault(key, value)
                
        return self._root_tree        


    def generate_structure(self, root, context, depth=0):
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
                                return
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
            self.generate_structure(root[key], context, depth=depth + 1)


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
                return 0
            
            return self.extract_index(key)

        def get_value(index):
            if index < len(sub_keys):
                if self.is_dict(sub_keys[index]):
                    return { self.strip_bracket(sub_keys[index]): None }
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

            self.generate_structure(root_tree, context)


    def pre_process_data(self):
        temp, container, data = {}, [], self.validated_data

        for key, value in data.items():
            if self.is_namespaced(key):
                if self.is_last(key, data, 'N'):
                    temp.setdefault(key, value) 
                    container.append({ self.get_namespace(key): temp })
                    temp = {}
                else:
                    temp.setdefault(key, value) 
            elif self.is_list(self.split(key)[0]):
                if self.is_last(key, data, 'L'):
                    temp.setdefault(key, value) 
                    container.append({ '': temp })
                    temp = {}
                else:
                    temp.setdefault(key, value)
            elif self.is_dict(self.split(key)[0]):
                if self.is_last(key, data, 'D'):
                    temp.setdefault(key, value) 
                    container.append({ '': temp })
                    temp = {}
                else:
                    temp.setdefault(key, value)
            else:
                temp.setdefault(key, value)
            
        if temp: container.append({ '': temp })

        return container
