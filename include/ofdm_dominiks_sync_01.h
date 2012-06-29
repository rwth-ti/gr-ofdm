
/* $Id: ofdm_dominiks_sync_01.h 923 2009-04-21 14:03:45Z auras $ */

#ifndef INCLUDED_OFDM_DOMINIKS_SYNC_01_H_
#define INCLUDED_OFDM_DOMINIKS_SYNC_01_H_

#include <ofdm_api.h>
#include "gr_block_fwd.h"// forward declarations
#include <gr_block.h>

class ofdm_dominiks_sync_01;
typedef boost::shared_ptr<ofdm_dominiks_sync_01>
  ofdm_dominiks_sync_01_sptr;

OFDM_API ofdm_dominiks_sync_01_sptr
ofdm_make_dominiks_sync_01( int vlen, int cplen );

/*!

 */
class OFDM_API ofdm_dominiks_sync_01 : public gr_block
{
private:

  ofdm_dominiks_sync_01( int vlen, int cplen );

  int  d_vlen;
  int  d_cplen;
  int  d_blocklen;   // vlen+cplen, provided for convenience

  int  d_state;      // Acquisition or Tracking

  int  d_avg_blocks; // average cyclic prefix autocorrelation
                     // over d_avg_blocks

  float d_sc_threshold; // preamble detection threshold
  float d_gi_threshold; // detection threshold

  int d_s0_max_ind_err; // max distance between SC and GI estimators' decisions
  int d_s1_gi_failures; // during tracking, failure = gi_val < threshold
  int d_s1_max_failures;// if more failures, recover (reenter acquisition)


  float * d_avg_gi_metric; // temporary buffer for GI ML estimator


  int d_index_decision; // Position within window that is end of OFDM block
  int d_hist;           // No. of minimum available input items
  int d_shift;          // Input delay

  float d_window_shift; // fractional shift decision
  float d_i_gain_shift; // gain/step size for integrating control loop

  unsigned long d_sample; // DEBUGGING sample counter


  /*! Enter acquisition state */

  void
  enter_state0();

  /*! Enter tracking state */

  void
  enter_state1();

  void
  forecast( int noutput_items,
    gr_vector_int &ninput_items_required );


  /*! Determine maximum input items to be processed
   *
   * Equals minimum available items of first three stream buffers.
   *
   * @param ninput_items Item count per stream
   * @return No. of items processable
   */

  inline
  int
  compute_min_ninput( gr_vector_int const & ninput_items ) const;


  /*! Determine maximum input items to be processed, respect multiple
   *
   * Equals minimum available items of first three stream buffers.
   *
   * @param ninput_items Item count per stream
   * @param multiple Return value is a multiple of this number
   * @return No. of items processable
   */

  inline
  int
  compute_min_ninput( gr_vector_int const & ninput_items,
    int const & multiple ) const;

  /*! Try to detect OFDM frame
   *
   * @param ind Peak index S&C metric
   * @param sc_val peak value
   * @param gi_metric Input for GI autocorrelator
   * @return
   */
  inline
  bool
  frame_detected( int const & ind, float const & sc_val,
    float const * const gi_metric );

  /*! In tracking state, compute autocorrelation at lag = index_decision
   *
   * This implementation currently uses the autocorrelator blocks in front
   * of the sync. Future implementation may mute these and compute the
   * values on their own, reducing the computational effort in the tracking
   * state.
   *
   * @param sc_metric
   * @param gi_metric
   * @param sc_val out
   * @param gi_val out
   */

  inline
  void
  s1_compute_metric_values(
    float const * const sc_metric, float const * const gi_metric,
    float & sc_val, float & gi_val ) const;


  /*! Check if we lost the synchronization during tracking and must recover
   *
   * Condition: if the GI metric value at the given index decision within
   * our window is below the threshold for several OFDM blocks, we will
   * re-enter the acquisition state.
   *
   * @param gi_val Value of autocorrelation of cyclic prefix at lag=index_dec
   * @return true = recover, false = we are fine
   */

  inline
  bool
  s1_must_recover( float const & gi_val );


  inline
  void
  s1_track_cyclic_prefix( float const * const sc_metric,
    float const * const gi_metric, float const & gi_val );

  //! DEBUGGING whitebox test
  inline
  void
  debug_samplectr_out( unsigned long * & trig_out, int const & i ) const;



public:

  bool start();

  static ofdm_dominiks_sync_01_sptr
  create( int vlen, int cplen );

  virtual ~ofdm_dominiks_sync_01();

  int
  general_work(
    int                         noutput_items,
    gr_vector_int             & ninput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_DOMINIKS_SYNC_01_H_ */
