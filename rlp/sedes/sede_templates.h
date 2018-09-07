/*
 * MessagePack packing routine template
 *
 * Copyright (C) 2008-2010 FURUHASHI Sadayuki
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

#include <math.h>

#if defined(__LITTLE_ENDIAN__)
#define TAKE8_8(d)  ((uint8_t*)&d)[0]
#define TAKE8_16(d) ((uint8_t*)&d)[0]
#define TAKE8_32(d) ((uint8_t*)&d)[0]
#define TAKE8_64(d) ((uint8_t*)&d)[0]
#elif defined(__BIG_ENDIAN__)
#define TAKE8_8(d)  ((uint8_t*)&d)[0]
#define TAKE8_16(d) ((uint8_t*)&d)[1]
#define TAKE8_32(d) ((uint8_t*)&d)[3]
#define TAKE8_64(d) ((uint8_t*)&d)[7]
#endif

#ifndef sede_pack_append_buffer
#error sede_pack_append_buffer callback is not defined
#endif

#ifndef sede_pack_insert_buffer
#error sede_pack_insert_buffer callback is not defined
#endif



/*
 * big endian and int
 */


unsigned long long _msgpack_load16_wrapper(void* p)
{
    return _msgpack_load16(uint16_t, p);
}

static inline int sede_pack_int_to_big_endian(sede_packer* x, unsigned long long input)
{
    if ((long long)input < 0)
    {
        return 4;
    }
    //we want no leading zeros
    if(input < 256)
    {
        //1 byte
        unsigned char buf[1] = {(uint8_t)input};
        sede_pack_append_buffer(x, buf, 1);
    }
    else if(input < 65536)
    {
        //2 bytes
        unsigned char buf[2];
        _msgpack_store16(&buf[0], (uint16_t)input);
        sede_pack_append_buffer(x, buf, 2);
    }
    else if(input < 16777216)
    {
        //3 bytes
        unsigned char buf[3];
        unsigned char padded_buf[4];
        _msgpack_store32(&padded_buf[0], (uint32_t)input);

        buf[0] = padded_buf[1];
        buf[1] = padded_buf[2];
        buf[2] = padded_buf[3];
        sede_pack_append_buffer(x, buf, 3);

    }
    else if(input < 4294967296)
    {
        //4 bytes
        unsigned char buf[4];
        _msgpack_store32(&buf[0], (uint32_t)input);
        sede_pack_append_buffer(x, buf, 4);
    }
    else if(input < 1099511627776)
    {
        //5 bytes
        //return input;
        unsigned char buf[5];
        unsigned char padded_buf[8];
        _msgpack_store64(&padded_buf[0], (uint64_t)input);

        buf[0] = padded_buf[3];
        buf[1] = padded_buf[4];
        buf[2] = padded_buf[5];
        buf[3] = padded_buf[6];
        buf[4] = padded_buf[7];

        sede_pack_append_buffer(x, buf, 5);
    }
    else if(input < 281474976710656)
    {
        //6 bytes
        unsigned char buf[6];
        unsigned char padded_buf[8];
        _msgpack_store64(&padded_buf[0], (uint64_t)input);

        buf[0] = padded_buf[2];
        buf[1] = padded_buf[3];
        buf[2] = padded_buf[4];
        buf[3] = padded_buf[5];
        buf[4] = padded_buf[6];
        buf[5] = padded_buf[7];

        sede_pack_append_buffer(x, buf, 6);
    }
    else if(input < 72057594037927936)
    {
        //7 bytes
        unsigned char buf[7];
        unsigned char padded_buf[8];
        _msgpack_store64(&padded_buf[0], (uint64_t)input);

        buf[0] = padded_buf[1];
        buf[1] = padded_buf[2];
        buf[2] = padded_buf[3];
        buf[3] = padded_buf[4];
        buf[4] = padded_buf[5];
        buf[5] = padded_buf[6];
        buf[6] = padded_buf[7];

        sede_pack_append_buffer(x, buf, 7);
    }
    else
    {
        //8 bytes
        unsigned char buf[7];
        _msgpack_store64(&buf[0], (uint64_t)input);

        sede_pack_append_buffer(x, buf, 8);
    }


}

static inline int sede_pack_add_left_padding(sede_packer* x, size_t l)
{
    if(l != 0)
    {
        //return x->length;
        if (((long long)l - (long long)x->length) < 0)
        {
            return 5;
        }
        else if ((l - (long long int)x->length) > 0)
        {
            size_t num_to_add = l - x->length;
            unsigned char buf[num_to_add] = {0x00};
            sede_pack_insert_buffer(x, buf, num_to_add, 0);
        }
    }
}




#undef msgpack_pack_append_buffer

#undef TAKE8_8
#undef TAKE8_16
#undef TAKE8_32
#undef TAKE8_64

#undef msgpack_pack_real_uint8
#undef msgpack_pack_real_uint16
#undef msgpack_pack_real_uint32
#undef msgpack_pack_real_uint64
#undef msgpack_pack_real_int8
#undef msgpack_pack_real_int16
#undef msgpack_pack_real_int32
#undef msgpack_pack_real_int64
