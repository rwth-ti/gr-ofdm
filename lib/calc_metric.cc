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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include <ofdm/calc_metric.h>

#include <float.h>
#include <stdexcept>

namespace gr {
  namespace ofdm {

  template <class T>
  void calc_metric(int O, int D, const std::vector<T> &TABLE, const T *in, float *metric, ofdm::ofdm_metric_type_t type)
  {
    float minm = FLT_MAX;
    int minmi = 0;


    switch (type){
    case ofdm::TRELLIS_EUCLIDEAN:
      for(int o=0;o<O;o++) {
        metric[o]=0.0;
        for (int m=0;m<D;m++) {
          T s=in[m]-TABLE[o*D+m];
          //gr_complex sc(1.0*s,0);
          //metric[o]+=(sc*conj(sc)).real();
          metric[o]+= s * s;
        }
      }
      break;
    case ofdm::TRELLIS_HARD_SYMBOL:
      for(int o=0;o<O;o++) {
        metric[o]=0.0;
        for (int m=0;m<D;m++) {
          T s=in[m]-TABLE[o*D+m];
          //gr_complex sc(1.0*s,0);
          //metric[o]+=(sc*conj(sc)).real();
          metric[o]+= s * s;
        }
        if(metric[o]<minm) {
          minm=metric[o];
          minmi=o;
        }
      }
      for(int o=0;o<O;o++) {
        metric[o] = (o==minmi?0.0:1.0);
      }
      break;
    case ofdm::TRELLIS_HARD_BIT:
      throw std::runtime_error ("Invalid metric type (not yet implemented).");
      break;
    default:
      throw std::runtime_error ("Invalid metric type.");
    }
  }



  template
  void calc_metric<short>(int O, int D, const std::vector<short> &TABLE, const short *in, float *metric, ofdm::ofdm_metric_type_t type);

  template
  void calc_metric<int>(int O, int D, const std::vector<int> &TABLE, const int *in, float *metric, ofdm::ofdm_metric_type_t type);

  template
  void calc_metric<float>(int O, int D, const std::vector<float> &TABLE, const float *in, float *metric, ofdm::ofdm_metric_type_t type);


  /*
  void calc_metric(int O, int D, const std::vector<short> &TABLE, const short *in, float *metric, ofdm_metric_type_t type)
  {
    float minm = FLT_MAX;
    int minmi = 0;

    switch (type){
    case TRELLIS_EUCLIDEAN:
      for(int o=0;o<O;o++) {
        metric[o]=0.0;
        for (int m=0;m<D;m++) {
          float s=in[m]-TABLE[o*D+m];
          metric[o]+=s*s;
        }
      }
      break;
    case TRELLIS_HARD_SYMBOL:
      for(int o=0;o<O;o++) {
        metric[o]=0.0;
        for (int m=0;m<D;m++) {
          float s=in[m]-TABLE[o*D+m];
          metric[o]+=s*s;
        }
        if(metric[o]<minm) {
          minm=metric[o];
          minmi=o;
        }
      }
      for(int o=0;o<O;o++) {
        metric[o] = (o==minmi?0.0:1.0);
      }
      break;
    case TRELLIS_HARD_BIT:
      throw std::runtime_error ("Invalid metric type (not yet implemented).");
      break;
    default:
      throw std::runtime_error ("Invalid metric type.");
    }
  }


  void calc_metric(int O, int D, const std::vector<int> &TABLE, const int *in, float *metric, ofdm_metric_type_t type)
  {
    float minm = FLT_MAX;
    int minmi = 0;

    switch (type){
    case TRELLIS_EUCLIDEAN:
      for(int o=0;o<O;o++) {
        metric[o]=0.0;
        for (int m=0;m<D;m++) {
          float s=in[m]-TABLE[o*D+m];
          metric[o]+=s*s;
        }
      }
      break;
    case TRELLIS_HARD_SYMBOL:
      for(int o=0;o<O;o++) {
        metric[o]=0.0;
        for (int m=0;m<D;m++) {
          float s=in[m]-TABLE[o*D+m];
          metric[o]+=s*s;
        }
        if(metric[o]<minm) {
          minm=metric[o];
          minmi=o;
        }
      }
      for(int o=0;o<O;o++) {
        metric[o] = (o==minmi?0.0:1.0);
      }
      break;
    case TRELLIS_HARD_BIT:
      throw std::runtime_error ("Invalid metric type (not yet implemented).");
      break;
    default:
      throw std::runtime_error ("Invalid metric type.");
    }
  }



  void calc_metric(int O, int D, const std::vector<float> &TABLE, const float *in, float *metric, ofdm_metric_type_t type)
  {
    float minm = FLT_MAX;
    int minmi = 0;

    switch (type){
    case TRELLIS_EUCLIDEAN:
      for(int o=0;o<O;o++) {
        metric[o]=0.0;
        for (int m=0;m<D;m++) {
          float s=in[m]-TABLE[o*D+m];
          metric[o]+=s*s;
        }
      }
      break;
    case TRELLIS_HARD_SYMBOL:
      for(int o=0;o<O;o++) {
        metric[o]=0.0;
        for (int m=0;m<D;m++) {
          float s=in[m]-TABLE[o*D+m];
          metric[o]+=s*s;
        }
        if(metric[o]<minm) {
          minm=metric[o];
          minmi=o;
        }
      }
      for(int o=0;o<O;o++) {
        metric[o] = (o==minmi?0.0:1.0);
      }
      break;
    case TRELLIS_HARD_BIT:
      throw std::runtime_error ("Invalid metric type (not yet implemented).");
      break;
    default:
      throw std::runtime_error ("Invalid metric type.");
    }
  }
  */





  void calc_metric(int O, int D, const std::vector<gr_complex> &TABLE, const gr_complex *in, float *metric, ofdm::ofdm_metric_type_t type)
  {
    float minm = FLT_MAX;
    int minmi = 0;


    switch (type){
    case ofdm::TRELLIS_EUCLIDEAN:
      for(int o=0;o<O;o++) {
        metric[o]=0.0;
        for (int m=0;m<D;m++) {
          gr_complex s=in[m]-TABLE[o*D+m];
          metric[o]+=s.real()*s.real()+s.imag()*s.imag();
        }
      }
      break;
    case ofdm::TRELLIS_HARD_SYMBOL:
      for(int o=0;o<O;o++) {
        metric[o]=0.0;
        for (int m=0;m<D;m++) {
          gr_complex s=in[m]-TABLE[o*D+m];
          metric[o]+=s.real()*s.real()+s.imag()*s.imag();
        }
        if(metric[o]<minm) {
          minm=metric[o];
          minmi=o;
        }
      }
      for(int o=0;o<O;o++) {
        metric[o] = (o==minmi?0.0:1.0);
      }
      break;
    case ofdm::TRELLIS_HARD_BIT:
      throw std::runtime_error ("Invalid metric type (not yet implemented).");
      break;
    default:
      throw std::runtime_error ("Invalid metric type.");
    }
  }

  } /* namespace ofdm */
} /* namespace gr */

