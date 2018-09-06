# /*
#  *
#  *  Parts of this code were taken from msgpack, which has the following licence:
#  * Copyright (C) 2009 Naoki INADA
#  *
#  *    Licensed under the Apache License, Version 2.0 (the "License");
#  *    you may not use this file except in compliance with the License.
#  *    You may obtain a copy of the License at
#  *
#  *        http://www.apache.org/licenses/LICENSE-2.0
#  *
#  *    Unless required by applicable law or agreed to in writing, software
#  *    distributed under the License is distributed on an "AS IS" BASIS,
#  *    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  *    See the License for the specific language governing permissions and
#  *    limitations under the License.
#  */

# coding: utf-8
#cython: embedsignature=True, c_string_encoding=ascii

from cpython cimport *
from cpython.version cimport PY_MAJOR_VERSION
from cpython.exc cimport PyErr_WarnEx

from rlp.exceptions import DeserializationError, SerializationError

from eth_utils import (
    int_to_big_endian,
    big_endian_to_int,
)

cdef extern from "Python.h":

    int PyMemoryView_Check(object obj)
    int PyByteArray_Check(object obj)
    int PyByteArray_CheckExact(object obj)
    #int PyInt_Check(object obj)
    object PyBytes_FromObject(object obj)
    object PyBytes_FromFormat(const char *format)
    char* PyUnicode_AsUTF8AndSize(object obj, Py_ssize_t *l) except NULL


cdef extern from "sedes.h":
    struct sede_packer:
        char* buf
        size_t length
        size_t buf_size

cdef int DEFAULT_RECURSE_LIMIT=511
#from https://github.com/ethereum/wiki/wiki/RLP
cdef unsigned long long ITEM_LIMIT = (2**64)-1



cdef class BigEndianInt(object):
    """
    cython big endian int sede

    """
    cdef int l
    cdef sede_packer pk
    cdef char* number

    def __cinit__(self):
        cdef int buf_size = 1024*1024
        self.pk.buf = <char*> PyMem_Malloc(buf_size)
        if self.pk.buf == NULL:
            raise MemoryError("Unable to allocate internal buffer.")
        self.pk.buf_size = buf_size
        self.pk.length = 0

    def __init__(self, l=0):
        self.l = l

    cpdef serialize(self, object obj):
        return self._serialize(obj)

    cdef _serialize(self, object obj):
        if PyInt_Check(obj):
            if self.l != 0 and obj >= 256 ** self.l:
                raise SerializationError('Integer too large (does not fit in {} '
                                         'bytes)'.format(self.l), obj)
            if obj < 0:
                raise SerializationError('Cannot serialize negative integers', obj)

            #self.number = <char*>obj
            return PyBytes_FromFormat

        else:
            raise SerializationError('Can only serialize integers', obj)

        #
        #
        #
        # if obj == 0:
        #     s = b''
        # else:
        #     s = int_to_big_endian(obj)
        #
        # if self.l is not None:
        #     return b'\x00' * max(0, self.l - len(s)) + s
        # else:
        #     return s

    def deserialize(self, serial):
        if self.l is not None and len(serial) != self.l:
            raise DeserializationError('Invalid serialization (wrong size)',
                                       serial)
        if self.l is None and len(serial) > 0 and serial[0:1] == b'\x00':
            raise DeserializationError('Invalid serialization (not minimal '
                                       'length)', serial)

        serial = serial or b'\x00'
        return big_endian_to_int(serial)
