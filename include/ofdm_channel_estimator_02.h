#ifndef INCLUDED_OFDM_CHANNEL_ESTIMATOR_02_H_
#define INCLUDED_OFDM_CHANNEL_ESTIMATOR_02_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_sync_block.h>

#include <vector>
#include <boost/shared_array.hpp>

class ofdm_channel_estimator_02;
typedef boost::shared_ptr<ofdm_channel_estimator_02> 
    ofdm_channel_estimator_02_sptr;
    
OFDM_API ofdm_channel_estimator_02_sptr ofdm_make_channel_estimator_02(int vlen, 
    const std::vector<int> &pilot_tones, 
    const std::vector<int> &nondata_block);

/*!
 * \brief Channel estimator/equalizer + LMS Phase tracking
 * 
 * Inputs should be unequalized blocks and a reset trigger to identify the
 * first preamble.
 * 
 * Outputs are the equalized ofdm blocks and the normalized CTF.
 */
class OFDM_API ofdm_channel_estimator_02 : public gr_sync_block
{
private:
  
  friend OFDM_API ofdm_channel_estimator_02_sptr 
  ofdm_make_channel_estimator_02(int vlen, 
      const std::vector<int> &pilot_tones, 
      const std::vector<int> &nondata_block);

  ofdm_channel_estimator_02(int vlen, 
      const std::vector<int> &pilot_tones, 
      const std::vector<int> &nondata_block);
  
  
  typedef boost::shared_array<float> norm_ctf_t;
  typedef boost::shared_array<gr_complex> block_t;
  
  block_t d_inv_ctf_estimate;
  norm_ctf_t d_norm_ctf_estimate;
  block_t d_tmp_ctf_estimate;
  block_t d_tmp_inv_ctf_estimate;
  norm_ctf_t d_tmp_norm_ctf_estimate;


  int d_blk;
  int d_dblk;
  int d_vlen;  
  int d_pcount;

  float d_acc_gamma;
  float d_acc_b;
  
  struct ofdm_block
  {
    ofdm_block() : known_block(false), pilot(false) {};
    bool known_block;
    bool pilot;
    block_t block;
    std::vector<bool> subc_used;
  };
  
  typedef boost::shared_ptr<ofdm_block> ofdm_block_sptr;
  
  std::vector<bool>         d_nondata_block;
  std::vector<float>        d_pilot_tone;
  std::vector<int>          d_pilot;
  std::vector<bool>         d_is_pilot;
  std::vector<float>        d_gamma_coeff;
  std::vector<float>        d_acc_phase;
  
  std::vector<ofdm_block_sptr>   d_ofdm_frame;
  
  
  
  
  inline void 
  LMS_phasetracking( gr_complex* out );
  
  inline block_t
  channel_estimation( 
      const gr_complex* in,
      gr_complex* out,
      float* ctf );
  
  void
  init_LMS_phasetracking(
      const std::vector<int> &pilot_tones,
      const std::vector<int> &nondata_block );
  
  void init_channel_estimation();

 
public:
  
  virtual ~ofdm_channel_estimator_02();
  
  void set_known_block(int no, 
      const std::vector<gr_complex> &block, bool pilot);

  int work(
    int noutput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_CHANNEL_ESTIMATOR_02_H_ */
