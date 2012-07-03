
/* $Id: ofdm_LMS_phase_tracking3.h 923 2009-04-21 14:03:45Z auras $ */

#ifndef INCLUDED_OFDM_LMS_PHASE_TRACKING3_H_
#define INCLUDED_OFDM_LMS_PHASE_TRACKING3_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>// forward declarations
#include <gr_sync_block.h>

#include <vector>

class ofdm_LMS_phase_tracking3;
typedef boost::shared_ptr<ofdm_LMS_phase_tracking3>
  ofdm_LMS_phase_tracking3_sptr;

OFDM_API ofdm_LMS_phase_tracking3_sptr
ofdm_make_LMS_phase_tracking3( int vlen,
  std::vector< int > const & pilot_subc,
  std::vector< int > const & nondata_blocks,
  std::vector< gr_complex > const & pilot_subcarriers);

/*!
TODO: code cleanup
 */
class OFDM_API ofdm_LMS_phase_tracking3 : public gr_sync_block
{
private:

  ofdm_LMS_phase_tracking3( int vlen,
    std::vector< int > const & pilot_subc,
    std::vector< int > const & nondata_blocks,
    std::vector< gr_complex > const & pilot_subcarriers);

  int  d_vlen;

  float d_acc_gamma;    //! gradient estimate accumulator
  float d_acc_b;        //! offset estimate accumulator

  int d_pcount; //! No. of pilot subcarriers
  int d_blk;    //! OFDM block counter, reset at frame start
  int d_in_da;    //! iterator

  std::vector< bool >  d_nondata_block;
  std::vector< gr_complex > d_pilot_tone;
  std::vector< int >   d_pilot;
  std::vector< bool >  d_is_pilot;
  std::vector< float > d_gamma_coeff;
  std::vector< float > d_acc_phase;
  std::vector< float > d_phase_last;
  //std::vector< gr_complex const> d_ina;

  void
  init_LMS_phasetracking(
      const std::vector<int> &pilot_tones,
      const std::vector<int> &nondata_block );

  inline void
  LMS_phasetracking( gr_complex const * in, gr_complex * out );

public:

  static ofdm_LMS_phase_tracking3_sptr
  create( int vlen,
    std::vector< int > const & pilot_subc,
    std::vector< int > const & nondata_blocks,
    std::vector< gr_complex > const & pilot_subcarriers);

  virtual ~ofdm_LMS_phase_tracking3() {};

  int
  work(
    int                         noutput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_LMS_PHASE_tracking3_H_ */
