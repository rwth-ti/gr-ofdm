/*
 * types.h
 *
 *  Created on: 03.12.2008
 *      Author: harries
 */

#ifndef TYPES_H
#define TYPES_H


#include <string>
#include <vector>
#include <complex>
#include "tao_skeleton/ofdm_tiC.h"

//defines several types used in the program

enum DataType {unspecified,
    vector_float,
    vector_int,
    vector_complex,
    scalar_float,
    scalar_int,
    scalar_complex,
    transmission_data,
    rx_performance_values,
    power_strategy,
    scatter_ctrl_data};

enum State {OK,
    ConnectionLoss,
    ServantError};

typedef enum a {SNR,
    CTF,
    SINRPSC,
    TransmissionData,
    power_aloc_scheme,
    rate_aloc_scheme,
    rx_performance,
    rx_bband,
    scatter,
    scatter_control,
    power_control,
    tx_control} IF_Type;

typedef std::complex<float> complexFloat;

struct transmissionData
{
    int subcarriers;
    int fft_window;
    int cp_length;
    float carrier_freq;
    float symbol_time;
    float bandwidth;
    float subbandwidth;
    int max_datarate;
    int burst_length;
};

typedef enum b {margin_adaptive, rate_adaptive, reset_strategy} strategy_type;

struct powercontrol
{
    ofdm_ti::PA_Ctrl::strategy_type strategy;
    float required_ber;
    float constraint;
    float channel_refresh_interval;
    float data_rate;
    int power_val;
    int modulation;
    float freqoff;
};

struct scattercontrol
{
    int subcarrier;
};

struct rx_performance_struct
{
    int station_id;
    float snr;
    float ber;
    float freqoff;
};

struct parameters
{
    std::string nameservice;
    std::string use;
    std::string	port;
    int id;
};

#endif
