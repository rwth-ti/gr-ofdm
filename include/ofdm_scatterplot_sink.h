
/* $Id$ */

#ifndef INCLUDED_OFDM_SCATTERPLOT_SINK_H_
#define INCLUDED_OFDM_SCATTERPLOT_SINK_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>// forward declarations
#include <util_ipc.h>
#include <gr_block.h>

#include <string>

class ofdm_scatterplot_sink;
typedef boost::shared_ptr<ofdm_scatterplot_sink>
  ofdm_scatterplot_sink_sptr;

OFDM_API ofdm_scatterplot_sink_sptr
ofdm_make_scatterplot_sink( int vlen, std::string shm_id = std::string() );

/*!

 */
class OFDM_API ofdm_scatterplot_sink : public gr_block
{
private:

  ofdm_scatterplot_sink( int vlen, std::string shm_id );

  int  d_vlen;

  c_interprocess* d_shm;
  c_point *temp_buffer;

  void
  forecast( int noutput_items,
    gr_vector_int &ninput_items_required );

public:

  static ofdm_scatterplot_sink_sptr
  create( int vlen, std::string shm_id );

  virtual ~ofdm_scatterplot_sink() {};

  int
  general_work(
    int                         noutput_items,
    gr_vector_int             & ninput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_SCATTERPLOT_SINK_H_ */
