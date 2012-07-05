/* -*- c++ -*- */
/*
 * Copyright 2004,2006 Free Software Foundation, Inc.
 *
 * This file is part of GNU Radio
 *
 * GNU Radio is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2, or (at your option)
 * any later version.
 *
 * GNU Radio is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with GNU Radio; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <string.h>

#include <gr_sync_block.h>

#include <ofdm_vector_mask.h>
#include <gr_io_signature.h>

#include <iostream>

ofdm_vector_mask_sptr ofdm_make_vector_mask( size_t vlen, size_t cut_left,
  size_t mask_len, std::vector< unsigned char > mask )
{
  return ofdm_vector_mask_sptr( new ofdm_vector_mask( vlen, cut_left, mask_len,
    mask ) );
}

ofdm_vector_mask::ofdm_vector_mask( size_t vlen, size_t cut_left,
  size_t mask_len, std::vector< unsigned char > mask ) :

  gr_sync_block( "vector_mask",
    gr_make_io_signature( 1, 1, vlen * sizeof(gr_complex) ),
    gr_make_io_signature( 1, 1, mask_len* sizeof(gr_complex) ) ),

  d_vlen( vlen ),
  d_cut_left( cut_left ),
  d_mask_len( mask_len ),
  d_mask( mask )
{
}

int
ofdm_vector_mask::work(
  int noutput_items,
  gr_vector_const_void_star &input_items,
  gr_vector_void_star &output_items )
{
  const gr_complex *in = static_cast< const gr_complex* > ( input_items[0] );
  gr_complex *out = static_cast< gr_complex* > ( output_items[0] );

  const int bytelen = d_mask_len * sizeof( gr_complex );
  in += d_cut_left;

  for( int i = 0; i < noutput_items; ++i )
  {
    memcpy( out, in, bytelen );
    out += d_mask_len;
    in += d_vlen;
  }

  return noutput_items;
}
