/*
 * util_random.h
 *
 *  Created on: 24.02.2009
 *      Author: koppers
 */

#ifndef UTIL_RANDOM_H_
#define UTIL_RANDOM_H_

#include <cstdlib>
#include <string>
#include <list>

class CRandom
{
private:
  unsigned int d_count;
  std::list<unsigned char> d_randomlist;
  std::list<unsigned char>::iterator d_iterator;
public:
  CRandom();
  void reset();
  void load_from_file(std::string filename);
  void generate(unsigned int no_items);
  unsigned char rand_bit();
  virtual
  ~CRandom();
};

#endif /* UTIL_RANDOM_H_ */
