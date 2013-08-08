/*
 * util_random.cpp
 *
 *  Created on: 24.02.2009
 *      Author: koppers
 */

#include <ofdm/util_random.h>
#include <iostream>
#include <fstream>

using namespace std;

CRandom::CRandom()
:d_count(0)
{
  srand(0);
  /*ofstream testfile("random.txt",ofstream::out);
  for (int i=0; i<16384; ++i)
    testfile << (int)(rand()%2);
  testfile.close();*/
  d_randomlist.resize(0);
}

CRandom::~CRandom()
{
  // TODO Auto-generated destructor stub
}

void CRandom::load_from_file(string filename)
{
  d_randomlist.resize(0);
  ifstream myfile(filename.c_str(),ifstream::in);
  while (myfile.good())
  {
    d_randomlist.push_back(myfile.get()-48);
  }
  myfile.close();
  d_iterator=d_randomlist.begin();
}

void CRandom::generate(unsigned int no_items)
{
  d_randomlist.resize(0);
  for (int i=0; i<no_items; ++i)
  {
    srand(i);
    d_randomlist.push_back(rand()%2);
  }
  d_iterator=d_randomlist.begin();
}

void CRandom::reset()
{
  d_iterator=d_randomlist.begin();
}

unsigned char CRandom::rand_bit()
{
  d_iterator++;
  if (d_iterator==d_randomlist.end())
    d_iterator=d_randomlist.begin();
  return *d_iterator;
}
