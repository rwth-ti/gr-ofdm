#ifndef INCLUDED_OFDM_SKIP_H_
#define INCLUDED_OFDM_SKIP_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_block.h>

class ofdm_skip;
typedef boost::shared_ptr<ofdm_skip> ofdm_skip_sptr;
OFDM_API ofdm_skip_sptr ofdm_make_skip(std::size_t itemsize, unsigned int blocklen);

/*!
 * \brief Skip items
 *
 * This block skips items within an item block of size \param blocklen. You
 * specify the items to be skipped via the public interface skip(no).
 *
 * First input is the item stream, first output the filtered stream.
 * Second input is a trigger (char) that should be 1 for the first item in
 * an item block, and 0 else. If connected, the second output is a trigger
 * stream with same properties as the first input, but its block length
 * diminuished by the number of skipped items.
 */
class OFDM_API ofdm_skip : public gr_block
{
  private:
    friend OFDM_API ofdm_skip_sptr ofdm_make_skip(std::size_t itemsize, unsigned int blocklen);

    ofdm_skip(std::size_t itemsize, unsigned int blocklen);

    std::size_t   d_itemsize;
    unsigned int d_blocklen;
    unsigned int d_item;
    unsigned int d_skip;

    std::vector<bool> d_items;
    std::vector<bool> d_first_item;

    void forecast (int noutput_items, gr_vector_int &ninput_items_required);

    int fixed_rate_ninput_to_noutput(int ninput);
    int fixed_rate_noutput_to_ninput(int noutput);

  public:
    virtual ~ofdm_skip() {};

    void skip(unsigned int no);

    int general_work (int noutput_items,
      gr_vector_int &ninput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
    
    virtual int noutput_forecast( gr_vector_int &ninput_items, 
        int available_space, int max_items_avail,
        std::vector<bool> &input_done );
};

#endif /* INCLUDED_OFDM_SKIP_H_ */
