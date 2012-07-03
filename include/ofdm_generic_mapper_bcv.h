#ifndef INCLUDED_OFDM_GENERIC_MAPPER_BCV_H_
#define INCLUDED_OFDM_GENERIC_MAPPER_BCV_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>
#include <boost/shared_array.hpp>
#include <gr_block.h>

class ofdm_generic_mapper_bcv;
typedef boost::shared_ptr<ofdm_generic_mapper_bcv> ofdm_generic_mapper_bcv_sptr;
OFDM_API ofdm_generic_mapper_bcv_sptr ofdm_make_generic_mapper_bcv (int vlen);

class ofdmi_modem;

/*! 
 * \brief Generic mapper for OFDM
 * input 1: byte stream, 1 bit per byte!
 * input 2: byte vector, size = number of carriers. bits per channel assignment
 *   Currently supported: 0,1,2,3,4,5,6,7,8 bits per symbol
 */
class OFDM_API ofdm_generic_mapper_bcv : public gr_block
{
private:
  friend OFDM_API ofdm_generic_mapper_bcv_sptr ofdm_make_generic_mapper_bcv (int vlen);
  
  ofdm_generic_mapper_bcv(int vlen);
  
  int d_vlen;
  int d_need_bits;
  ofdmi_modem *mod;
  
  void forecast (int noutput_items, gr_vector_int &ninput_items_required);
  
  
  int d_need_bitmap;
  boost::shared_array<char> d_bitmap;
  

public:
  virtual ~ofdm_generic_mapper_bcv() {};
  
  int general_work(int noutput_items, 
      gr_vector_int &ninput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
  
  virtual int noutput_forecast( gr_vector_int &ninput_items, 
      int available_space, int max_items_avail,
      std::vector<bool> &input_done );
};
     

#endif /* INCLUDED_OFDM_GENERIC_MAPPER_BCV_H_ */
