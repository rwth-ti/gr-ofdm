#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_sc_snr_estimator.h>

#include <cmath>
#include <algorithm>
#include <iostream>

ofdm_sc_snr_estimator_sptr ofdm_make_sc_snr_estimator(int vlen)
{
  return ofdm_sc_snr_estimator_sptr(new ofdm_sc_snr_estimator(vlen));
}

ofdm_sc_snr_estimator::ofdm_sc_snr_estimator(int vlen)
  : gr_sync_block("sc_snr_estimator",
           gr_make_io_signature (1, 1, sizeof(gr_complex)*vlen),
           gr_make_io_signature (1, 1, sizeof(float))),
  d_vlen(vlen)
{
}

//inline static gr_complexd recursive_p_sum(const gr_complex* in, int vlen, const int& N){
//  if(vlen == 1){
//    return std::conj((gr_complexd)in[0])*(gr_complexd)in[N];
//  }
//  
//  return recursive_p_sum(in,vlen/2,N)+recursive_p_sum(in+vlen/2,vlen/2,N);
//}
//
//inline static double recursive_r_sum(const gr_complex* in, int vlen){
//  if(vlen == 1){
//    return (double)in->real() * (double)in->real() 
//            + (double)in->imag() * (double)in->imag();
//  }
//  
//  return recursive_r_sum(in,vlen/2)+recursive_r_sum(in+vlen/2,vlen/2);
//}
//

int ofdm_sc_snr_estimator::work(
    int noutput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  const gr_complex *in = static_cast<const gr_complex*>(input_items[0]);
  float *out = static_cast<float*>(output_items[0]);
  
  const int N = d_vlen/2;
  
  for(int i = 0; i < noutput_items; ++i, in+=d_vlen){
    
    // compute correlation between first half and second half
    gr_complexd p(0.0,0.0);
//    p = recursive_p_sum(in,d_vlen,N);
//    double r = recursive_r_sum(in,d_vlen);
    double r = 0.0;
    for(int k = 0; k < N; ++k){
      p += std::conj(in[k])*in[k+N];
      r += in[k].real()*in[k].real()+in[k].imag()*in[k].imag()
           +in[k+N].real()*in[k+N].real()+in[k+N].imag()*in[k+N].imag();
    }
    
    double p_mag = std::abs(p);
//    double diff = r - p_mag;
    double m = p_mag/(r*0.5);
    
//    if(diff < 0.0){
//      // uh maybe simulation?
//      diff = 1e-6;
//    }
    double m_lim = std::max(1.-(2e-5),std::min(-1000.,m));
//    double snr_est = p_mag/diff;
    double snr_est = m / (1 - m_lim);
    
    // numerically unstable, avoid large absolute values
    double snr_lim = std::max(0.1, std::min(1000000.0, snr_est));
    
    out[i] = (float)snr_lim;
//    std::cout << "[SNR] " << p_mag << " " << r << " "  << snr_est << " -- " << snr_lim << std::endl;
//    std::cout << "[SNR] " << p_mag << " " << r << " " << diff << " "  << snr_est << " -- " << snr_lim << std::endl;
    
  }
  
  return noutput_items;
}
