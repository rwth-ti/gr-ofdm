/* -*- c++ -*- */
/* 
 * Copyright 2014 Institute for Theoretical Information Technology,
 *                RWTH Aachen University
 *                www.ti.rwth-aachen.de
 * 
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "allocation_src_impl.h"
#include <iostream>
#include <pmt/pmt.h>
#include <volk/volk.h>

#include <numeric>


namespace gr {
  namespace ofdm {

    allocation_src::sptr
    allocation_src::make(int subcarriers, int data_symbols, bool coding, char *address, char *fb_address)
    {
      return gnuradio::get_initial_sptr
        (new allocation_src_impl(subcarriers, data_symbols, coding, address, fb_address));
    }

    /*
     * The private constructor
     *
     * Description of output format:
     *
     * id: 0..255
     * bitcount: number of payload bits in a frame
     * bitloading: vector containing 2 vectors with bitloading for 1.: id and 2.: data
     * power: vector containing power allocation vectors for id symbol and every data symbol
     *
     */
    allocation_src_impl::allocation_src_impl(int subcarriers, int data_symbols, bool coding, char *address, char *fb_address)
        : gr::block("allocation_src",
                         gr::io_signature::make(0, 0, 0),
                         gr::io_signature::make(0, 0, 0))
        ,d_bitcount_out(2000)
        ,d_subcarriers(subcarriers)
        ,d_data_symbols(data_symbols)
        ,d_coding( coding )
        ,d_bitspermode( {1,2,3,4,6,8,9,10,12})
        ,d_modulbitspermode( {1,2,2,4,4,6,6,6,8} )
        ,d_modulbitcount_out(2000)
        ,d_allocation_scheme(CM)
        ,d_power_limit(subcarriers)
        ,d_data_rate(subcarriers*3)
        ,d_gap(6.6)
        ,d_amplitude_out(1.0 + 1.0i)
        ,d_amplitude_abs(1)

    {
        if (d_coding)
        {
            std::vector<int> out_sig(6);
            out_sig[0] = sizeof(short);                             // id
            out_sig[1] = sizeof(float)*subcarriers;                 // power
            out_sig[2] = sizeof(uint8_t)*subcarriers;               // bitloading
            out_sig[3] = sizeof(gr_complex);                        // amplitude
            out_sig[4] = sizeof(int);                               // uncoded bitcount
            out_sig[5] = sizeof(int);                               // coded bitcount
            set_output_signature(io_signature::makev(6,6,out_sig));
        }
        else
        {
            std::vector<int> out_sig(5);
            out_sig[0] = sizeof(short);                             // id
            out_sig[1] = sizeof(float)*subcarriers;                 // power
            out_sig[2] = sizeof(uint8_t)*subcarriers;               // bitloading
            out_sig[3] = sizeof(gr_complex);                        // amplitude
            out_sig[4] = sizeof(int);                               // bitcount
            set_output_signature(io_signature::makev(5,5,out_sig));
        }


        std::vector<uint8_t> bitloading_vec;
        std::vector<float> power_vec;
        // default data modulation scheme is BPSK
        for(int i=0;i<subcarriers;i++)
        {
            bitloading_vec.push_back(1);
        }
        // init power allocation vector
        for(int i=0;i<subcarriers;i++)
        {
            power_vec.push_back(1);
        }
        // generate allocation and allocation_out structures
        d_allocation.id = 0;
        d_allocation_out.id = 0;
        set_allocation(bitloading_vec,power_vec);

        for(int i=0;i<=256;i++)
        {
            d_amplitude.push_back(1.0);
        }

        d_inv_ones.resize(subcarriers,1.0);

        d_context = new zmq::context_t(1);
        d_socket = new zmq::socket_t(*d_context, ZMQ_PUB);
        d_socket->bind(address);
        std::cout << "allocation_src sending allocation on " << address << std::endl;

        d_context_feedback = new zmq::context_t(1);
        d_socket_feedback = new zmq::socket_t(*d_context_feedback, ZMQ_SUB);
        d_socket_feedback->connect(fb_address);
        d_socket_feedback->setsockopt(ZMQ_SUBSCRIBE, "", 0);
        std::cout << "allocation_src receiving feedback on" << fb_address << std::endl;

        //set_output_multiple((1+d_data_symbols));
        //set_output_multiple((1+d_data_symbols)*d_subcarriers);
        //set_min_output_buffer (3, 2*sizeof(gr_complex)*(1+d_data_symbols)*d_subcarriers);
        //set_max_output_buffer (3, 2*sizeof(gr_complex)*(1+d_data_symbols)*d_subcarriers);
        set_min_noutput_items((1+d_data_symbols));
        //set_max_noutput_items((1+d_data_symbols)*d_subcarriers);

        init_gap_map();
    }

    /*
     * Our virtual destructor.
     */
    allocation_src_impl::~allocation_src_impl()
    {
        delete(d_socket);
        delete(d_context);
        delete(d_socket_feedback);
        delete(d_context_feedback);

    }

    void
    allocation_src_impl::send_allocation()
    {
        // use pmt to serialize allocation struct (this is VERY slow)
//        pmt::pmt_t pmt_id, pmt_bitloading, pmt_power;
//        pmt_id = pmt::from_long(d_allocation.id);
//        pmt_bitloading = pmt::init_u8vector(d_allocation.bitloading.size(),d_allocation.bitloading);
//        pmt_power = pmt::init_c32vector(d_allocation.power.size(),d_allocation.power);
//        pmt::pmt_t pmt_tuple;
//        pmt_tuple = pmt::make_tuple();
//        pmt_tuple = pmt::make_tuple(pmt_id, pmt_bitloading, pmt_power);
//        std::string msg_str = pmt::serialize_str(pmt_tuple);
//
//        // copy to zmq message and send
//        zmq::message_t msg(msg_str.size()+1);
//        memcpy(msg.data(), (void *)msg_str.c_str(), msg_str.size()+1);

        // inverse Power
        d_inv_power = d_allocation.power;
        for(int i = 0; i< d_subcarriers; i++)
        {
            if(d_inv_power[i]==0)
                d_inv_power[i]=1;
        }
        volk_32f_x2_divide_32f(&d_inv_power[0], &d_inv_ones[0], &d_inv_power[0], d_subcarriers);

        // just write datagram to message with raw copying (much faster)
        zmq::message_t msg(sizeof(d_allocation.id)
                           + d_subcarriers*sizeof(d_allocation.bitloading[0])
                           + d_subcarriers*sizeof(d_inv_power[0]));
        memcpy(msg.data(), &d_allocation.id, sizeof(d_allocation.id));
        memcpy((uint8_t*)msg.data()+sizeof(d_allocation.id),
                                 &d_allocation.bitloading[0],
                                 d_subcarriers*sizeof(d_allocation.bitloading[0]));
        memcpy((uint8_t*)msg.data()+sizeof(d_allocation.id)+d_subcarriers*sizeof(d_allocation.bitloading[0]),
                                 &d_inv_power[0],
                                 d_subcarriers*sizeof(d_inv_power[0]));
        d_socket->send(msg, ZMQ_NOBLOCK);
    }


    void
    allocation_src_impl::recv_snr()
    {
        zmq::pollitem_t items[] = { { *d_socket_feedback, 0, ZMQ_POLLIN, 0 } };
        bool msg_received = true;
        while(msg_received) {
            // poll with timeout 0
            zmq::poll (&items[0], 1, 0);
            //  If we got a msg, process
            if (items[0].revents & ZMQ_POLLIN) {
                // Receive data
                zmq::message_t msg;
                d_socket_feedback->recv(&msg);

                // copy message into allocation struct and find id to put into buffer
                d_feedback_information.id = *(short*)msg.data();
                d_feedback_information.snr.clear();
                d_feedback_information.snr.assign((float*)((char*)msg.data()+sizeof(short)),
                                                              (float*)((char*)msg.data()
                                                              +sizeof(short)
                                                              +d_subcarriers*sizeof(float)));

                for(int i= 0;i<d_subcarriers; i++)
                {
                    d_feedback_information.snr[i] = pow(10, d_feedback_information.snr[i]/10);
                    //d_feedback_information.snr[i] /= d_amplitude[d_feedback_information.id];
                }

                switch (d_allocation_scheme)
                {
                    case CM:
                        d_amplitude_abs=1;
                        break;
                    case RA:
                        d_amplitude_abs=1;
                        calculate_bitloading_RA();
                        break;
                    case MA:
                        calculate_bitloading_MA();
                        break;
                    case LA:
                        d_amplitude_abs=1;
                        calculate_bitloading_loading_adaptive();
                        break;
                    default:
                        std::cout<<"Choose Allocation Scheme!"<<std::endl;
                }

            } else {
                msg_received = false;
            }
        }
    }

    void
    allocation_src_impl::calculate_bitloading()
    {
        std::vector<uint8_t> bitloading_vec;
        for(int i = 0; i < d_subcarriers; i++)
        {
            if(d_feedback_information.snr[i]<6.78)
                bitloading_vec.push_back(0);
            else if(d_feedback_information.snr[i]<9.79)
                bitloading_vec.push_back(1);
            else if(d_feedback_information.snr[i]<14.78)
                bitloading_vec.push_back(2);
            else if(d_feedback_information.snr[i]<16.54)
                bitloading_vec.push_back(3);
            else if(d_feedback_information.snr[i]<19.58)
                bitloading_vec.push_back(4);
            else if(d_feedback_information.snr[i]<22.55)
                bitloading_vec.push_back(5);
            else if(d_feedback_information.snr[i]<25.49)
                bitloading_vec.push_back(6);
            else if(d_feedback_information.snr[i]<26.25)
                bitloading_vec.push_back(7);
            else
                bitloading_vec.push_back(8);

        }

        int sum_of_elems = 0;
        for(std::vector<uint8_t>::iterator j=bitloading_vec.begin();j!=bitloading_vec.end();++j)
            sum_of_elems += *j;

        if(sum_of_elems > 100)
        {
            d_bitcount_out = sum_of_elems*d_data_symbols;

            d_allocation.bitloading = bitloading_vec;

            // clear and write bitloading output vector
            d_allocation_out.bitloading.clear();
            // insert data symbol modulation at the end ONCE
            d_allocation_out.bitloading.insert(d_allocation_out.bitloading.end(), bitloading_vec.begin(), bitloading_vec.end());
        }


    }


    void
    allocation_src_impl::calculate_bitloading_RA()
    {
        float level=0;
        int counter = 0;
        d_allocation.power.clear();
        std::vector<float>::iterator it;
        std::vector<float> inv_snr;

        for(int i = 0; i < d_subcarriers; i++)
        {
            if(d_feedback_information.snr[i]>7.6)//&& d_feedback_information.snr[i]< 40)
            {
                inv_snr.push_back( d_gap / d_feedback_information.snr[i]); 
                counter ++;
            }
            else inv_snr.push_back(0);

        }

        while(1)
        {
            level = (d_power_limit + std::accumulate( inv_snr.begin(), inv_snr.end(), 0.))/counter;
            counter--;
            if(counter < 0.75 * d_subcarriers) break;



            it = std::max_element(inv_snr.begin(), inv_snr.end());
            if(*it > level)
            {
                *it = 0;
            }
            else break;
        }

        if(counter< 0.75 * d_subcarriers)
        {
            // default data modulation scheme is BPSK
            d_allocation.bitloading.clear();
            d_allocation.bitloading.assign(d_subcarriers,1);
            // init power allocation vector
            d_allocation.power.clear();
            d_allocation.power.assign(d_subcarriers,1);
        }
        else
        {

        //scale power to 1 and send scaling factor to time domain
        //d_amplitude_abs = ((level*counter)-std::accumulate( inv_snr.begin(), inv_snr.end(), 0.))/d_subcarriers;

        //for(it =  inv_snr.begin(); it!= inv_snr.end(); it++)
        for(int i = 0; i < d_subcarriers; i++)
        {
            if(inv_snr[i]!=0)
            {
                d_allocation.power.push_back(sqrt(level - inv_snr[i])/d_amplitude_abs);
                //if(d_feedback_information.snr[i] > 1659.6) d_allocation.bitloading[i] = 8;
                //else 
                    d_allocation.bitloading[i] = (char)log2(1 + ((d_allocation.power[i]*d_feedback_information.snr[i])/ d_gap ));
                    if(d_allocation.bitloading[i]>8) d_allocation.bitloading[i]=8;
            }
            else
            {
                d_allocation.power.push_back(0);
                d_allocation.bitloading[i] = 0;
            }
        }
        }

        // clear and write power output vector
        d_allocation_out.power = d_allocation.power;

        // clear and write bitloading output vector
        d_allocation_out.bitloading.clear();
        // insert data symbol modulation at the end ONCE
        //d_allocation_out.bitloading.insert(d_allocation_out.bitloading.end(), d_allocation.bitloading.begin(), d_allocation.bitloading.end());
        d_allocation_out.bitloading=d_allocation.bitloading;

        int sum_of_elems = 0;
        for(std::vector<uint8_t>::iterator j=d_allocation.bitloading.begin();j!=d_allocation.bitloading.end();++j)
            sum_of_elems += *j;
        d_bitcount_out = sum_of_elems*d_data_symbols;

    }

    void
    allocation_src_impl::calculate_bitloading_MA()
    {
        std::vector<float> snr_sort;
        float G = 0;
        float level;
        int it = 0;
        d_allocation.power.clear();
        d_allocation.bitloading.clear();

        //Inizialise
        for(int i = 0; i < d_subcarriers; i++)
        {
            snr_sort.push_back(d_feedback_information.snr[i]);
            G+= log2(snr_sort[i]);
        }
        //if(G < d_data_rate) return;
        if(G < d_subcarriers)
        {
            // default data modulation scheme is BPSK
            d_allocation.bitloading.clear();
            d_allocation.bitloading.assign(d_subcarriers,1);
            // init power allocation vector
            d_allocation.power.clear();
            d_allocation.power.assign(d_subcarriers,1);

            // clear and write power output vector
            d_allocation_out.power = d_allocation.power;

            // clear and write bitloading output vector
            d_allocation_out.bitloading.clear();
            // insert data symbol modulation at the end ONCE
            d_allocation_out.bitloading.insert(d_allocation_out.bitloading.end(), d_allocation.bitloading.begin(), d_allocation.bitloading.end());

            int sum_of_elems = 0;
            for(std::vector<uint8_t>::iterator j=d_allocation.bitloading.begin();j!=d_allocation.bitloading.end();++j)
                sum_of_elems += *j;
            d_bitcount_out = sum_of_elems*d_data_symbols;

            return;
        }
        std::sort(snr_sort.begin(), snr_sort.end());
        level = d_gap * pow(2, ((d_data_rate-G)/d_subcarriers));

        //Get Water Level
        while(level < (d_gap / snr_sort[it]))
        {
            if(it>50)
            {
                return;
            }
            G-= log2(snr_sort[it]);
            it++;
            level = d_gap * pow(2, (d_data_rate-G) / (d_subcarriers - it));
        }

        //scale power to 1 and send scaling factor to time domain
        d_amplitude_abs=0;
        for(int i = 0; i < d_subcarriers; i++)
        {
            if(level > (d_gap /d_feedback_information.snr[i] ))
                d_amplitude_abs += level - d_gap/d_feedback_information.snr[i];
        }
        d_amplitude_abs =sqrt(d_amplitude_abs/d_subcarriers);
        

        //Allocate
        for(int i = 0; i < d_subcarriers; i++)
        {
            if(d_feedback_information.snr[i] < snr_sort[it])
            {
                d_allocation.power.push_back( 0);
                d_allocation.bitloading.push_back( 0);
            }
            else
            {
                d_allocation.power.push_back( sqrt((level - d_gap/d_feedback_information.snr[i]))/ d_amplitude_abs );
                if(d_allocation.power[i] > 5) d_allocation.power[i] = 5;
                d_allocation.bitloading.push_back(  (char)log2(1 + ((d_allocation.power[i]*d_amplitude_abs*d_feedback_information.snr[i])/ d_gap )));
                if(d_allocation.bitloading[i] > 8) d_allocation.bitloading[i] = 8;
            }
        }


        // clear and write power output vector
        d_allocation_out.power = d_allocation.power;

        // clear and write bitloading output vector
        d_allocation_out.bitloading.clear();
        // insert data symbol modulation at the end ONCE
        d_allocation_out.bitloading.insert(d_allocation_out.bitloading.end(), d_allocation.bitloading.begin(), d_allocation.bitloading.end());

        int sum_of_elems = 0;
        for(std::vector<uint8_t>::iterator j=d_allocation.bitloading.begin();j!=d_allocation.bitloading.end();++j)
            sum_of_elems += *j;
        d_bitcount_out = sum_of_elems*d_data_symbols;
    }


    void
    allocation_src_impl::calculate_bitloading_loading_adaptive()
    {
        int count=0;

        for(int i = 0; i < d_subcarriers; i++)
        {
            d_allocation.bitloading[i] = (char)log2(1 + ((d_feedback_information.snr[i])/ d_gap ));
            if(d_allocation.bitloading[i]>8) d_allocation.bitloading[i]=8;
        }

        for(int i = 0; i < d_subcarriers; i++)
        {
            if(d_allocation.bitloading[i]==0) count++;
        }

        if(count>30)
        {
            // default data modulation scheme is BPSK
            d_allocation.bitloading.clear();
            d_allocation.bitloading.assign(d_subcarriers,1);
        }

        // init power allocation vector
        d_allocation.power.clear();
        d_allocation.power.assign(d_subcarriers,1);

        // clear and write power output vector
        d_allocation_out.power = d_allocation.power;

        // clear and write bitloading output vector
        d_allocation_out.bitloading.clear();
        d_allocation_out.bitloading=d_allocation.bitloading;

        int sum_of_elems = 0;
        for(std::vector<uint8_t>::iterator j=d_allocation.bitloading.begin();j!=d_allocation.bitloading.end();++j)
            sum_of_elems += *j;
        d_bitcount_out = sum_of_elems*d_data_symbols;

    }


    void
    allocation_src_impl::init_gap_map()
    {
        d_gap_map[0.00705930124968]=17.6861667633;
        d_gap_map[0.00145799992606]=19.6811962128;
        d_gap_map[0.000147700062371]=21.6702270508;
        d_gap_map[0.49996471405]=-65.7821578979;
        d_gap_map[0.499103397131]=-4.07673358917;
        d_gap_map[0.493141263723]=-2.78180670738;
        d_gap_map[0.47038424015]=-0.984365165234;
        d_gap_map[0.420552909374]=1.47982990742;
        d_gap_map[0.360013961792]=3.14165472984;
        d_gap_map[0.295007318258]=5.20545005798;
        d_gap_map[0.232737958431]=6.37246417999;
        d_gap_map[0.177854716778]=7.8739490509;
        d_gap_map[0.128163740039]=9.68508338928;
        d_gap_map[0.0842084139585]=11.6712675095;
        d_gap_map[0.0474758036435]=13.6737070084;
        d_gap_map[0.0214185025543]=15.6705417633;
        d_gap_map[4.7000826271e-06]=23.6781864166;
        d_gap_map[1.00000001335e-10]=25.6884059906;

    }


    void
    allocation_src_impl::set_allocation_scheme(int allocation_scheme)
    {
        d_allocation_scheme = (d_allocation_scheme_enum) allocation_scheme;
    }

    void
    allocation_src_impl::set_data_rate(int data_rate)
    {
        d_data_rate = data_rate;
    }

    void
    allocation_src_impl::set_power_limit(int power_limit)
    {
        d_power_limit = power_limit;
    }

    void
    allocation_src_impl::set_gap(float gap)
    {
        //d_gap = pow(10, gap/10.0);
        d_gap = pow(10,((d_gap_map.lower_bound(gap)->second)/10))/(pow(2,4)-1);
    }


    void
    allocation_src_impl::set_allocation(std::vector<uint8_t> bitloading,
                                        std::vector<float> power)
    {
        gr::thread::scoped_lock guard(d_mutex);
        d_allocation.bitloading = bitloading;
        d_allocation.power = power;

        // clear and write bitloading output vector
        d_allocation_out.bitloading.clear();
        // insert data symbol modulation at the end ONCE
        d_allocation_out.bitloading.insert(d_allocation_out.bitloading.end(), bitloading.begin(), bitloading.end());

        // clear and write power output vector
        d_allocation_out.power = power;

        int sum_of_elems = 0;
        int modul_sum_of_elems = 0;
        if (d_coding)
        {
			for(std::vector<uint8_t>::iterator j=bitloading.begin();j!=bitloading.end();++j)
			{
				//std::cout << "Bitcount_src bits: " <<  (d_bitspermode[*j-1]) << std::endl;
				sum_of_elems += d_bitspermode[*j-1];
				modul_sum_of_elems += d_modulbitspermode[*j-1];
			}

			d_bitcount_out = sum_of_elems*d_data_symbols/2;
			d_modulbitcount_out = modul_sum_of_elems*d_data_symbols;
			//std::cout << "d_bitcount_out: " << d_bitcount_out << std::endl;
        }
        else
        {
        	for(std::vector<uint8_t>::iterator j=bitloading.begin();j!=bitloading.end();++j)
            sum_of_elems += *j;
        	d_bitcount_out = sum_of_elems*d_data_symbols;
        }

    }


    int
    allocation_src_impl::general_work(int noutput_items,
                                      gr_vector_int &ninput_items,
                                      gr_vector_const_void_star &input_items,
                                      gr_vector_void_star &output_items)

    {
        gr::thread::scoped_lock guard(d_mutex);

        short *out_id = (short *) output_items[0];
        float *out_power = (float *) output_items[1];
        uint8_t *out_bitloading = (uint8_t *) output_items[2];
        gr_complex *out_amplitude = (gr_complex *) output_items[3];
        int *out_bitcount = (int *) output_items[4];
        int *out_modulbitcount = (int *) output_items[5];


        if (d_coding)
			for (int i = 0; i < (noutput_items); i++) {
				// send the allocation to Rx
				send_allocation();

				// now generate outputs
				out_id[i] = d_allocation_out.id;
				out_bitcount[i] = d_bitcount_out;
				// Bit count for mapper and data before coding is different
				out_modulbitcount[i] = d_modulbitcount_out;
				//FIXME: probably dirty hack
				// output vectors data (bpsk is used for id)
				int bl_idx = i*d_subcarriers;
				memcpy(&out_bitloading[bl_idx], &d_allocation_out.bitloading[0], sizeof(uint8_t)*d_subcarriers);
				// output 1 vector for id and the rest for data
				int p_idx = i*d_subcarriers;
				memcpy(&out_power[p_idx], &d_allocation_out.power[0], sizeof(float)*d_subcarriers);
	            memcpy(&out_amplitude[i], &d_amplitude_out, sizeof(gr_complex));

				//increase frame id, [0..255]
				d_allocation.id++;
				if (d_allocation.id > 255) {
					d_allocation.id = 0;
				}
				d_allocation_out.id = d_allocation.id;
			}
        else
        for (int i = 0; i < (noutput_items); i++) {
            // send the allocation to Rx
            recv_snr();
            send_allocation();

            d_amplitude_out = (1.0+1.0i)*d_amplitude_abs;
            d_amplitude[d_allocation_out.id]=d_amplitude_abs;   

			// now generate outputs
			out_id[i] = d_allocation_out.id;
			out_bitcount[i] = d_bitcount_out;
			//FIXME: probably dirty hack
			// output vectors data (bpsk is used for id)
			int bl_idx = i*d_subcarriers;
			memcpy(&out_bitloading[bl_idx], &d_allocation_out.bitloading[0], sizeof(uint8_t)*d_subcarriers);
			// output 1 vector for id and the rest for data
			int p_idx = i*d_subcarriers;
			memcpy(&out_power[p_idx], &d_allocation_out.power[0], sizeof(float)*d_subcarriers);
                        volk_32f_x2_multiply_32f(&out_power[p_idx], &out_power[p_idx],&out_power[p_idx], d_subcarriers);
                        memcpy(&out_amplitude[i], &d_amplitude_out, sizeof(gr_complex));
			//increase frame id, [0..255]
			d_allocation.id++;
			if (d_allocation.id > 255) {
				d_allocation.id = 0;
			}
			d_allocation_out.id = d_allocation.id;
		}


        return noutput_items;
    }
  } /* namespace ofdm */
} /* namespace gr */

