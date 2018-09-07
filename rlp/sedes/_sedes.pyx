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

from cpython.bytes cimport (
    PyBytes_AsString,
    PyBytes_FromStringAndSize,
    PyBytes_Size,
    PyBytes_Check,
)
from cpython.buffer cimport (
    Py_buffer,
    PyObject_CheckBuffer,
    PyObject_GetBuffer,
    PyBuffer_Release,
    PyBuffer_IsContiguous,
    PyBUF_READ,
    PyBUF_SIMPLE,
    PyBUF_FULL_RO,
)
from cpython.mem cimport PyMem_Malloc, PyMem_Free
from cpython.object cimport PyCallable_Check
from cpython.ref cimport Py_DECREF
from cpython.exc cimport PyErr_WarnEx

cdef extern from "Python.h":

    int PyMemoryView_Check(object obj)
    int PyByteArray_Check(object obj)
    int PyByteArray_CheckExact(object obj)
    #int PyInt_Check(object obj)
    object PyBytes_FromObject(object obj)
    object PyBytes_FromFormat(const char *format)
    char* PyUnicode_AsUTF8AndSize(object obj, Py_ssize_t *l) except NULL

    ctypedef struct PyObject
    ctypedef PY_LONG_LONG
    cdef int PyObject_AsReadBuffer(object o, const void** buff, Py_ssize_t* buf_len) except -1
    object PyMemoryView_GetContiguous(object obj, int buffertype, char order)
    object PyLong_FromString(char* str, char** pend, int base)

cdef extern from "sedes.h":
    struct sede_packer:
        char* buf
        size_t length
        size_t buf_size

    int sede_pack_int_to_big_endian(sede_packer* x, unsigned long long input)
    int sede_pack_add_left_padding(sede_packer* x, size_t l)
    unsigned long long _msgpack_load16_wrapper(void* p)


cdef int DEFAULT_RECURSE_LIMIT=511
#from https://github.com/ethereum/wiki/wiki/RLP
cdef unsigned long long ITEM_LIMIT = (2**64)-1

cdef inline int PyBytesLike_Check(object o):
    return PyBytes_Check(o) or PyByteArray_Check(o)



cdef class BigEndianInt(object):
    """
    cython big endian int sede

    """
    cdef int l
    cdef sede_packer pk
    cdef bint autoreset

    def __cinit__(self):
        cdef int buf_size = 1024*1024
        self.pk.buf = <char*> PyMem_Malloc(buf_size)
        if self.pk.buf == NULL:
            raise MemoryError("Unable to allocate internal buffer.")
        self.pk.buf_size = buf_size
        self.pk.length = 0

    def __init__(self, l=0, bint autoreset=True):
        self.l = l
        self.autoreset = autoreset


    cpdef serialize(self, object obj):
        cdef int ret

        if PyInt_Check(obj):
            if obj < 0:
                raise SerializationError('Cannot serialize negative integers', obj)

            if obj < ITEM_LIMIT:
                #print("doing the fast way")
                try:
                    ret = self._serialize(obj)
                except:
                    self.pk.length = 0
                    raise
                if ret:  # should not happen.
                    if ret == 4:
                        raise SerializationError('Cannot serialize negative integers', obj)

                    if ret == 5:
                        raise SerializationError('Integer too large (does not fit in {} '
                                                 'bytes)'.format(self.l), obj)
                    else:
                        raise RuntimeError("internal error")
                        print(ret)

                buf = PyBytes_FromStringAndSize(self.pk.buf, self.pk.length)

                if self.autoreset:
                    self.pk.length = 0

                return buf


            else:
                if self.l != 0 and obj >= 256 ** self.l:
                    raise SerializationError('Integer too large (does not fit in {} '
                                             'bytes)'.format(self.l), obj)


                #print("doing the slow python way")
                if obj == 0:
                    s = b''
                else:
                    s = int_to_big_endian(obj)

                if self.l is not None:
                    return b'\x00' * max(0, self.l - len(s)) + s
                else:
                    return s

        else:
            raise SerializationError('Can only serialize integers', obj)



    cdef int _serialize(self, object obj):
        #this function is called after it checks that obj is an int. so it is now an int

        cdef unsigned long long num

        num = obj
        ret = sede_pack_int_to_big_endian(&self.pk, num)

        if ret != 0:
            return ret

        if self.l != 0:
            ret = sede_pack_add_left_padding(&self.pk, self.l)

        return ret



    def deserialize(self, serial):
        if self.l is not 0 and len(serial) != self.l:
            raise DeserializationError('Invalid serialization (wrong size)',
                                       serial)
        if self.l is 0 and len(serial) > 0 and serial[0:1] == b'\x00':
            raise DeserializationError('Invalid serialization (not minimal '
                                       'length)', serial)

        serial = serial or b'\x00'
        return big_endian_to_int(serial)

