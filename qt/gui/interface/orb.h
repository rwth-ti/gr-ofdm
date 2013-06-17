#ifndef ORB_H_
#define ORB_H_

#include <boost/shared_ptr.hpp>

#include <string>
#include <stdexcept>

#include <tao/ORB.h>

//class orb_wrapper;

class orb_wrapper
{
public:

  static boost::shared_ptr<orb_wrapper>
  create( std::string nameservice = std::string("corbaloc:rir:/NameService") );

  CORBA::ORB_ptr get_ORB();

  CORBA::Object_ptr resolve( std::string name );


  class detail;


  ~orb_wrapper() {};


private:


  boost::shared_ptr<detail> d_detail;

  orb_wrapper( boost::shared_ptr<detail> );

};

struct name_resolution_failed : public std::runtime_error
{
  std::string req_name;

  name_resolution_failed( std::string x )
    : std::runtime_error( "Name resolution failed" ),
      req_name( x ) {};

  ~name_resolution_failed() throw() {};
};

struct obj_non_existing : public std::runtime_error
{
  std::string req_name;

  obj_non_existing( std::string x )
    : std::runtime_error( "Object (" + x + ") does not exist"),
      req_name( x ) {};

  ~obj_non_existing() throw() {};
};

#endif /*ORB_H_*/
