#ifndef INCLUDED_OFDM_GENERIC_DEMAPPER_VCB_H_
#define INCLUDED_OFDM_GENERIC_DEMAPPER_VCB_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>
#include <gr_block.h>

class ofdm_generic_demapper_vcb;
typedef boost::shared_ptr<ofdm_generic_demapper_vcb> ofdm_generic_demapper_vcb_sptr;
OFDM_API ofdm_generic_demapper_vcb_sptr ofdm_make_generic_demapper_vcb (int vlen);

class ofdmi_modem;

#include <boost/shared_array.hpp>

/*!
 * \brief Generic demapper for OFDM
 * 
 * Input ports:
 *  1. data blocks
 *  2. bit maps
 *  3. update trigger
 * 
 * Output ports:
 *  1. bit stream
 * 
 * Demap incoming data blocks according to last bit map. On update trigger,
 * the next available bit map is stored and will be used for next data blocks.
 * There must be one trigger point per data block with value of either 1 or 0.
 * 
 *   Currently supported: 0, 1, 2, 3, 4, 5, 6, 7, 8 bits per symbol
 *   Supported modulations: BPSK, QPSK, 8PSK, 16-QAM, 32-QAM, 64-QAM, 128-QAM, 256-QAM
 */
class OFDM_API ofdm_generic_demapper_vcb : public gr_block
{
private:
  friend OFDM_API ofdm_generic_demapper_vcb_sptr
    ofdm_make_generic_demapper_vcb (int vlen);

  ofdm_generic_demapper_vcb(int vlen);

  int d_vlen;
  
  int d_items_req;
  int d_need_bitmap;
  
  // internal state
  boost::shared_array<char> d_bitmap;
  
  boost::shared_ptr<ofdmi_modem> d_demod;
  
  void forecast (int noutput_items, gr_vector_int &ninput_items_required);

public:
  virtual ~ofdm_generic_demapper_vcb();

  int general_work(int noutput_items,
    gr_vector_int &ninput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items);
  
  virtual int noutput_forecast( gr_vector_int &ninput_items, 
      int available_space, int max_items_avail,
      std::vector<bool> &input_done );
  
  std::vector<gr_complex> get_constellation( int bits );
  
};


#endif /* INCLUDED_OFDM_GENERIC_DEMAPPER_VCB_H_ */
