#ifndef INCLUDED_OFDM_TRIGGER_SURVEILLANCE_H_
#define INCLUDED_OFDM_TRIGGER_SURVEILLANCE_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_sync_block.h>

class ofdm_trigger_surveillance;
typedef boost::shared_ptr<ofdm_trigger_surveillance> ofdm_trigger_surveillance_sptr;
OFDM_API ofdm_trigger_surveillance_sptr ofdm_make_trigger_surveillance (int ideal_distance, int max_shift);

/*!

 */
class OFDM_API ofdm_trigger_surveillance : public gr_sync_block
{
  private:
    friend OFDM_API ofdm_trigger_surveillance_sptr ofdm_make_trigger_surveillance (int ideal_distance, int max_shift);

    ofdm_trigger_surveillance (int ideal_distance, int max_shift);

    long long  d_ideal_distance;
    long long  d_max_shift;
    long long d_dist;
    unsigned long long d_lost;
    bool d_first;

  public:
    virtual ~ofdm_trigger_surveillance() {};

    unsigned long long lost_triggers() { return d_lost; };
    void reset_counter() { d_lost = 0; };

    int work (int noutput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_TRIGGER_SURVEILLANCE_H_ */
