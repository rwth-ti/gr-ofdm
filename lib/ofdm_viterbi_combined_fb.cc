/* -*- c++ -*- */
/*
 * Copyright 2004 Free Software Foundation, Inc.
 * 
 * This file is part of GNU Radio
 * 
 * GNU Radio is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
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

// WARNING: this file is machine generated.  Edits will be over written

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <ofdm_viterbi_combined_fb.h>
#include <gr_io_signature.h>
#include <assert.h>
#include <iostream>
  
static const float INF = 1.0e9;

#define DEBUG 0

ofdm_viterbi_combined_fb_sptr
ofdm_make_viterbi_combined_fb (
    const fsm &FSM,
    int K,
    int S0,
    int SK,
    int D,
    int chunkdivisor,
    const std::vector<float> &TABLE,
    ofdm_metric_type_t TYPE)
{
  return ofdm_viterbi_combined_fb_sptr (new ofdm_viterbi_combined_fb (FSM,K,S0,SK,D,chunkdivisor,TABLE,TYPE));
}

ofdm_viterbi_combined_fb::ofdm_viterbi_combined_fb (
    const fsm &FSM,
    int K,
    int S0,
    int SK,
    int D,
    int chunkdivisor,
    const std::vector<float> &TABLE,
    ofdm_metric_type_t TYPE)
  : gr_block ("viterbi_combined_fb",
			  gr_make_io_signature2 (2, 2,
					  sizeof (float),
					  sizeof(unsigned int)),
			  gr_make_io_signature (1, 1, sizeof (unsigned char))),
  d_FSM (FSM),
  d_K (K),
  d_S0 (S0),
  d_SK (SK),
  d_D (D),
  d_chunkdivisor (chunkdivisor),
  d_TABLE (TABLE),
  d_TYPE (TYPE),
  d_chunkcounter(0)//,
  //d_trace(FSM.S()*K)
{
    set_relative_rate (1.0 / ((double) d_D));
    set_output_multiple (d_K);
}


void ofdm_viterbi_combined_fb::set_TABLE(const std::vector<float> &table)
{
  d_TABLE = table;
}

void ofdm_viterbi_combined_fb::set_K(int K)
{
	d_K = K;
	set_output_multiple(d_K);
}

void
ofdm_viterbi_combined_fb::forecast (int noutput_items, gr_vector_int &ninput_items_required)
{
	assert (noutput_items % d_K == 0);
	ninput_items_required[0] = d_D * d_K;
	if(d_chunkcounter==0)
	{
		ninput_items_required[1] = 1;
	}
	else
	{
		ninput_items_required[1] = 0;
	}
}

void viterbi_algorithm_combined(int I, int S, int O, 
             const std::vector<int> &NS,
             const std::vector<int> &OS,
             const std::vector< std::vector<int> > &PS,
             const std::vector< std::vector<int> > &PI,
             int K,
             int S0,int SK,
             int D,
             const std::vector<float> &TABLE,
             ofdm_metric_type_t TYPE,
             const float *in, unsigned char *out)//,
             //std::vector<int> &trace) 
{
  std::vector<int> trace(S*K);
  std::vector<float> alpha(S*2);
  float *metric = new float[O];
  int alphai;
  float norm,mm,minm;
  int minmi;
  int st;

  if(S0<0) { // initial state not specified
      for(int i=0;i<S;i++) alpha[0*S+i]=0;
  }
  else {
      for(int i=0;i<S;i++) alpha[0*S+i]=INF;
      alpha[0*S+S0]=0.0;
  }

  alphai=0;
  for(int k=0;k<K;k++) {
      calc_metric(O, D, TABLE, &(in[k*D]), metric,TYPE); // calc metrics
      norm=INF;
      for(int j=0;j<S;j++) { // for each next state do ACS
          minm=INF;
          minmi=0;
          for(unsigned int i=0;i<PS[j].size();i++) {
              //int i0 = j*I+i;
              if((mm=alpha[alphai*S+PS[j][i]]+metric[OS[PS[j][i]*I+PI[j][i]]])<minm)
                  minm=mm,minmi=i;
          }
          trace[k*S+j]=minmi;
          alpha[((alphai+1)%2)*S+j]=minm;
          if(minm<norm) norm=minm;
      }
      for(int j=0;j<S;j++) 
          alpha[((alphai+1)%2)*S+j]-=norm; // normalize total metrics so they do not explode
      alphai=(alphai+1)%2;
  }

  if(SK<0) { // final state not specified
      minm=INF;
      minmi=0;
      for(int i=0;i<S;i++)
          if((mm=alpha[alphai*S+i])<minm) minm=mm,minmi=i;
      st=minmi;
  }
  else {
      st=SK;
  }

  for(int k=K-1;k>=0;k--) { // traceback
      int i0=trace[k*S+st];
      out[k]= (unsigned char) PI[st][i0];
      st=PS[st][i0];
  }
  
  delete [] metric;

}

int
ofdm_viterbi_combined_fb::general_work (int noutput_items,
                        gr_vector_int &ninput_items,
                        gr_vector_const_void_star &input_items,
                        gr_vector_void_star &output_items)
{
	if(DEBUG)
		std::cout << "d_K input: " << *((unsigned int*)input_items[1]) << " noutput_items: " << noutput_items << std::endl;
	set_K(*((unsigned int*)input_items[1]));
	//consume(1,1);
	if (noutput_items % d_K != 0)
		return 0;

	//int nblocks = noutput_items / d_K;
	const float *in = (const float *) input_items[0];
	unsigned char *out = (unsigned char *) output_items[0];



	//for (int n=0;n<nblocks;n++) {
	int n = 0;
		viterbi_algorithm_combined(d_FSM.I(),d_FSM.S(),d_FSM.O(),d_FSM.NS(),d_FSM.OS(),d_FSM.PS(),d_FSM.PI(),d_K,d_S0,d_SK,d_D,d_TABLE,d_TYPE,&(in[n*d_K*d_D]),&(out[n*d_K]));//,d_trace);
	//}
	d_chunkcounter++;
  //consume(0,d_D * noutput_items );
  consume(0,d_D * d_K );
  //if (nblocks > 0)
  //consume(1,nblocks);
  if(d_chunkcounter==d_chunkdivisor)
  {
	  consume(1,1);
  	  d_chunkcounter=0;
  }
  //return noutput_items;
  return d_K;
}
