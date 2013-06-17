#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <gr_io_signature.h>
#include "ofdm_corba_power_src_sv.h"

#include "corba_push_consumer.h"

#include <iostream>
#include <stdexcept>

#define DEBUG 0

ofdm_corba_power_src_sv_sptr 
ofdm_make_corba_power_src_sv(int isubcarriers, std::string sevent_channel, 
    std::string snameservice_ip, std::string snameservice_port,
    bool hack1)
{
  return ofdm_corba_power_src_sv_sptr(new ofdm_corba_power_src_sv( isubcarriers, 
      sevent_channel, snameservice_ip, snameservice_port, hack1 ));
}


void 
ofdm_corba_power_src_sv::forecast(int noutput_items, 
    gr_vector_int &ninput_items_required)
{
  if(d_qdata.empty())
    ninput_items_required[0] = 1;
  else
    ninput_items_required[0] = 0;
}


ofdm_corba_power_src_sv::ofdm_corba_power_src_sv(int isubcarriers, 
    std::string sevent_channel, std::string snameservice_ip, 
    std::string snameservice_port, bool hack1 )

  : gr_block("corba_power_src_sv",
           gr_make_io_signature (1, 1, sizeof(short)),
           gr_make_io_signature (1, 1, sizeof(float)*isubcarriers)),
           
  d_isubcarriers(isubcarriers), 
  d_sevent_channel(sevent_channel), 
  d_snameservice_ip(snameservice_ip), 
  d_snameservice_port(snameservice_port),
  
  d_hack1(hack1)
  
{
  
	d_push_consumer = get_corba_push_consumer_singleton(d_snameservice_ip, 
	    d_snameservice_port);
	
	d_push_consumer->set_owner("corba_power_src_sv");
	
}

int 
ofdm_corba_power_src_sv::general_work(
    int noutput_items,
    gr_vector_int &ninput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items )
{
  const short *in = static_cast<const short*>(input_items[0]);
  float *out = static_cast<float*>(output_items[0]);

  

  if( d_qdata.empty() ){
    
    for( int i = 0; i < ninput_items[0]; ++i ){
      
      if(DEBUG)
        std::cout << "Power_src asks for ID: " << in[i] << std::endl;

  	  
      corba_push_consumer::value_ptr config_data = 
         d_push_consumer->get_tx_config(in[i],true);

//  	  ofdm_ti::tx_config_data*  config_data = 
//  	      d_push_consumer->get_tx_config( in[i], true );

  	  //stop, if ID was not found or max. output items were produced
  	  if( config_data == 0 ){
  	    
  		break;
  		  
  	  } else {
  	    
  	      if( config_data->power_map.length() != (unsigned)d_isubcarriers ){
  	        throw std::runtime_error("[PowerMapSrc] Error: received power"\
  	                                 " map vector with false length");
  	      }
  	      
  	      int mul_id = config_data->id_blocks;
  	      int mul_data = config_data->data_blocks;
  	      
  	      if( d_hack1 ){ // FIXME dirty hack
  	        mul_id = 1;
  	        mul_data = 1;
  	      }
  	      
  	      
  		  //1st produce ID map(s)
  		  for(unsigned short i = 0; i < (mul_id * d_isubcarriers); ++i)
  		  {
  		    d_qdata.push(1);
  		  }

  		  //2nd add real maps
  		  for(int k = 0; k < mul_data; ++k)
  		  {
            for(int j = 0; j < d_isubcarriers; ++j)
            {
              d_qdata.push(config_data->power_map[j]);
            }
  		  }


  		  //3rd remove input item and set ireturn_items
  		  consume_each(1);
  		  
  		  if(DEBUG)
  		    std::cout << "Consume input element" << std::endl;
  		  
  	  } // if config_data == 0
  	  
    } // for-loop
    
    if(DEBUG)
      std::cout << "Power_src consumed"
                << " elements and new queue size is " 
                << d_qdata.size()/d_isubcarriers << std::endl;
  
  } // if d_qdata.empty()


  if( d_qdata.empty() ){
    if(DEBUG)
      std::cout << "Power_src produces " << 0 << " elements"<< std::endl;

    return 0;
  }

  int produced = std::min( noutput_items,
         static_cast<int>( d_qdata.size() ) / d_isubcarriers );

  for( int p = 0; p < produced*d_isubcarriers; ++p ){
    out[p] = d_qdata.front();
    d_qdata.pop();
  }
  
  if(DEBUG)
    std::cout << "Power_src produces " << produced << " elements"<< std::endl;

  return produced;
}

ofdm_corba_power_src_sv::~ofdm_corba_power_src_sv()
{
}

bool ofdm_corba_power_src_sv::start()
{
  d_push_consumer->subscribe_event_channel(d_sevent_channel);
  return true;
}

bool ofdm_corba_power_src_sv::stop()
{
  std::cout << "[corbapowersrc] shutdown consumer" << std::endl;
  d_push_consumer->shutdown();
  return true;
}
