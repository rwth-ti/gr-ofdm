#ifndef INCLUDED_OFDM_BER_MEASUREMENT_H_
#define INCLUDED_OFDM_BER_MEASUREMENT_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_sync_block.h>

class ofdm_ber_measurement;
typedef boost::shared_ptr<ofdm_ber_measurement> ofdm_ber_measurement_sptr;
OFDM_API ofdm_ber_measurement_sptr ofdm_make_ber_measurement (unsigned long long sliding_window_length);

/*!
 * \brief Bit error rate measurement
 *
 * Input:
 * - demodulated data stream, 1 bit per byte, inband flag 2 allowed
 * - reference data stream
 *
 * Output:
 * - BER performance estimate value per input byte
 *
 * We count the bit errors inside the sliding window. The bit error rate estimate
 * is accessible through get_ber().
 */
class OFDM_API ofdm_ber_measurement : public gr_sync_block
{
  private:
    friend OFDM_API ofdm_ber_measurement_sptr ofdm_make_ber_measurement (unsigned long long sliding_window_length);

    ofdm_ber_measurement (unsigned long long sliding_window_length);

    unsigned long long d_sliding_window_length;
    long long int d_bits_in_win;
    long long int d_errs_in_win;

  public:
    virtual ~ofdm_ber_measurement() {};

    float get_ber(void)
    {
      return static_cast<float>(d_errs_in_win)/d_bits_in_win;
    }

    int work (int noutput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_BER_MEASUREMENT_H_ */
