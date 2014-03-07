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

#ifndef OFDMI_SHARED_GENERATOR_H_
#define OFDMI_SHARED_GENERATOR_H_

#include <boost/random.hpp>
#include <boost/shared_ptr.hpp>

typedef boost::mt19937 shared_generator_type;
typedef boost::shared_ptr<shared_generator_type> shared_generator_sptr;

shared_generator_sptr
get_shared_generator( void );

#endif /*OFDMI_SHARED_GENERATOR_H_*/
