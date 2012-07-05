#ifndef INCLUDED_OFDM_THROUGHPUT_MEASURE_H_
#define INCLUDED_OFDM_THROUGHPUT_MEASURE_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations

#include <gr_sync_block.h>
#ifdef HAVE_SYS_TIME_H
#include <sys/time.h>
#endif

class ofdm_throughput_measure;
typedef boost::shared_ptr<ofdm_throughput_measure> ofdm_throughput_measure_sptr;
OFDM_API ofdm_throughput_measure_sptr ofdm_make_throughput_measure (int itemsize);

/*!

 */
class OFDM_API ofdm_throughput_measure : public gr_sync_block
{
  private:
    friend OFDM_API ofdm_throughput_measure_sptr ofdm_make_throughput_measure (int itemsize);

    ofdm_throughput_measure (int itemsize);

    int       d_itemsize;
    double    d_total_samples;
    bool      d_init;
#ifdef HAVE_SYS_TIME_H
    struct timeval  d_start;
#endif

    double d_min, d_max, d_avg;

  public:
    virtual ~ofdm_throughput_measure() {};

    double get_max() const  { return d_max; }
    double get_min() const  { return d_min; }
    double get_avg() const  { return d_avg; }

    int work (int noutput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_THROUGHPUT_MEASURE_H_ */
