
/* $Id$ */

#ifndef INCLUDED_OFDM_IMGTRANSFER_SRC_H_
#define INCLUDED_OFDM_IMGTRANSFER_SRC_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>// forward declarations
#include <util_bmp.h>
#include <util_random.h>
#include <string>
#include <vector>
#include <gr_block.h>

class ofdm_imgtransfer_src;
typedef boost::shared_ptr<ofdm_imgtransfer_src>
  ofdm_imgtransfer_src_sptr;

OFDM_API ofdm_imgtransfer_src_sptr
ofdm_make_imgtransfer_src( std::string filename );

/*!

 */
class OFDM_API ofdm_imgtransfer_src : public gr_block
{
private:

  ofdm_imgtransfer_src( std::string filename );

  std::string   		d_filename;

  int d_pos;
  unsigned int d_imgpos, d_bitcounter, d_bytecounter, d_color;
  unsigned int d_bla;

  unsigned int d_bitcount;

  std::vector<unsigned char>		d_headerbuffer;
  std::vector<unsigned char>		d_buffer;

  CRandom random_generator;

  Bitmap d_bitmap;

  void
  forecast( int noutput_items,
    gr_vector_int &ninput_items_required );

public:

  static ofdm_imgtransfer_src_sptr
  create( std::string filename );

  virtual ~ofdm_imgtransfer_src() {};

  int
  general_work(
    int                         noutput_items,
    gr_vector_int             & ninput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_IMGTRANSFER_SRC_H_ */
