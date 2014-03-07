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

#ifndef INCLUDED_OFDM_FSM_H
#define INCLUDED_OFDM_FSM_H

#include <ofdm/api.h>

#include <vector>
#include <iosfwd>

//namespace gr {
 // namespace ofdm {

    /*!
     * \brief <+description+>
     *
     */
    class  OFDM_API fsm
    {
    public:
      fsm();
      ~fsm();
      fsm(const fsm &FSM);
      fsm(int I, int S, int O, const std::vector<int> &NS, const std::vector<int> &OS);
      fsm(const char *name);
      fsm(int k, int n, const std::vector<int> &G);
      fsm(int mod_size, int ch_length);
      fsm(int P, int M, int L);
      fsm(const fsm &FSM1, const fsm &FSM2);
      fsm(const fsm &FSM, int n);
      int I () const { return d_I; }
      int S () const { return d_S; }
      int O () const { return d_O; }
      const std::vector<int> & NS () const { return d_NS; }
      const std::vector<int> & OS () const { return d_OS; }
      const std::vector< std::vector<int> > & PS () const { return d_PS; }
      const std::vector< std::vector<int> > & PI () const { return d_PI; }
      const std::vector<int> & TMi () const { return d_TMi; }
      const std::vector<int> & TMl () const { return d_TMl; }
      void write_trellis_svg(std::string filename ,int number_stages);
      virtual void write_fsm_txt(std::string filename);
    private:
      int d_I;
      int d_S;
      int d_O;
      std::vector<int> d_NS;
      std::vector<int> d_OS;
      std::vector< std::vector<int> > d_PS;
      std::vector< std::vector<int> > d_PI;
      std::vector<int> d_TMi;
      std::vector<int> d_TMl;
      void generate_PS_PI ();
      void generate_TM ();
      bool find_es(int es);
    };

//  } // namespace ofdm
//} // namespace gr

#endif /* INCLUDED_OFDM_FSM_H */

