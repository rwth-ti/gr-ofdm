
/* $Id$ */

#ifndef C_INTERPROCESS_H
#define C_INTERPROCESS_H

#include <boost/interprocess/managed_shared_memory.hpp>
#include <boost/interprocess/sync/named_mutex.hpp>
#include <boost/interprocess/sync/scoped_lock.hpp>

#include <string>
#include <iostream>
#include <cstring>      // std::memcpy
#include <stdexcept>
#include <sstream>
#include <algorithm>
//#include <gnuradio/gr_complex.h>

using namespace boost::interprocess;

typedef struct
{
  double x      __attribute__((packed));
  double y      __attribute__((packed));
} c_point;

struct c_interprocess
{
  typedef unsigned long size_type;

  // TODO: use separate mutex per shared memory !!!
  // FIXME: someone st* a* ... deleted the mutex

  c_interprocess(size_type bufferlength, size_type buffercount,
    std::string my_shm_id = std::string())
  :  d_mutex( open_or_create
            , mutex_id.c_str() ),
     d_bufferlength(bufferlength),
     d_buffercount(buffercount)
  {
    if( my_shm_id.size() == 0 )
      d_shm_id = shm_id;
    else
      d_shm_id = my_shm_id;
    std::cout << "IPC using shared mem id " << d_shm_id << std::endl;

    d_shmsize=sizeof(c_point)*d_buffercount*d_bufferlength+d_bufferlength*d_buffercount*sizeof(char);
    //shared_memory_object::remove(shm_id.c_str());
    d_shm=new managed_shared_memory(
                  open_or_create
                , d_shm_id.c_str()
                , d_shmsize*2 );
    std::cout << "Sizeof(c_point): " << sizeof(c_point) << "sizeof(char):" << sizeof(char) << "\n";
    std::cout << "Init IPC with Bufferlength of " << d_bufferlength << ". Its Size is " << d_shm->get_size()<< " and free are " << d_shm->get_free_memory() << "\n";
    try
    {
      std::cout << "Trying to allocate space of " << d_bufferlength*d_buffercount*sizeof(c_point) << " Bytes!\n";
      d_pointbuffer = d_shm->find_or_construct< c_point >
                  ( shared_buffer_id.c_str() )
                  [ d_bufferlength*d_buffercount ]
                    ();
      std::cout << "Now Freememory is " << d_shm->get_free_memory() << "\n";
      std::cout << "Trying to allocate space of " << d_bufferlength*d_buffercount*sizeof(char) << " Bytes!\n";
      d_putbuffer = d_shm->find_or_construct< char >
                  ( put_buffer_id.c_str() )
                  [ d_bufferlength*d_buffercount ]
                    ();
      std::cout << "Now Freememory is " << d_shm->get_free_memory() << "\n";
      d_bufferstending = d_shm->find_or_construct< size_type >
                         ( buffers_tend_id.c_str() )
                         (0);
      d_curbuffer = d_shm->find_or_construct< size_type >
                   ( buffers_cur_id.c_str() )
                   (0);
    }
    catch( bad_alloc const & ex )
    {
      std::cerr << "Caught " << ex.what() << std::endl;
      if( d_shm->get_size() < d_shmsize )
      {
        std::cerr << "Shared memory size too smal"
            "l, try to reset IPC"
                  << std::endl;
      }
      throw;
    }
    catch( ... )
    {
      std::cerr << "failed" << std::endl;
      throw;
    }
    std::cout << "Finished init\n";
  } // detail()


  void cleanup_shm()
  {
    shared_memory_object::remove(d_shm_id.c_str());
  }
  void
  add_points( c_point const* in, const char* where_to_put )
  {
    //where_to_put is array of char which says for each in-point, where to put it
    try
    {
      //std::cout << "Locking...\n";
      //scoped_lock< mutex_type > lock( d_mutex );

      std::memcpy(&d_pointbuffer[(*d_curbuffer)*d_bufferlength],in,d_bufferlength*sizeof(c_point));
      if (where_to_put!=NULL)
        std::memcpy(&d_putbuffer[(*d_curbuffer)*d_bufferlength],where_to_put,d_bufferlength*sizeof(char));
      else
      {
        int last_buffer=(*d_curbuffer-1+d_buffercount)%d_buffercount;
        std::memcpy(&d_putbuffer[(*d_curbuffer)*d_bufferlength],&d_putbuffer[last_buffer*d_bufferlength],d_bufferlength*sizeof(char));
      }
      (*d_curbuffer)++;
      if ((*d_curbuffer)==d_buffercount)
        (*d_curbuffer)=0;
      (*d_bufferstending)++;
    }
    catch( interprocess_exception const & ex )
    {
      std::stringstream msg;
      msg << "Interprocess Exception: " << ex.what();
      throw std::runtime_error( msg.str() );
    }
  }

  void
  read_points( c_point * dst, unsigned char * where_to_put )
  {
    //std::cout << "IPC read_points CurBuffer; " << *d_curbuffer << " Tending Buffers: "<< *d_bufferstending <<"\n";
    try
    {
      //scoped_lock< mutex_type > lock( d_mutex )
      unsigned char buffer_to_read=(*d_curbuffer)-d_buffercount;
      buffer_to_read%=d_buffercount;
      if (*d_bufferstending>0)
        {
            std::memcpy(dst,&d_pointbuffer[(buffer_to_read)*d_bufferlength],d_bufferlength*sizeof(c_point));
            std::memcpy(where_to_put,&d_putbuffer[(buffer_to_read)*d_bufferlength],d_bufferlength*sizeof(char));
            (*d_bufferstending)--;
        }
    }
    catch( interprocess_exception const & ex )
    {
      std::stringstream msg;
      msg << "Interprocess Exception: " << ex.what();
      throw std::runtime_error( msg.str() );
    }
  }

  void
  reset()
  {
    std::cout << "reset IPC\n";
    shared_memory_object :: remove( d_shm_id.c_str());
    named_mutex :: remove( mutex_id.c_str() );
  }


  static c_interprocess *
  create(size_type bufferlength, size_type buffercount, std::string shm_id = std::string() )
  {
    std::cout << "create IPC\n";
    c_interprocess * ptr = 0;
    try
    {
      ptr = new c_interprocess(bufferlength, buffercount, shm_id);
      return ptr;
    }
    catch( interprocess_exception const & ex )
    {
      std::stringstream msg;
      msg << "Interprocess Exception: " << ex.what();
      if( ptr ) delete ptr;

      throw std::runtime_error( msg.str() );
    }
    catch( ... )
    {
      if( ptr ) delete ptr;
      throw;
    }
  }

  size_type d_shmsize;

  // name definitions of shared objects
  static std::string const shm_id;
  static std::string const shared_buffer_id;
  static std::string const put_buffer_id;
  static std::string const mutex_id;
  static std::string const buffers_tend_id;
  static std::string const buffers_cur_id;

  std::string d_shm_id;


  size_type *d_curbuffer; //Buffer to write in
  size_type *d_bufferstending;
  typedef named_mutex mutex_type;



  managed_shared_memory *d_shm;
  mutex_type d_mutex;


  size_type d_bufferlength;
  size_type d_buffercount;

  // shared objects
  c_point * d_pointbuffer;
  char * d_putbuffer;
};


#endif /* C_INTERPROCESS_H */
