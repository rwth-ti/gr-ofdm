#ifndef INCLUDED_OFDM_GENERIC_SOFTDEMAPPER_VCF_H_
#define INCLUDED_OFDM_GENERIC_SOFTDEMAPPER_VCF_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>

class ofdm_generic_softdemapper_vcf;
typedef boost::shared_ptr<ofdm_generic_softdemapper_vcf> ofdm_generic_softdemapper_vcf_sptr;
OFDM_API ofdm_generic_softdemapper_vcf_sptr ofdm_make_generic_softdemapper_vcf (int vlen,bool coding=false);

class ofdmi_modem;

#include <boost/shared_array.hpp>

/*!
 * \brief Generic demapper for OFDM
 * 
 * Input ports:
 *  1. data blocks
 *  2. bit maps
 *  3- channel state informations (proportional to subchannel SNRs)
 *  4. update trigger
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
class OFDM_API ofdm_generic_softdemapper_vcf : public gr_block
{
private:
  friend OFDM_API ofdm_generic_softdemapper_vcf_sptr
    ofdm_make_generic_softdemapper_vcf (int vlen,bool coding);

  ofdm_generic_softdemapper_vcf(int vlen,bool coding);

  int d_vlen, d_items_req, d_need_bitmap, d_need_csi;
  bool d_coding;
  
  boost::shared_array<float> d_csi;

  // internal state
  boost::shared_array<char> d_bitmap;
  
  boost::shared_ptr<ofdmi_modem> d_demod;
  
  void forecast (int noutput_items, gr_vector_int &ninput_items_required);

public:
  virtual ~ofdm_generic_softdemapper_vcf();

  int general_work(int noutput_items,
    gr_vector_int &ninput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items);
  
  virtual int noutput_forecast( gr_vector_int &ninput_items, 
      int available_space, int max_items_avail,
      std::vector<bool> &input_done );
  
  std::vector<gr_complex> get_constellation( int bits, bool coding=false );
  
};


#endif /* INCLUDED_OFDM_GENERIC_SOFTDEMAPPER_VCF_H_ */
