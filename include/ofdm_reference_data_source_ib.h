#ifndef INCLUDED_OFDM_REFERENCE_DATA_SOURCE_IB_H_
#define INCLUDED_OFDM_REFERENCE_DATA_SOURCE_IB_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <vector>

class ofdm_reference_data_source_ib;
typedef boost::shared_ptr<ofdm_reference_data_source_ib> ofdm_reference_data_source_ib_sptr;
OFDM_API ofdm_reference_data_source_ib_sptr ofdm_make_reference_data_source_ib(const std::vector<int> &ref_data);

/*!
 * \param ref_data Unpacked byte data, lower 8 bits used
 */
class OFDM_API ofdm_reference_data_source_ib : public gr_block
{
  private:
    friend ofdm_reference_data_source_ib_sptr ofdm_make_reference_data_source_ib(const std::vector<int> &ref_data);

    ofdm_reference_data_source_ib(const std::vector<int> &ref_data);

    std::vector<char> d_ref_data;
    std::vector<char>::const_iterator d_bpos;
    std::vector<char>::size_type d_produced;

    void forecast(int noutput_items, gr_vector_int &ninput_items_required);

  public:
    virtual ~ofdm_reference_data_source_ib() {};

    int general_work(
      int noutput_items,
      gr_vector_int &ninput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_REFERENCE_DATA_SOURCE_IB_H_ */
