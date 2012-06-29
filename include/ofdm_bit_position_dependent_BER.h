
/* $Id: ofdm_bit_position_dependent_BER.h 1106 2009-08-15 15:07:55Z auras $ */

#ifndef INCLUDED_OFDM_BIT_POSITION_DEPENDENT_BER_H_
#define INCLUDED_OFDM_BIT_POSITION_DEPENDENT_BER_H_

#include <ofdm_api.h>
#include "gr_block_fwd.h"// forward declarations
#include <boost/shared_array.hpp>
#include <string>
#include <vector>
#include <gr_block.h>


class ofdm_bit_position_dependent_BER;
typedef boost::shared_ptr<ofdm_bit_position_dependent_BER>
  ofdm_bit_position_dependent_BER_sptr;

OFDM_API ofdm_bit_position_dependent_BER_sptr
ofdm_make_bit_position_dependent_BER( std::string filename_prefix );

/*!

 */
class OFDM_API ofdm_bit_position_dependent_BER : public gr_block
{
private:

  ofdm_bit_position_dependent_BER( std::string filename_prefix );

  std::string   d_filename_prefix;

  void
  forecast( int noutput_items,
    gr_vector_int &ninput_items_required );


  typedef unsigned int cntr_t;
  typedef boost::shared_array< cntr_t > cntr_vec_t;

  typedef unsigned int index_t;

  index_t               d_index;
  index_t               d_cntr_len;
  cntr_vec_t            d_cntr;


  index_t               d_file_idx;

  bool                  d_min_reached;

  void flush();

public:

  bool stop();

  static ofdm_bit_position_dependent_BER_sptr
  create( std::string filename_prefix );

  virtual ~ofdm_bit_position_dependent_BER() { flush(); };

  std::vector< int > get_cntr_vec() const;

  int
  general_work(
    int                         noutput_items,
    gr_vector_int             & ninput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_BIT_POSITION_DEPENDENT_BER_H_ */
