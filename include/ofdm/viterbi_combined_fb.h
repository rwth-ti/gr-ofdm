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

#ifndef INCLUDED_OFDM_VITERBI_COMBINED_FB_H
#define INCLUDED_OFDM_VITERBI_COMBINED_FB_H

#include <ofdm/api.h>
#include <gnuradio/block.h>

#include <ofdm/calc_metric.h>
#include <ofdm/fsm.h>

namespace gr {
  namespace ofdm {

    /*!
     * \brief <+description of block+>
     * \ingroup ofdm
     *
     */
    class OFDM_API viterbi_combined_fb : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<viterbi_combined_fb> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of ofdm::viterbi_combined_fb.
       *
       * To avoid accidental use of raw pointers, ofdm::viterbi_combined_fb's
       * constructor is in a private implementation
       * class. ofdm::viterbi_combined_fb::make is the public interface for
       * creating new instances.
       */
      static sptr make(const fsm &FSM, int K, int S0, int SK, int D, int chunkdivisor, const std::vector<float> &TABLE, ofdm::ofdm_metric_type_t TYPE);

      virtual fsm FSM() const = 0;
      virtual int K() const = 0;
      virtual int S0() const = 0;
      virtual int SK() const = 0;
      virtual int D() const = 0;
	  virtual std::vector<float> TABLE () const = 0;
	  virtual ofdm::ofdm_metric_type_t TYPE () const = 0;
		//std::vector<int> trace () const { return d_trace; }
	  virtual void set_TABLE (const std::vector<float> &table) = 0;
	  virtual void set_K (int K) = 0;;



    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_VITERBI_COMBINED_FB_H */

