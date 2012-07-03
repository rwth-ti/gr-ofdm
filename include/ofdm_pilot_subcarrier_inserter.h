
/* $Id: ofdm_pilot_subcarrier_inserter.h 611 2008-10-20 15:26:52Z auras $ */

#ifndef INCLUDED_OFDM_PILOT_SUBCARRIER_INSERTER_H_
#define INCLUDED_OFDM_PILOT_SUBCARRIER_INSERTER_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>// forward declarations
#include <gr_sync_block.h>

class ofdm_pilot_subcarrier_inserter;
typedef boost::shared_ptr<ofdm_pilot_subcarrier_inserter>
  ofdm_pilot_subcarrier_inserter_sptr;

OFDM_API ofdm_pilot_subcarrier_inserter_sptr
ofdm_make_pilot_subcarrier_inserter( int vlen,
  const std::vector<gr_complex> &symbols, const std::vector<int> &subc_index );

/*!

 */
class OFDM_API ofdm_pilot_subcarrier_inserter : public gr_sync_block
{
private:

  ofdm_pilot_subcarrier_inserter( int vlen,
    const std::vector<gr_complex> &symbols,
    const std::vector<int> &subc_index );

  int   d_vlen;
  std::vector<gr_complex>   d_symbols;
  std::vector<int>   d_partition;

public:

  static ofdm_pilot_subcarrier_inserter_sptr
  create( int vlen, const std::vector<gr_complex> &symbols,
    const std::vector<int> &subc_index );

  virtual ~ofdm_pilot_subcarrier_inserter() {};

  int
  work(
    int                         noutput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_PILOT_SUBCARRIER_INSERTER_H_ */
