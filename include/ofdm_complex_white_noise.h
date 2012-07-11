#ifndef INCLUDED_OFDM_COMPLEX_WHITE_NOISE_H_
#define INCLUDED_OFDM_COMPLEX_WHITE_NOISE_H_

#include <ofdm_api.h>
#include <gr_sync_block.h>

class ofdm_complex_white_noise;
typedef boost::shared_ptr<ofdm_complex_white_noise> 
  ofdm_complex_white_noise_sptr;
  
OFDM_API ofdm_complex_white_noise_sptr 
ofdm_make_complex_white_noise( gr_complex mean, float sigma );

/*!

 */
class OFDM_API ofdm_complex_white_noise : public gr_sync_block
{
private:
  ofdm_complex_white_noise( gr_complex mean, float sigma );
  
  class rng_detail;
  boost::shared_ptr<rng_detail> d_rng_detail;

  gr_complex  d_mean;
  float  d_sigma;

public:
  static ofdm_complex_white_noise_sptr
  create( gr_complex mean, float sigma );
  
  virtual ~ofdm_complex_white_noise() {};

  int work(
    int                         noutput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items);
};

#endif /* INCLUDED_OFDM_COMPLEX_WHITE_NOISE_H_ */
