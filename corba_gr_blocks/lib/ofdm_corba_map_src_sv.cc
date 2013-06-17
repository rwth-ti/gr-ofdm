#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <gr_io_signature.h>
#include "ofdm_corba_map_src_sv.h"

#include "corba_push_consumer.h"

#include <iostream>

ofdm_corba_map_src_sv_sptr ofdm_make_corba_map_src_sv(int isubcarriers, std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port)
{
  return ofdm_corba_map_src_sv_sptr(new ofdm_corba_map_src_sv( isubcarriers, sevent_channel, snameservice_ip, snameservice_port));
}


void ofdm_corba_map_src_sv::forecast(int noutput_items, gr_vector_int &ninput_items_required)
{
  if(d_qdata.empty())
    ninput_items_required[0] = 1;
  else
    ninput_items_required[0] = 0;
}


ofdm_corba_map_src_sv::ofdm_corba_map_src_sv(int isubcarriers, std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port)
  : gr_block("corba_map_src_sv",
           gr_make_io_signature (1, 1, sizeof(short)),
           gr_make_io_signature2(1, 2, isubcarriers*sizeof(char), 
                                       sizeof(int))),
  d_isubcarriers(isubcarriers), 
  d_sevent_channel(sevent_channel), 
  d_snameservice_ip(snameservice_ip), 
  d_snameservice_port(snameservice_port)
{

  d_push_consumer = get_corba_push_consumer_singleton(d_snameservice_ip, d_snameservice_port);
  
  d_push_consumer->set_owner("corba_map_src_sv");
}


int ofdm_corba_map_src_sv::general_work(
    int noutput_items,
    gr_vector_int &ninput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  const short *in = static_cast<const short*>(input_items[0]);
  char *out = static_cast<char*>(output_items[0]);
  unsigned int consumed = 0;
  
  int *count = 0;
  if(output_items.size() > 1)
    count = static_cast<int*>(output_items[1]);

  // TODO: output buffer gross genug?

  if(d_qdata.empty()){
    for(int i = 0; i < ninput_items[0]; ++i)
    {
  	  //Produce a total of "BLOCKS_PER_FRAME" maps per input id
#ifdef DEBUG_OUT
  	  std::cout << "Map_src asks for ID: " << in[i] << std::endl;
#endif
  	  
      corba_push_consumer::value_ptr config_data = 
        d_push_consumer->get_tx_config(in[i],true);

//  	  ofdm_ti::tx_config_data* config_data = d_push_consumer->get_tx_config(in[i],true);

  	  //stop, if ID was not found or max. output items were produced
  	  if(config_data == NULL)
  	  {
  		  break;
  	  }
  	  else
  	  {
  		  //1st produce ID map(s)
  		  for(unsigned short k = 0; k < (config_data->id_blocks * d_isubcarriers); ++k)
  		  {
  			  //out[act_out_pos++] = 1;
  			  d_qdata.push(1);
  		  }
  		  
  		  if(count){
  		    
            for(int j = 0; j < d_isubcarriers; ++j)
            {
                //out[act_out_pos++] = config_data->mod_map[j];
              d_qdata.push(config_data->mod_map[j]);
            }
            
            d_cqdata.push(config_data->id_blocks);
            d_cqdata.push(config_data->data_blocks);
            
  		  }else{
  		    
    		  //2nd add real maps
    		  for(int k = 0; k < config_data->data_blocks; ++k)
    		  {
    			  for(int j = 0; j < d_isubcarriers; ++j)
    			  {
    				  //out[act_out_pos++] = config_data->mod_map[j];
    			    d_qdata.push(config_data->mod_map[j]);
    			  }
    		  }
    		  
  		  }


  		  //3rd remove input item and set ireturn_items
  		  //ireturn_items += config_data->data_blocks + config_data->id_blocks;
  		  consume_each(1);
  		  ++consumed;
  	  }
    }
#ifdef DEBUG_OUT
  std::cout << "Map_src consumed " << consumed << " elements and new queue size is " << d_qdata.size()/d_isubcarriers << std::endl;
#endif
  }

  if(d_qdata.empty()){
#ifdef DEBUG_OUT
    std::cout << "Map_src produces " << 0 << " elements"<< std::endl;
#endif
    return 0;
  }

  int produced = std::min(noutput_items,static_cast<int>(d_qdata.size())/d_isubcarriers);

  for(int p = 0; p < produced*d_isubcarriers; ++p){
    out[p] = d_qdata.front();
    d_qdata.pop();
  }
  
  if(count){
    for(int p = 0; p < produced; ++p){
      count[p] = d_cqdata.front();
      d_cqdata.pop();
    }
    
    assert(d_cqdata.size()*d_isubcarriers == d_qdata.size());
  }

#ifdef DEBUG_OUT
  std::cout << "Map_src produces " << produced << " elements"<< std::endl;
#endif

  return produced;
}

ofdm_corba_map_src_sv::~ofdm_corba_map_src_sv()
{
}

bool ofdm_corba_map_src_sv::start()
{
  d_push_consumer->subscribe_event_channel(d_sevent_channel);
  return true;
}

bool ofdm_corba_map_src_sv::stop()
{
  std::cout << "[corbamapsrc] shutdown consumer" << std::endl;
  d_push_consumer->shutdown();
  return true;
}
