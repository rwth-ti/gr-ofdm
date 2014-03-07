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

#ifndef INCLUDED_OFDM_IMGTRANSFER_SRC_IMPL_H
#define INCLUDED_OFDM_IMGTRANSFER_SRC_IMPL_H

#include <ofdm/imgtransfer_src.h>

#include <ofdm/util_bmp.h>
#include <ofdm/util_random.h>
#include <string>
#include <vector>

namespace gr {
  namespace ofdm {

    class imgtransfer_src_impl : public imgtransfer_src
    {
     private:
	  std::string   		d_filename;

	  int d_pos;
	  unsigned int d_imgpos, d_bitcounter, d_bytecounter, d_color;
	  unsigned int d_bla;

	  unsigned int d_bitcount;

	  std::vector<unsigned char>		d_headerbuffer;
	  std::vector<unsigned char>		d_buffer;

	  CRandom random_generator;

	  Bitmap d_bitmap;

     public:
      imgtransfer_src_impl(std::string filename);
      ~imgtransfer_src_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
		       gr_vector_int &ninput_items,
		       gr_vector_const_void_star &input_items,
		       gr_vector_void_star &output_items);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_IMGTRANSFER_SRC_IMPL_H */

