#include <stdint.h>
#include <ofdm/util_endian.h>

int16_t twist_int16(int16_t inVar)
{
    int16_t outVar;
    uint8_t* inBField = (uint8_t*) &inVar;
    uint8_t* outBField = (uint8_t*) &outVar;

    outBField[0] = inBField[1];
    outBField[1] = inBField[0];

    return outVar;
}

uint16_t twist_uint16(uint16_t inVar)
{
    uint16_t outVar;
    uint8_t* inBField = (uint8_t*) &inVar;
    uint8_t* outBField = (uint8_t*) &outVar;

    outBField[0] = inBField[1];
    outBField[1] = inBField[0];

    return outVar;
}

int32_t twist_int32(int32_t inVar)
{
    int32_t outVar;
    uint8_t* inBField = (uint8_t*) &inVar;
    uint8_t* outBField = (uint8_t*) &outVar;

    outBField[0] = inBField[3];
    outBField[1] = inBField[2];
    outBField[2] = inBField[1];
    outBField[3] = inBField[0];

    return outVar;
}

uint32_t twist_uint32(uint32_t inVar)
{
    uint32_t outVar;
    uint8_t* inBField = (uint8_t*) &inVar;
    uint8_t* outBField = (uint8_t*) &outVar;

    outBField[0] = inBField[3];
    outBField[1] = inBField[2];
    outBField[2] = inBField[1];
    outBField[3] = inBField[0];

    return outVar;
}

