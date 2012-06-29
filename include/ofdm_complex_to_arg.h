#ifndef INCLUDED_OFDM_COMPLEX_TO_ARG_H_
#define INCLUDED_OFDM_COMPLEX_TO_ARG_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_sync_block.h>

class ofdm_complex_to_arg;
typedef boost::shared_ptr<ofdm_complex_to_arg> ofdm_complex_to_arg_sptr;
OFDM_API ofdm_complex_to_arg_sptr ofdm_make_complex_to_arg (unsigned int vlen = 1);

/*!
 * \brief arg of complex value
 *
 * This class computes the argument of the complex-valued input. Contrarily
 * to the available standard class, we employ std::arg()-function. This
 * provides a higher precision but is slower than the approximation used
 * in GNU Radio standard block.
 */
class OFDM_API ofdm_complex_to_arg : public gr_sync_block
{
  private:
    friend OFDM_API ofdm_complex_to_arg_sptr ofdm_make_complex_to_arg (unsigned int vlen);

    ofdm_complex_to_arg (unsigned int vlen);

    unsigned int  d_vlen;

  public:
    virtual ~ofdm_complex_to_arg() {};

    int work (int noutput_items,
              gr_vector_const_void_star &input_items,
              gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_COMPLEX_TO_ARG_H_ */
