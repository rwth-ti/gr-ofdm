#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <boost/thread/once.hpp>

#include <ctime>

#include <ofdmi_shared_generator.h>

static boost::once_flag f=BOOST_ONCE_INIT; 
static shared_generator_sptr shared_generator;


void init_func()
{
  unsigned int seed = static_cast<unsigned int>( std::time( 0 ) );
  shared_generator_sptr t( new shared_generator_type( seed ) );
  shared_generator = t;
}


shared_generator_sptr
get_shared_generator( void )
{
  boost::call_once( &init_func, f );
  
  return shared_generator;
}
