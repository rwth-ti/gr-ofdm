#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include "ofdm_corba_id_filter.h"

#include "corba_push_consumer.h"

#include <iostream>

ofdm_corba_id_filter_sptr
ofdm_make_corba_id_filter(std::string sevent_channel,
        std::string snameservice_ip, std::string snameservice_port,
        int max_trials)
{
    return ofdm_corba_id_filter_sptr(new ofdm_corba_id_filter(sevent_channel,
            snameservice_ip, snameservice_port, max_trials));
}

ofdm_corba_id_filter::ofdm_corba_id_filter(std::string sevent_channel,
        std::string snameservice_ip, std::string snameservice_port,
        int max_trials) :
    gr_sync_block("corba_id_filter", gr_make_io_signature(1, 1, sizeof(short)),
            gr_make_io_signature(1, 1, sizeof(short))), d_sevent_channel(
            sevent_channel), d_snameservice_ip(snameservice_ip),
            d_snameservice_port(snameservice_port), d_max_trials(max_trials),
            d_trials(0)
{
    d_push_consumer = get_corba_push_consumer_singleton(d_snameservice_ip,
            d_snameservice_port);
    d_push_consumer->set_owner("corba_id_filter");
    set_history(2);
}

int
ofdm_corba_id_filter::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
{
    const short *in = static_cast<const short*> (input_items[0]);
    short *out = static_cast<short*> (output_items[0]);

    if (noutput_items < 2) {
        return (0);
    }

    for (int i = 0; i < noutput_items-1; ++i) {
        short id = in[i+1];
        if (in[i] == in[i+2]) {
            id = in[i];
        }

        corba_push_consumer::value_ptr config_data =
                d_push_consumer->get_tx_config(id);

        //    ofdm_ti::tx_config_data *config_data = d_push_consumer->get_tx_config(id);
        if (!config_data) {
            //      if(d_trials < d_max_trials){
            //        ++d_trials;
            //        return i;
            //      }

            id = d_push_consumer->get_latest_id();
            std::cout << "-";
        }
        else {
            std::cout << "+";// << in[i+1];
            //      d_trials = 0;
        }

        out[i] = id;
    }

    return noutput_items-1;
}

bool
ofdm_corba_id_filter::start()
{
    d_push_consumer->subscribe_event_channel(d_sevent_channel);
    return true;
}

bool
ofdm_corba_id_filter::stop()
{
    std::cout << "[corbaidfilter] shutdown consumer" << std::endl;
    d_push_consumer->shutdown();
    return true;
}
