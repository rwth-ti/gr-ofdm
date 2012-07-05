#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>

#include <ofdm_throughput_measure.h>
#include <gr_io_signature.h>

#include <cmath>
#ifdef HAVE_TIME_H
#include <time.h>
#endif

#include <string.h>

#include <iostream>
#include <algorithm>

ofdm_throughput_measure_sptr ofdm_make_throughput_measure (int itemsize)
{
  return ofdm_throughput_measure_sptr (new ofdm_throughput_measure (itemsize));
}

ofdm_throughput_measure::ofdm_throughput_measure (int itemsize)
  : gr_sync_block ("throughput_measure",
           gr_make_io_signature (1, 1, itemsize),
           gr_make_io_signature (1, 1, itemsize)),
  d_itemsize(itemsize), d_total_samples(0), d_init(false),
  d_min(-1), d_max(0), d_avg(0)
{
#ifdef HAVE_GETTIMEOFDAY
  gettimeofday(&d_start, 0);
#endif
}

int ofdm_throughput_measure::work (int noutput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  const char *in = static_cast<const char*>(input_items[0]);
  char *out = static_cast<char*>(output_items[0]);

#if defined(HAVE_GETTIMEOFDAY)
  if(!d_init) {
    gettimeofday(&d_start, 0);
    d_init=true;
  } else {
    struct timeval now;
    gettimeofday(&now, 0);
    long t_usec = now.tv_usec - d_start.tv_usec;
    long t_sec  = now.tv_sec - d_start.tv_sec;
    double t = (double)t_sec + (double)t_usec * 1e-6;
    if (t < 1e-6)    // avoid unlikely divide by zero
      t = 1e-6;

    double actual_samples_per_sec = d_total_samples / t;

    d_avg = 0.995 * d_avg + 0.005 * actual_samples_per_sec;
    if(d_min < 0)
      d_min = actual_samples_per_sec;
    else
      d_min = std::min(d_min,actual_samples_per_sec);
    d_max = std::max(d_max,actual_samples_per_sec);

    //std::cout << "samplerate " << actual_samples_per_sec << "/s" << std::endl;
  }
#endif

  d_total_samples += noutput_items;
  memcpy(out, in, noutput_items * d_itemsize);

  return noutput_items;
}
