#ifndef OFDMI_TICTOC_HPP_
#define OFDMI_TICTOC_HPP_

#include <inttypes.h>
#include <list>
#include <algorithm>
#include <fcntl.h>
#include <string>

extern "C" {
void cpuid_x86 (unsigned int op, unsigned int result[4]);
};

extern "C" {
   __inline__ uint64_t rdtsc() {
   uint32_t lo, hi;
   unsigned int  op=0, regs[4];
   cpuid_x86 (op, regs); // serialize
   /* We cannot use "=A", since this would use %rax on x86_64 */
   __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
   return (uint64_t)hi << 32 | lo;
   }
}

static uint64_t g_tsc_start;
static std::list<std::pair<int, uint64_t> > g_ticks;

static inline void
tic()
{
  g_tsc_start = rdtsc();
}

static inline void
toc( int id = 0 )
{
  uint64_t stop = rdtsc();
  uint64_t diff = stop-g_tsc_start;
  g_ticks.push_back( std::make_pair( id, diff ) );
}

static inline void
save_ticks_to_file( std::string filename )
{
  FILE* f = fopen(filename.c_str(),"wb");
  
  for( std::list<std::pair<int,uint64_t> >::const_iterator iter = g_ticks.begin();
      iter != g_ticks.end(); 
      ++iter) 
  {
    
    fwrite(&(iter->first),1,sizeof(int),f);
    fwrite(&(iter->second),1,sizeof(uint64_t),f);
    
  }
  
  fclose(f);
}

#endif /*OFDMI_TICTOC_HPP_*/
