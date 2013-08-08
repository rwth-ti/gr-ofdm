/* -*- c++ -*- */
/* 
 * Copyright 2013 <+YOU OR YOUR COMPANY+>.
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


#ifndef INCLUDED_OFDM_REFERENCE_DATA_SOURCE_02_IB_H
#define INCLUDED_OFDM_REFERENCE_DATA_SOURCE_02_IB_H

#include <ofdm/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace ofdm {

  /*!
   * \param ref_data Unpacked byte data, lower 8 bits used
   */
    class OFDM_API reference_data_source_02_ib : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<reference_data_source_02_ib> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of ofdm::reference_data_source_02_ib.
       *
       * To avoid accidental use of raw pointers, ofdm::reference_data_source_02_ib's
       * constructor is in a private implementation
       * class. ofdm::reference_data_source_02_ib::make is the public interface for
       * creating new instances.
       */
      static sptr make(const std::vector<char> &ref_data);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_REFERENCE_DATA_SOURCE_02_IB_H */

