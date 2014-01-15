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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "frame_mux_impl.h"

#include <iostream>

#include "malloc16.h"
#include <cstring>

#define DEBUG 0

namespace gr {
  namespace ofdm {

	  typedef float v4sf __attribute__ ((vector_size(16)));
	  typedef v4sf * v4sf_ptr __attribute__ ((aligned(16)));
	  typedef v4sf const * v4sfc_ptr __attribute__ ((aligned(16)));


    frame_mux::sptr
    frame_mux::make(int vlen, int frame_len)
    {
      return gnuradio::get_initial_sptr
        (new frame_mux_impl(vlen, frame_len));
    }

    /*
     * The private constructor
     */
    frame_mux_impl::frame_mux_impl(int vlen, int frame_len)
      : gr::block("frame_mux",
              gr::io_signature::make(1, 1, sizeof( gr_complex ) * vlen),
              gr::io_signature::make(1, 1, sizeof( gr_complex ) * vlen ))
     , d_vlen( vlen )
     , d_frame_len( frame_len )
     , d_preambles( 0 )
     , d_data_blocks( frame_len )
     , d_frame_head( 0 )
     , d_head_size( 0 )
    {
    	  update();
    	  assert( ( vlen % 2 ) == 0 ); // -> 16 bytes
    }

    /*
     * Our virtual destructor.
     */
    frame_mux_impl::~frame_mux_impl()
    {
    	  if( d_head_size > 0 )
    	  {
    	    free16Align( d_frame_head );
    	  }
    }

    void
    frame_mux_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    	ninput_items_required[ 0 ] = noutput_items / d_frame_len * d_data_blocks;
    }

    void
    frame_mux_impl ::
    add_preamble( std::vector< gr_complex > const & vec )
    {
      assert( vec.size() == d_vlen );

      std::cout << "add preamble" << std::endl;
      std::cout << "head size is " << d_head_size << std::endl;

      size_type const new_head_size = d_head_size + d_vlen * sizeof( gr_complex );

      std::cout << "new head size is " << new_head_size << std::endl;

      cache_ptr new_head =
        static_cast< cache_ptr >( malloc16Align( new_head_size ) );

      if( d_head_size > 0 )
      {
        memcpy( new_head, d_frame_head, d_head_size );
        free16Align( d_frame_head );
        std::cout << "copy old head to new head" << std::endl;
      }

      memcpy( new_head + d_head_size / sizeof( float ),
              vec.data(), d_vlen * sizeof( gr_complex ) );

      d_head_size = new_head_size;
      d_frame_head = new_head;

      ++d_preambles;
      d_data_blocks = d_frame_len - d_preambles;

      std::cout << "preambles " << d_preambles << " data blocks " << d_data_blocks
                << " framelen " << d_frame_len << std::endl;

      update();
    }

    void
    frame_mux_impl ::
    update()
    {
      set_output_multiple( d_frame_len );
      set_relative_rate( static_cast< double >( d_frame_len ) /
                         static_cast< double >( d_data_blocks ) );
      d_data_size = d_vlen * sizeof( gr_complex ) * d_data_blocks;
    }

    int
    frame_mux_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
    	  v4sfc_ptr __restrict in = static_cast< v4sfc_ptr >( input_items[0] );
    	  v4sf_ptr __restrict out = static_cast< v4sf_ptr >( output_items[0] );
    	  v4sfc_ptr __restrict fh = reinterpret_cast< v4sfc_ptr >( d_frame_head );

    	//  assert( ( (int)in & 15 ) == 0 );
    	//  assert( ( (int)out & 15 ) == 0 );
    	//  assert( ( (int)fh & 15 ) == 0 );


    	  size_type const nframes = noutput_items / d_frame_len;
    	  size_type const head_size = d_head_size / 16; // because d_vlen % 2 == 0
    	  size_type const data_size = d_data_size / 16;

    	  for( size_type i = 0; i < nframes; ++i )
    	  {
    	    for( size_type j = 0; j < head_size; ++j )
    	    {
    	      out[ j ] = fh[ j ];
    	    }
    	    out += head_size;

    	    for( size_type j = 0; j < data_size; ++j )
    	    {
    	      out[ j ] = in[ j ];
    	    }
    	    out += data_size;
    	    in += data_size;
    	  }

    	  consume( 0, nframes * d_data_blocks );

    	  return nframes * d_frame_len;
    }

  } /* namespace ofdm */
} /* namespace gr */

