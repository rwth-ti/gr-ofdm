/*
 * ofdm_vector_element.h
 *
 *  Created on: 01.02.2012
 *      Author: schmitz
 */

#ifndef INCLUDED_OFDM_VECTOR_ELEMENT_H_
#define INCLUDED_OFDM_VECTOR_ELEMENT_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>
#include <gr_sync_block.h>

#include <vector>

class ofdm_vector_element;
typedef boost::shared_ptr<ofdm_vector_element> ofdm_vector_element_sptr;

OFDM_API ofdm_vector_element_sptr ofdm_make_vector_element (int vlen, int element);

class OFDM_API ofdm_vector_element : public gr_sync_block
{
    friend OFDM_API ofdm_vector_element_sptr
        ofdm_make_vector_element (int vlen, int element);

    private:
    int d_vlen;
    int d_element;

    protected:
    ofdm_vector_element (int vlen, int element);

    public:
    int work (int noutput_items,
            gr_vector_const_void_star &input_items,
            gr_vector_void_star &output_items);

    void set_element(const int element);
};

#endif /* INCLUDED_OFDM_VECTOR_ELEMENT_H_ */
