#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <gr_io_signature.h>
#include <ofdm_reference_data_source_ib.h>

#include <algorithm>
#include <iostream>

#define DEBUG 0

ofdm_reference_data_source_ib_sptr ofdm_make_reference_data_source_ib(const std::vector<char> &ref_data)
{
    return ofdm_reference_data_source_ib_sptr(new ofdm_reference_data_source_ib(ref_data));
}

void ofdm_reference_data_source_ib::forecast(int noutput_items, gr_vector_int &ninput_items_required)
{
    ninput_items_required[0] = 1;
    ninput_items_required[1] = 1;
}

ofdm_reference_data_source_ib::ofdm_reference_data_source_ib(const std::vector<char> &ref_data)
    : gr_block("reference_data_source_ib",
            gr_make_io_signature2 (2, 2, sizeof(short),
                sizeof(unsigned int)),
            gr_make_io_signature (1, 1, sizeof(char))),
    d_ref_data(ref_data),
    d_vec_pos(0),
    d_produced(0),
    d_last_id(-2)
{
}

int ofdm_reference_data_source_ib::general_work(
        int noutput_items,
        gr_vector_int &ninput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
{
    const short *in_id = static_cast<const short*>(input_items[0]);
    const unsigned int *in_cnt = static_cast<const unsigned int*>(input_items[1]);
    char *out = static_cast<char*>(output_items[0]);

    if(DEBUG)
        std::cout << "[dref.src " << unique_id() << "] entered, state "
            << "nin=" << ninput_items[0] << " nout=" << noutput_items
            << " d_produced=" << d_produced
            << " in_cnt[0]=" << in_cnt[0]
            << std::endl;

    if(in_cnt[0] == 0){

        std::cerr << "warning: bitcount = 0" << std::endl;
        consume_each(1);
        return 0;

    } else if(in_cnt[0] > d_produced){
        //how many bits should be produced?
        int nout = std::min(in_cnt[0]-d_produced,(unsigned int)noutput_items);

        if(DEBUG)
            std::cout << "produce " << nout << " items" << std::endl;

        //copy as many bits as needed
        for (int i = 0 ; i < nout; ++i) {
            //reset if end of input vector reached
            if ((unsigned int)d_vec_pos >= d_ref_data.size()) {
                d_vec_pos = 0;
            }
            out[i] = d_ref_data[d_vec_pos];
            d_vec_pos++;
        }
        d_produced += nout;

        // if frame end reached restart counter and call consume
        if(d_produced >= in_cnt[0]){
            d_produced = 0;
            consume_each(1);
            if(DEBUG)
                std::cout << "consume input value" << std::endl;
            // if new ID reset input data to keep sync
            if(d_last_id != in_id[0]) {
                d_last_id = in_id[0];
                d_vec_pos = 0;
            }
        }

        return nout;

    }

    assert(false && "should never get here");
    return -1;

    // for unscyncronized long random sequence uncomment and comment above
    //    for (int i = 0 ; i < noutput_items; i++)
    //    {
    //        if ((unsigned int)d_vec_pos >= d_ref_data.size()) {
    //            d_vec_pos = 0;
    //        }
    //        out[i] = d_ref_data[d_vec_pos];
    //        d_vec_pos++;
    //    }
    //
    //    consume_each(1);
    //    return noutput_items;
}
