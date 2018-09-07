/*
 *
 *  Parts of this code were taken from msgpack, which has the following licence:
 * Copyright (C) 2009 Naoki INADA
 *
 *    Licensed under the Apache License, Version 2.0 (the "License");
 *    you may not use this file except in compliance with the License.
 *    You may obtain a copy of the License at
 *
 *        http://www.apache.org/licenses/LICENSE-2.0
 *
 *    Unless required by applicable law or agreed to in writing, software
 *    distributed under the License is distributed on an "AS IS" BASIS,
 *    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *    See the License for the specific language governing permissions and
 *    limitations under the License.
 */

#include <stddef.h>
#include <stdlib.h>
#include "sysdep.h"
#include <limits.h>
#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif


#ifdef _MSC_VER
#define inline __inline
#endif

typedef struct sede_packer {
    char *buf;
    size_t length;
    size_t buf_size;
} sede_packer;

typedef struct Packer Packer;

static inline int sede_pack_write(sede_packer* pk, const char *data, size_t l)
{
    char* buf = pk->buf;
    size_t bs = pk->buf_size;
    size_t len = pk->length;

    if (len + l > bs) {
        bs = (len + l) * 2;
        buf = (char*)PyMem_Realloc(buf, bs);
        if (!buf) {
            PyErr_NoMemory();
            return -1;
        }
    }
    memcpy(buf + len, data, l);
    len += l;

    pk->buf = buf;
    pk->buf_size = bs;
    pk->length = len;
    return 0;
}

//
// overwrites some bytes at a given position
//
static inline int sede_pack_insert_at_position(sede_packer* pk, const char *data, size_t l, size_t position)
{
    char* buf = pk->buf;
    size_t bs = pk->buf_size;
    size_t len = pk->length;

    //First we have to extend it by length
    if (len + l > bs) {
        bs = (len + l) * 2;
        buf = (char*)PyMem_Realloc(buf, bs);
        if (!buf) {
            PyErr_NoMemory();
            return -1;
        }
    }

    memcpy(buf + position + l, buf + position, len-position);

    //now there is a gap of length l at position, ready to be written to

    memcpy(buf + position, data, l);

    len += l;

    pk->buf = buf;
    pk->buf_size = bs;
    pk->length = len;
    return 0;
}

#define sede_pack_append_buffer(user, buf, len) \
        return sede_pack_write(user, (const char*)buf, len)

#define sede_pack_insert_buffer(user, buf, len, position) \
        return sede_pack_insert_at_position(user, (const char*)buf, len, position)

#include "sede_templates.h"

#ifdef __cplusplus
}
#endif
