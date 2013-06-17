#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <gr_io_signature.h>
#include "ofdm_corba_assignment_src_sv.h"

#include "corba_push_consumer.h"

#include <iostream>

#define DEBUG 0

ofdm_corba_assignment_src_sv_sptr 
ofdm_make_corba_assignment_src_sv(int istation_id, int isubcarriers, 
    std::string sevent_channel, std::string snameservice_ip, 
    std::string snameservice_port)
{
  return ofdm_corba_assignment_src_sv_sptr(new ofdm_corba_assignment_src_sv(
      istation_id, isubcarriers, sevent_channel, snameservice_ip, 
      snameservice_port));
}


void ofdm_corba_assignment_src_sv::forecast(int noutput_items, 
    gr_vector_int &ninput_items_required)
{
  if(d_qdata.empty())
    ninput_items_required[0] = 1;
  else
    ninput_items_required[0] = 0;
}


ofdm_corba_assignment_src_sv::ofdm_corba_assignment_src_sv(int istation_id, 
    int isubcarriers, std::string sevent_channel, std::string snameservice_ip,
    std::string snameservice_port)

  : gr_block("corba_assignment_src_sv",
           gr_make_io_signature (1, 1, sizeof(short)),
           gr_make_io_signature (1, 1, sizeof(char)*isubcarriers)),
           
  d_istation_id(istation_id), 
  d_isubcarriers(isubcarriers), 
  d_sevent_channel(sevent_channel), 
  d_snameservice_ip(snameservice_ip), 
  d_snameservice_port(snameservice_port)
  
{
  
  d_push_consumer = get_corba_push_consumer_singleton(d_snameservice_ip, 
      d_snameservice_port);
  
  d_push_consumer->set_owner("corba_assignment_src_sv");
  
}

int 
ofdm_corba_assignment_src_sv::general_work(
    int noutput_items,
    gr_vector_int &ninput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  
  const short *in = static_cast<const short*>(input_items[0]);
  char *out = static_cast<char*>(output_items[0]);

  if(d_qdata.empty()){
    
    for(int i = 0; i < ninput_items[0]; ++i){
      
      if(DEBUG)
        std::cout << "Assignment_src asks for ID: " << in[i] << std::endl;

  	  corba_push_consumer::value_ptr config_data = 
  	    d_push_consumer->get_tx_config(in[i],true);

  	  //stop, if ID was not found or max. output items were produced
  	  if( config_data == 0 ){
  	    
		break;
  		  
  	  } else {
  	    
        //1st produce ID map(s)
        for(unsigned short i = 0; i < d_isubcarriers; ++i){
          d_qdata.push(0);
        }
        
        //2nd add data maps
        for(int j = 0; j < d_isubcarriers; ++j){
          
          if(config_data->assignment_map[j] == d_istation_id)
            d_qdata.push(1);
          else
            d_qdata.push(0);
          
        }
        
        //3rd remove input item
        consume_each(1);
  		  
  	  } // if config_data == 0
  	  
    } // for-loop
    
  } // if d_qdata.empty()

  if(d_qdata.empty()){
    
    if(DEBUG)
      std::cout << "Assignment_src produces " << 0 << " elements"<< std::endl;

    return 0;
    
  }

  
  int produced = std::min( noutput_items,
         static_cast<int>( d_qdata.size() )/d_isubcarriers );

  
  for(int p = 0; p < produced*d_isubcarriers; ++p){
    out[p] = d_qdata.front();
    d_qdata.pop();
  }
  
  

  if(DEBUG)
    std::cout << "Assignment_src produces " << produced << " elements"<< std::endl;

  return produced;
}

ofdm_corba_assignment_src_sv::~ofdm_corba_assignment_src_sv()
{
}

bool ofdm_corba_assignment_src_sv::start()
{
  d_push_consumer->subscribe_event_channel(d_sevent_channel);
  return true;
}

bool ofdm_corba_assignment_src_sv::stop()
{
  std::cout << "[corbaassignmentsrc] interrupt push consumer" << std::endl;
  d_push_consumer->interrupt();
  return true;
}
