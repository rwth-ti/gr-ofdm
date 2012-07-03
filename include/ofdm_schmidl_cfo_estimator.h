#ifndef INCLUDED_OFDM_SCHMIDL_CFO_ESTIMATOR_H_
#define INCLUDED_OFDM_SCHMIDL_CFO_ESTIMATOR_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>
#include <gr_sync_block.h>

class ofdm_schmidl_cfo_estimator;
typedef boost::shared_ptr<ofdm_schmidl_cfo_estimator> ofdm_schmidl_cfo_estimator_sptr;
OFDM_API ofdm_schmidl_cfo_estimator_sptr ofdm_make_schmidl_cfo_estimator (const int fft_length, const int carriers, 
    const int estimation_range, const std::vector<gr_complex>& differential_pn_seq);

/*!
  Carrier frequency offset estimator
  This block calculates a metric that will show up a maximum at the point that is an
  estimation for the integer part of the present frequency shift.
  It supposes	to have a special preamble design, where two pn sequences are transmitted
  on the even subchannels. See Schmidl & Cox's paper.
  
  Input 1 is a a stream of fft'ed preamble 1.
  Input 2 is a a stream of fft'ed preamble 2.
  
  Output is a vector of size estimation_range * 2 + 1
  Index goes from -estimation_range to +estimation_range
  Maximum at e.g. 80 with range = 100 means: 80 => -20 => offset is -20 + frac(offset)
  
  The parameter differential_pn_seq is meant to be:
    v_k = conjugate(sqrt(2) * c_2_k / c_1_k)
  assuming that c_1_k and c_2_k are the pn sequences of the first and second preamble.
  We ignore even indices.
*/
class OFDM_API ofdm_schmidl_cfo_estimator : public gr_sync_block
{
private:

  friend OFDM_API ofdm_schmidl_cfo_estimator_sptr ofdm_make_schmidl_cfo_estimator (const int fft_length, 
    const int carriers, const int estimation_range, const std::vector<gr_complex>& differential_pn_seq);

  ofdm_schmidl_cfo_estimator (const int fft_length, const int carriers, 
    const int estimation_range, const std::vector<gr_complex>& differential_pn_seq);

  std::vector<gr_complex> d_differential_pn_seq;
  int d_fft_length;
  int d_carriers;
  int d_left_padding;
  int d_estimation_range;

public:

  virtual ~ofdm_schmidl_cfo_estimator() {};

  int work (int noutput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_SCHMIDL_CFO_ESTIMATOR_H_ */
