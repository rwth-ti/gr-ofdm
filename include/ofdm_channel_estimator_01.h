#ifndef INCLUDED_OFDM_CHANNEL_ESTIMATOR_01_H_
#define INCLUDED_OFDM_CHANNEL_ESTIMATOR_01_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_sync_block.h>

class ofdm_channel_estimator_01;
typedef boost::shared_ptr<ofdm_channel_estimator_01> ofdm_channel_estimator_01_sptr;
OFDM_API ofdm_channel_estimator_01_sptr ofdm_make_channel_estimator_01 (int vlen);

#include <vector>
#include <boost/shared_array.hpp>

/*!
 * Inputs:
 * - ofdm symbols, complex vector stream, width=vlen
 * - frame trigger, byte stream, one byte per ofdm symbol
 *
 * Outputs:
 * - inverse CTF, for equalizer, same format as ofdm symbol stream
 * - CTF, as above
 */
class OFDM_API ofdm_channel_estimator_01 : public gr_sync_block
{
private:
  friend OFDM_API ofdm_channel_estimator_01_sptr ofdm_make_channel_estimator_01 (int vlen);

  ofdm_channel_estimator_01 (int vlen);
  
  int d_vlen;
  int d_blk;
  boost::shared_array<gr_complex> d_inv_ctf_estimate;
  boost::shared_array<gr_complex> d_ctf_estimate;

  /*!
   * Known Symbol: compute CTF for this symbol.
   * Pilot: Store CTF.
   * Symbol: Known data
   */
  struct ofdm_block
  {
    ofdm_block() : known_block(false), pilot(false) {};
    bool known_block;
    bool pilot;
    boost::shared_array<gr_complex> block;
  };

  std::vector<ofdm_block> d_ofdm_frame;

  void calculate_equalization(
      const gr_complex* blk,
      const boost::shared_array<gr_complex>& known_blk,
      boost::shared_array<gr_complex> &inv_ctf,
      boost::shared_array<gr_complex> &ctf);

public:
  virtual ~ofdm_channel_estimator_01() {};

  void set_known_block(int no, const std::vector<gr_complex> &block, bool pilot);

  int work (int noutput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_CHANNEL_ESTIMATOR_01_H_ */
