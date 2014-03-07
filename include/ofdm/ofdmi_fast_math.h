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

#ifndef INCLUDED_OFDMI_FAST_MATH_H_
#define INCLUDED_OFDMI_FAST_MATH_H_


typedef float v4sf __attribute__ ((vector_size (16)));
typedef float const v4sfc __attribute__ ((vector_size (16)));

typedef union
{
  v4sf vec;
  float v[4];
}
v4sf_i __attribute__((aligned(16)));


static inline
void
perform_frequency_shift( gr_complex const * const in, gr_complex * const out,
  int vlen, float const initial_phase, float const phase_step )
{
  v4sf_i phasor = { { 0 } };
  phasor.v[0] = std::cos( initial_phase );
  phasor.v[1] = std::sin( initial_phase );
  phasor.v[2] = std::cos( initial_phase + phase_step );
  phasor.v[3] = std::sin( initial_phase + phase_step );

  v4sf_i step_phasor = { { 0 } };
  step_phasor.v[0] = std::cos( 2 * phase_step );
  step_phasor.v[1] = std::sin( 2 * phase_step );
  step_phasor.v[2] = std::cos( 2 * phase_step );
  step_phasor.v[3] = std::sin( 2 * phase_step );

  v4sfc * vin = reinterpret_cast< v4sfc * >( in );
  v4sf * vout = reinterpret_cast< v4sf * >( out );

  // complex multiplication, with gr_expj( phase )
  // phase increased for every complex sample
  for( int j = 0; j < vlen/2; ++j )
  {
    v4sf x0 = __builtin_ia32_movsldup( phasor.vec );
    v4sf x1 = vin[ j ];
    x0 *= x1;

    x1 = __builtin_ia32_shufps( x1, x1, 0xB1 );
    v4sf x2 = __builtin_ia32_movshdup( phasor.vec );
    x2 *= x1;

    x0 = __builtin_ia32_addsubps( x0, x2 );
    vout[ j ] = x0;


    x0 = __builtin_ia32_movsldup( phasor.vec );
    x1 = step_phasor.vec;
    x0 *= x1;

    x1 = __builtin_ia32_shufps( x1, x1, 0xB1 );
    x2 = __builtin_ia32_movshdup( phasor.vec );
    x2 *= x1;

    x0 = __builtin_ia32_addsubps( x0, x2 );
    phasor.vec = x0;

  } // for-loop over input

} // perform_frequency_shift

//    gr_complex phasor( std::cos( d_phase ), std::sin( d_phase ) );
//    const gr_complex step_phasor( std::cos( phase_step ),
//      std::sin( phase_step ) );
//
//    for( int j = 0; j < d_vlen; ++j )
//    {
//      out[j] = in[j] * phasor;
//      phasor *= step_phasor;
//    }

static inline
void
multiply_complex_vector( gr_complex const * const x,
  gr_complex const * const y, gr_complex * const out, int vlen )
{
  v4sfc * vx = reinterpret_cast< v4sfc * >( x );
  v4sfc * vy = reinterpret_cast< v4sfc * >( y );
  v4sf * vout = reinterpret_cast< v4sf * >( out );

  for( int j = 0; j < vlen/2; ++j )
  {
    v4sf x0 = __builtin_ia32_movsldup( vx[ j ] );
    v4sf x1 = vy[ j ];
    x0 *= x1;

    x1 = __builtin_ia32_shufps( x1, x1, 0xB1 );
    v4sf x2 = __builtin_ia32_movshdup( vx[ j ] );
    x2 *= x1;

    x0 = __builtin_ia32_addsubps( x0, x2 );
    vout[ j ] = x0;

  } // element-wise complex multiplication with d_buffer

} // multiply_complex_vector

#endif // INCLUDED_OFDMI_FAST_MATH_H_
