"""
Module for sedes objects that use lists as serialization format.
"""
from collections import Sequence

from eth_utils import (
    to_list,
    to_tuple,
)

from rlp.exceptions import (
    SerializationError,
    ListSerializationError,
    DeserializationError,
    ListDeserializationError,
    RLPException,
)

from .binary import (
    Binary as BinaryClass,
)


def is_sedes(obj):
    """Check if `obj` is a sedes object.

    A sedes object is characterized by having the methods `serialize(obj)` and
    `deserialize(serial)`.
    """
    return hasattr(obj, 'serialize') and hasattr(obj, 'deserialize')


def is_sequence(obj):
    """Check if `obj` is a sequence, but not a string or bytes."""
    return isinstance(obj, Sequence) and not (
        isinstance(obj, str) or BinaryClass.is_valid_type(obj))


class List(list):

    """A sedes for lists, implemented as a list of other sedes objects.

    :param strict: If true (de)serializing lists that have a length not
                   matching the sedes length will result in an error. If false
                   (de)serialization will stop as soon as either one of the
                   lists runs out of elements.

    :param has_serializable_children: Set to true if any children in the list are serializable.
                                      Otherwise, it won't try to serialize any children.
    """

    def __init__(self, elements=None, strict=True, has_serializable_children = True):
        super(List, self).__init__()
        self.strict = strict
        self.has_serializable_children = has_serializable_children

        if len(elements) < 2:
            raise RLPException("List needs at least 2 elements")

        if elements:
            for e in elements:
                if is_sedes(e):
                    self.append(e)
                elif isinstance(e, Sequence):
                    self.append(List(e))
                else:
                    raise TypeError(
                        'Instances of List must only contain sedes objects or '
                        'nested sequences thereof.'
                    )

    def get_sede_identifier(self):
        inner_list = []
        for sede in self:
            inner_list.append(sede.get_sede_identifier())
        return inner_list


    # @to_list
    # def serialize(self, obj):
    #     if self.validate and not is_sequence(obj):
    #         raise ListSerializationError('Can only serialize sequences', obj)
    #     if self.strict:
    #         if len(self) != len(obj) or len(self) < len(obj):
    #             raise ListSerializationError('List has wrong length', obj)
    #
    #     for index, (element, sedes) in enumerate(zip(obj, self)):
    #         try:
    #             yield sedes.serialize(element)
    #         except SerializationError as e:
    #             raise ListSerializationError(obj=obj, element_exception=e, index=index)
    #
    # @to_tuple
    # def deserialize(self, serial):
    #     if self.validate and not is_sequence(serial):
    #         raise ListDeserializationError('Can only deserialize sequences', serial)
    #
    #     if self.strict and len(serial) != len(self):
    #         raise ListDeserializationError('List has wrong length', serial)
    #
    #     for idx, (sedes, element) in enumerate(zip(self, serial)):
    #         try:
    #             yield sedes.deserialize(element)
    #         except DeserializationError as e:
    #             raise ListDeserializationError(serial=serial, element_exception=e, index=idx)

    @to_list
    def serialize_to_list(self, obj):
        for index, (element, sedes) in enumerate(zip(obj, self)):
            try:
                yield sedes.serialize(element)
            except SerializationError as e:
                raise ListSerializationError(obj=obj, element_exception=e, index=index)

    def serialize(self, obj):
        if self.has_serializable_children:
            return self.serialize_to_list(obj)
        else:
            return obj

    @to_tuple
    def deserialize_to_tuple(self, serial):
        for idx, (sedes, element) in enumerate(zip(self, serial)):
            try:
                yield sedes.deserialize(element)
            except DeserializationError as e:
                raise ListDeserializationError(serial=serial, element_exception=e, index=idx)

    def deserialize(self, serial):
        if self.has_serializable_children:
            return self.deserialize_to_tuple(serial)
        else:
            return serial

def FList(elements):
    return List(elements, has_serializable_children = False)

class CountableList(object):

    """A sedes for lists of arbitrary length.

    :param element_sedes: when (de-)serializing a list, this sedes will be
                          applied to all of its elements
    :param max_length: maximum number of allowed elements, or `None` for no limit
    """

    def __init__(self, element_sedes, has_serializable_children = True):

        self.element_sedes = element_sedes
        self.has_serializable_children = has_serializable_children

    def get_sede_identifier(self):
        return [self.element_sedes.get_sede_identifier()]
        # if(!isinstance(self.element_sedes), list)
        # if len(self.element_sedes) == 0:
        #     return [];
        # elif len(self.element_sedes) == 1:
        #     return [self[0].get_sede_identifier()]
        # else:
        #     inner_list = []
        #     for sede in self.element_sedes:
        #         inner_list.append(sede.get_sede_identifier())
        #     return [inner_list]

    # @to_list
    # def serialize(self, obj):
    #     if self.validate and not is_sequence(obj):
    #         raise ListSerializationError('Can only serialize sequences', obj)
    #
    #     if self.max_length is not None and len(obj) > self.max_length:
    #         raise ListSerializationError(
    #             'Too many elements ({}, allowed {})'.format(
    #                 len(obj),
    #                 self.max_length,
    #             ),
    #             obj=obj,
    #         )
    #
    #     for index, element in enumerate(obj):
    #         try:
    #             yield self.element_sedes.serialize(element)
    #         except SerializationError as e:
    #             raise ListSerializationError(obj=obj, element_exception=e, index=index)
    #
    # @to_tuple
    # def deserialize(self, serial):
    #     if self.validate and not is_sequence(serial):
    #         raise ListDeserializationError('Can only deserialize sequences', serial=serial)
    #     for index, element in enumerate(serial):
    #         if self.max_length is not None and index >= self.max_length:
    #             raise ListDeserializationError(
    #                 'Too many elements (more than {})'.format(self.max_length),
    #                 serial=serial,
    #             )
    #
    #         try:
    #             yield self.element_sedes.deserialize(element)
    #         except DeserializationError as e:
    #             raise ListDeserializationError(serial=serial, element_exception=e, index=index)

    @to_list
    def serialize_to_list(self, obj):
        for index, element in enumerate(obj):
            try:
                yield self.element_sedes.serialize(element)
            except SerializationError as e:
                raise ListSerializationError(obj=obj, element_exception=e, index=index)

    @to_tuple
    def deserialize_to_tuple(self, serial):
        for index, element in enumerate(serial):
            try:
                yield self.element_sedes.deserialize(element)
            except DeserializationError as e:
                raise ListDeserializationError(serial=serial, element_exception=e, index=index)

    def serialize(self, obj):
        if self.has_serializable_children:
            return self.serialize_to_list(obj)
        else:
            return obj

    def deserialize(self, serial):
        if self.has_serializable_children:
            return self.deserialize_to_tuple(serial)
        else:
            return serial

def FCountableList(elements):
    return CountableList(elements, has_serializable_children = False)