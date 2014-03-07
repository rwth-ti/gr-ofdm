/* -*- c++ -*- */
/* 
 * Copyright 2014 Institute for Theoretical Information Technology,
 *                RWTH Aachen University
 *                www.ti.rwth-aachen.de
 * 
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifndef INCLUDED_OFDM_CALC_METRIC_H
#define INCLUDED_OFDM_CALC_METRIC_H

#include <ofdm/api.h>
#include <ofdm/ofdm_metric_type.h>

namespace gr {
  namespace ofdm {

  template <class T>
  void OFDM_API calc_metric(int O, int D, const std::vector<T> &TABLE, const T *in, float *metric, ofdm::ofdm_metric_type_t type);

  /*
  void calc_metric(int O, int D, const std::vector<short> &TABLE, const short *in, float *metric, ofdm_metric_type_t type);

  void calc_metric(int O, int D, const std::vector<int> &TABLE, const int *in, float *metric, ofdm_metric_type_t type);

  void calc_metric(int O, int D, const std::vector<float> &TABLE, const float *in, float *metric, ofdm_metric_type_t type);
  */

  void OFDM_API calc_metric(int O, int D, const std::vector<gr_complex> &TABLE, const gr_complex *in, float *metric, ofdm::ofdm_metric_type_t type);


  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_CALC_METRIC_H */

