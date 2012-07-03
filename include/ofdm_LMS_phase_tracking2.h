
/* $Id: ofdm_LMS_phase_tracking2.h 923 2009-04-21 14:03:45Z auras $ */

#ifndef INCLUDED_OFDM_LMS_PHASE_TRACKING2_H_
#define INCLUDED_OFDM_LMS_PHASE_TRACKING2_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>// forward declarations
#include <gr_sync_block.h>

#include <vector>

class ofdm_LMS_phase_tracking2;
typedef boost::shared_ptr<ofdm_LMS_phase_tracking2>
  ofdm_LMS_phase_tracking2_sptr;

OFDM_API ofdm_LMS_phase_tracking2_sptr
ofdm_make_LMS_phase_tracking2( int vlen,
  std::vector< int > const & pilot_subc,
  std::vector< int > const & nondata_blocks );

/*!
TODO: code cleanup
 */
class OFDM_API ofdm_LMS_phase_tracking2 : public gr_sync_block
{
private:

  ofdm_LMS_phase_tracking2( int vlen,
    std::vector< int > const & pilot_subc,
    std::vector< int > const & nondata_blocks );

  int  d_vlen;

  float d_acc_gamma;    //! gradient estimate accumulator
  float d_acc_b;        //! offset estimate accumulator

  int d_pcount; //! No. of pilot subcarriers
  int d_blk;    //! OFDM block counter, reset at frame start

  std::vector< bool >  d_nondata_block;
  std::vector< float > d_pilot_tone;
  std::vector< int >   d_pilot;
  std::vector< bool >  d_is_pilot;
  std::vector< float > d_gamma_coeff;
  std::vector< float > d_acc_phase;

  void
  init_LMS_phasetracking(
      const std::vector<int> &pilot_tones,
      const std::vector<int> &nondata_block );

  inline void
  LMS_phasetracking( gr_complex const * in, gr_complex * out );

public:

  static ofdm_LMS_phase_tracking2_sptr
  create( int vlen,
    std::vector< int > const & pilot_subc,
    std::vector< int > const & nondata_blocks );

  virtual ~ofdm_LMS_phase_tracking2() {};

  int
  work(
    int                         noutput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_LMS_PHASE_TRACKING2_H_ */
