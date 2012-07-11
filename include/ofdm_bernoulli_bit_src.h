#ifndef INCLUDED_OFDM_BERNOULLI_BIT_SRC_H_
#define INCLUDED_OFDM_BERNOULLI_BIT_SRC_H_

#include <ofdm_api.h>
#include <gr_sync_block.h>

class ofdm_bernoulli_bit_src;
typedef boost::shared_ptr<ofdm_bernoulli_bit_src> ofdm_bernoulli_bit_src_sptr;
OFDM_API ofdm_bernoulli_bit_src_sptr ofdm_make_bernoulli_bit_src(double p);


/*!

 */
class OFDM_API ofdm_bernoulli_bit_src : public gr_sync_block
{
  private:
    friend OFDM_API ofdm_bernoulli_bit_src_sptr ofdm_make_bernoulli_bit_src(double p);

    ofdm_bernoulli_bit_src(double p);

    double  d_p;
    
    class rng_detail;
    boost::shared_ptr<rng_detail> d_rng_detail;
 
  public:
    virtual ~ofdm_bernoulli_bit_src() {};

    int work(
      int noutput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_BERNOULLI_BIT_SRC_H_ */
