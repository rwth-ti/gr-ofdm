#ifndef INCLUDED_OFDM_SYMBOL_RANDOM_SRC_H_
#define INCLUDED_OFDM_SYMBOL_RANDOM_SRC_H_

#include <ofdm_api.h>
#include <gr_sync_block.h>

class ofdm_symbol_random_src;
typedef boost::shared_ptr<ofdm_symbol_random_src> ofdm_symbol_random_src_sptr;

OFDM_API ofdm_symbol_random_src_sptr 
  ofdm_make_symbol_random_src(const std::vector<gr_complex>& symbols, int vlen);

/*!

 */
class OFDM_API ofdm_symbol_random_src : public gr_sync_block
{
  private:
    friend OFDM_API ofdm_symbol_random_src_sptr 
    ofdm_make_symbol_random_src( const std::vector<gr_complex>& symbols, 
        int vlen );

    ofdm_symbol_random_src(const std::vector<gr_complex>& symbols, int vlen);

    std::vector<gr_complex>   d_symbols;
    int   d_vlen;
    
    class rng_detail;
    boost::shared_ptr<rng_detail> d_rng_detail;
 
  public:
    virtual ~ofdm_symbol_random_src() {};

    int work(
      int noutput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_SYMBOL_RANDOM_SRC_H_ */
