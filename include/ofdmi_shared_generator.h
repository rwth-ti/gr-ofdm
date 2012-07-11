#ifndef OFDMI_SHARED_GENERATOR_H_
#define OFDMI_SHARED_GENERATOR_H_

#include <boost/random.hpp>
#include <boost/shared_ptr.hpp>

typedef boost::mt19937 shared_generator_type;
typedef boost::shared_ptr<shared_generator_type> shared_generator_sptr;

shared_generator_sptr
get_shared_generator( void );

#endif /*OFDMI_SHARED_GENERATOR_H_*/
