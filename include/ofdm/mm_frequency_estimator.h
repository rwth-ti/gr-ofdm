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

#ifndef INCLUDED_OFDM_MM_FREQUENCY_ESTIMATOR_H
#define INCLUDED_OFDM_MM_FREQUENCY_ESTIMATOR_H

#include <ofdm/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
  namespace ofdm {

    /*!
     * \brief <+description of block+>
     * \ingroup ofdm
     *
     */
    class OFDM_API mm_frequency_estimator : virtual public gr::sync_block
    {
     public:
      typedef boost::shared_ptr<mm_frequency_estimator> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of ofdm::mm_frequency_estimator.
       *
       * To avoid accidental use of raw pointers, ofdm::mm_frequency_estimator's
       * constructor is in a private implementation
       * class. ofdm::mm_frequency_estimator::make is the public interface for
       * creating new instances.
       */
      static sptr make(int vlen, int identical_parts, int scale, bool fbmc=0);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_MM_FREQUENCY_ESTIMATOR_H */

