#ifndef _ENDIAN_CONVERSION_H
#define _ENDIAN_CONVERSION_H

#include <stdint.h>
#include <sys/param.h>

#ifdef __BYTE_ORDER

#if __BYTE_ORDER == __LITTLE_ENDIAN
#define HO_LE
#else
#if __BYTE_ORDER == __BIG_ENDIAN
#define HO_BE
#endif /*__BYTE_ORDER == __BIG_ENDIAN*/
#endif /*__BYTE_ORDER == __LITTLE_ENDIAN*/

#endif /*__BYTE_ORDER*/

#ifdef HO_BE

int16_t twist_int16(int16_t inVar);
uint16_t twist_uint16(uint16_t inVar);
int32_t twist_int32(int32_t inVar);
uint32_t twist_uint32(uint32_t inVar);

int16_t leth_int16(int16_t inVar)
{
    return twist_int16(inVar);
}
uint16_t leth_uint16(uint16_t inVar)
{
    return twist_uint16(inVar);
}
int32_t leth_int32(int32_t inVar)
{
    return twist_int32(inVar);
}
uint32_t leth_uint32(uint32_t inVar)
{
    return twist_uint32(inVar);
}

int16_t htle_int16(int16_t inVar)
{
    return twist_int16(inVar);
}
uint16_t htle_uint16(uint16_t inVar)
{
    return twist_uint16(inVar);
}
int32_t htle_int32(int32_t inVar)
{
    return twist_int32(inVar);
}
uint32_t htle_uint32(uint32_t inVar)
{
    return twist_uint32(inVar);
}

#else
#define leth_int16(a) (a);
#define leth_uint16(a) (a);
#define leth_int32(a) (a);
#define leth_uint32(a) (a);


#define htle_int16(a) (a);
#define htle_uint16(a) (a);
#define htle_int32(a) (a);
#define htle_uint32(a) (a);


#endif /*HO_BE*/

#endif /*_ENDIAN_CONVERSION_H*/
