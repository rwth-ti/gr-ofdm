/* -*- c++ -*- */
/* 
 * Copyright 2014 <+YOU OR YOUR COMPANY+>.
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
#include "midamble_insert_impl.h"

#include "malloc16.h"

namespace gr {
  namespace ofdm {

  typedef float v4sf __attribute__ ((vector_size(16)));
  typedef v4sf * v4sf_ptr __attribute__ ((aligned(16)));
  typedef v4sf const * v4sfc_ptr __attribute__ ((aligned(16)));


    midamble_insert::sptr
    midamble_insert::make(int vlen, int frame_len)
    {
      return gnuradio::get_initial_sptr
        (new midamble_insert_impl(vlen, frame_len));
    }

    /*
     * The private constructor
     */
    midamble_insert_impl::midamble_insert_impl(int vlen, int frame_len)
      : gr::block("midamble_insert",
              gr::io_signature::make(1, 1, sizeof( gr_complex ) * vlen),
              gr::io_signature::make(1, 1, sizeof( gr_complex ) * vlen ))
    , d_vlen( vlen )
    , d_frame_len( frame_len )
    , d_head_size( 0 )
    {
  	  update();
  	  assert( ( vlen % 2 ) == 0 ); // -> 16 bytes
    }

    /*
     * Our virtual destructor.
     */
    midamble_insert_impl::~midamble_insert_impl()
    {
    }

    void
    midamble_insert_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    	ninput_items_required[ 0 ] = noutput_items / (d_frame_len+1) * d_frame_len;
    }

    void
    midamble_insert_impl ::
    update()
    {
  	  d_data_size = d_vlen * sizeof( gr_complex ) * d_frame_len;
	  d_head_size = d_vlen * sizeof( gr_complex );

        set_output_multiple( d_frame_len+1 );
        set_relative_rate( static_cast< double >( d_frame_len+1 ) /
                           static_cast< double >( d_frame_len ) );
    }

    int
    midamble_insert_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {

/*        const <+ITYPE*> *in = (const <+ITYPE*> *) input_items[0];
        <+OTYPE*> *out = (<+OTYPE*> *) output_items[0];

        // Do <+signal processing+>
        // Tell runtime system how many input items we consumed on
        // each input stream.
        consume_each (noutput_items);

        // Tell runtime system how many output items we produced.
        return noutput_items;*/

      v4sfc_ptr __restrict in = static_cast< v4sfc_ptr >( input_items[0] );
	  v4sf_ptr __restrict out = static_cast< v4sf_ptr >( output_items[0] );

	  const v4sf zero = { 0.0};



	 // v4sfc_ptr __restrict fh = reinterpret_cast< v4sfc_ptr >( d_frame_head );

	//  assert( ( (int)in & 15 ) == 0 );
	//  assert( ( (int)out & 15 ) == 0 );
	//  assert( ( (int)fh & 15 ) == 0 );



	  //size_type const nframes = noutput_items / (d_frame_len- d_preambles+1);
	  size_type const nframes = noutput_items / (d_frame_len+1);
	  size_type const head_size = d_head_size / 16; // because d_vlen % 2 == 0
	  size_type const data_size = d_data_size / 16;

	  for( size_type i = 0; i < nframes; ++i )
	  {
		for( size_type j = 0; j < head_size; ++j )
		{
		  out[ j ] = in[ j ];
		}
		out += head_size;
		in += head_size;


		  for( size_type j = 0; j < head_size; ++j )
		{
		  out[ j ] = zero;
		}
		out += head_size;

		for( size_type j = 0; j < data_size-head_size; ++j )
		{
		  out[ j ] = in[ j ];
		}
		out += data_size-head_size;
		in += data_size-head_size;
	  }

	  consume( 0, nframes * d_frame_len );

	  //return nframes * (d_frame_len- d_preambles+1);
	  return nframes * (d_frame_len+1);


    }

  } /* namespace ofdm */
} /* namespace gr */

