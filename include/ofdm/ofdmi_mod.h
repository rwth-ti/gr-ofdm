#ifndef ofdmi_MOD_H_
#define ofdmi_MOD_H_

#include <gnuradio/types.h>
#include <gnuradio/math.h>

#include <vector>
#include <cmath>
#include <algorithm>
#include <iostream>
#include <stdexcept>

void ofdmi_make_psk(std::vector<gr_complex> &constellation, unsigned char bits);
void ofdmi_make_qam(std::vector<gr_complex> &constellation, unsigned char bits);


std::vector< std::vector< std::vector< char > > >
ofdmi_generate_128qam_lut();

std::vector< std::vector< std::vector< char > > >
ofdmi_generate_32qam_lut();


class modulation_scheme
{
protected:
  typedef std::vector<gr_complex>  cplx_vector;
  typedef std::vector<cplx_vector> bit_partition;
  typedef std::vector<char>        bit_vector;
  typedef std::vector<bit_vector>  bit_matrix;

  cplx_vector   d_constellation;
  bit_matrix    d_ind_to_bits;
  bit_partition d_soft0;
  bit_partition d_soft1;
  float         d_mindist;

public:
  inline modulation_scheme(int bits) {
    assert(bits > 0 && bits <= 8);

    if(bits < 4){ //PSK
      ofdmi_make_psk(d_constellation, bits);
    }else{ //QAM
      ofdmi_make_qam(d_constellation, bits);
    }

    assert(d_constellation.size() == pow(2,bits));

    d_ind_to_bits.resize(d_constellation.size());
    d_soft0.resize(bits);
    d_soft1.resize(bits);
    for(cplx_vector::size_type ind = 0; ind < d_constellation.size(); ++ind){
      for(int b = bits-1; b >= 0; --b){
        char bit = (ind >> b) & 1;
        d_ind_to_bits[ind].push_back(bit);
        if(bit == 0){
          d_soft0[bits-1-b].push_back(d_constellation[ind]);
        }else{
          d_soft1[bits-1-b].push_back(d_constellation[ind]);
        }
      }
    }

    float mindist = INFINITY;
    for(cplx_vector::size_type x = 0; x < d_constellation.size(); ++x){
      for(cplx_vector::size_type y = 0; y < d_constellation.size(); ++y){
        if(x == y)
          continue;
        float dist = std::abs(d_constellation[x]-d_constellation[y]);
        mindist = std::min(mindist,dist);
      }
    }
    d_mindist = mindist/2.0;
  }


  virtual inline ~modulation_scheme() {};


  const cplx_vector& get_constellation( void ) const
  {
    return d_constellation;
  }
};

template <int bits>
class generic_modulation_scheme : public modulation_scheme
{
public:
  inline generic_modulation_scheme() : modulation_scheme(bits) {};
  virtual inline ~generic_modulation_scheme() {};

  inline void
  modulate( gr_complex*& sout, const char*& din, bool coding) const;

  // hard decision
  inline void
  demodulate( const gr_complex& sym, char*& dout ) const;

  inline void
  softdemodulate( const gr_complex & sym, float *& dout, float g, float max_g, bool coding) const;

  // soft decision
  inline void
  demodulate_softbits( const gr_complex& sym, float*& dout ) const;
};



class bpsk_scheme : public modulation_scheme
{
private:
  const generic_modulation_scheme<1> mod;

public:
  inline bpsk_scheme() : modulation_scheme(1) {};

  inline void
  modulate(gr_complex*& sout, const char*& din, bool coding) const
  {
    mod.modulate(sout,din,coding);
  }

  inline void
  softdemodulate( const gr_complex & sym, float *& dout, float g, float max_g, bool coding) const
  {
  	mod.softdemodulate(sym,dout,g,max_g,coding);
  	++dout;
  }

  inline void
  demodulate(const gr_complex& sym, char*& dout) const
  {
    if(sym.real() < 0.0)
      *dout = 1;

    ++dout;
  }
};



class qpsk_scheme : public modulation_scheme
{
private:
  const generic_modulation_scheme<2> mod;


public:
  inline qpsk_scheme() : modulation_scheme(2) {};

  inline void
  modulate( gr_complex*& sout, const char*& din, bool coding) const
  {
    mod.modulate(sout,din,coding);
  }

  inline void
  softdemodulate( const gr_complex & sym, float *& dout, float g, float max_g, bool coding) const
  {
    mod.softdemodulate(sym,dout,g,max_g,coding);
    dout += 2;
  }

  inline void
  demodulate( const gr_complex& sym, char*& dout ) const
  {
    const float x_r = -sym.real();
    const float x_i = sym.imag();

    if( x_r < 0.0 )
      dout[0] = 1;

    if( x_i < 0.0 )
      dout[1] = 1;

    dout += 2;
  }
};

class m8psk_scheme : public modulation_scheme
{
private:
  const generic_modulation_scheme<3> mod;


  static const float d_pi_8 = M_PI / 8.0;
  static const float d_7pi_8 = 7.0 * M_PI / 8.0;
  static const float d_3pi_8 = 3.0 * M_PI / 8.0;
  static const float d_5pi_8 = 5.0 * M_PI / 8.0;

public:
  inline m8psk_scheme() : modulation_scheme(3) {};

  inline void
  modulate(gr_complex*& sout, const char*& din, bool coding) const
  {
    mod.modulate(sout,din,coding);
  }

  inline void
  demodulate(const gr_complex& sym, char*& dout) const
  {
    const float arg = std::atan2( sym.imag(), sym.real() );

    if( arg < - d_pi_8 || arg > d_7pi_8 ){
      dout[2] = 1;
    }

    if( arg > d_3pi_8 || arg < - d_5pi_8 ){
      dout[1] = 1;
    }

    if( ( arg > d_pi_8 && arg < d_5pi_8 ) ||
        ( arg < - d_3pi_8 && arg > - d_7pi_8 ) ) {
      dout[0] = 1;
    }

    dout += 3;
  }
};



class m16qam_scheme : public modulation_scheme
{
private:
  const generic_modulation_scheme<4> mod;

  static const float level_0 = 0.6325;

public:
  inline m16qam_scheme() : modulation_scheme(4) {};

  inline void
  modulate(gr_complex*& sout, const char*& din, bool coding) const
  {
    mod.modulate(sout,din,coding);
  }

  inline void
  softdemodulate( const gr_complex & sym, float *& dout, float g, float max_g, bool coding) const
  {
  	mod.softdemodulate(sym,dout,g,max_g,coding);
  	dout += 4;
  }

  inline void
  demodulate(const gr_complex& sym, char*& dout) const
  {
    const float i = sym.real();
    const float q = sym.imag();

    if(i > 0.0){
      dout[0] = 1;
      if((i-level_0) < 0.0)
        dout[1] = 1;
    }else{
      if((i+level_0) > 0.0)
        dout[1] = 1;
    }

    if(q < 0.0){
      dout[2] = 1;
      if((q+level_0) > 0.0)
        dout[3] = 1;
    }else{
      if((q-level_0) < 0.0)
        dout[3] = 1;
    }

    dout += 4;
  }
};


class m32qam_scheme : public modulation_scheme
{
private:
  const generic_modulation_scheme<5> mod;

  std::vector< std::vector< std::vector< char > > > lut;

public:
  inline m32qam_scheme() : modulation_scheme(5)
  {
    lut = ofdmi_generate_32qam_lut();
  };

  inline void
  modulate(gr_complex*& sout, const char*& din, bool coding) const
  {
    mod.modulate(sout,din,coding);
  }

  inline void
  demodulate( const gr_complex & sym, char *& dout ) const
  {
    char * __restrict data = dout;


    const float norm = 1.0 / 0.447214;
    const float min_r = -3.000000;
    const float min_i = -3.000000;
    const float bound =  1.339405;
    const float x_r = gr::branchless_clip( sym.real(), bound );
    const float x_i = gr::branchless_clip( sym.imag(), bound );
    const int ind_r = static_cast< int >( x_r * norm - min_r );
    const int ind_i = static_cast< int >( x_i * norm - min_i );

    data[0] = lut[0][ind_r][ind_i];
    data[1] = lut[1][ind_r][ind_i];
    data[2] = lut[2][ind_r][ind_i];
    data[3] = lut[3][ind_r][ind_i];
    data[4] = lut[4][ind_r][ind_i];


    dout += 5;

  }
};



class m64qam_scheme : public modulation_scheme
{
private:
  const generic_modulation_scheme<6> mod;

  static const float level = 0.3086;
  static const float level2 = 0.3086*2.0;
  static const float level3 = 0.3086*3.0;

public:
  inline m64qam_scheme() : modulation_scheme(6) {};

  inline void
  modulate(gr_complex*& sout, const char*& din, bool coding) const
  {
    mod.modulate(sout,din,coding);
  }

  inline void
  softdemodulate( const gr_complex & sym, float *& dout, float g, float max_g, bool coding) const
  {
  	mod.softdemodulate(sym,dout,g,max_g,coding);
  	dout += 6;
  }

  inline void
  demodulate(const gr_complex& sym, char*& dout) const
  {
    const float i = sym.real();
    const float q = -sym.imag();

    if(i < 0.0){
      if((level2+i)>0.0){
        dout[1] = 1;
        if((-level-i)>0.0)
          dout[2] = 1;
      }else{
        if((i+level3)>0.0)
          dout[2] = 1;
      }
    }else{
      dout[0] = 1;
      if((level2-i)>0.0){
        dout[1] = 1;
        if((i-level)>0.0)
          dout[2] = 1;
      }else{
        if((-i+level3)>0.0)
          dout[2] = 1;
      }
    }

    if(q < 0.0){
      if((level2+q)>0.0){
        dout[4] = 1;
        if((-level-q)>0.0)
          dout[5] = 1;
      }else{
        if((q+level3)>0.0)
          dout[5] = 1;
      }
    }else{
      dout[3] = 1;
      if((level2-q)>0.0){
        dout[4] = 1;
        if((q-level)>0.0)
          dout[5] = 1;
      }else{
        if((-q+level3)>0.0)
          dout[5] = 1;
      }
    }


    dout += 6;
  }
};


class m128qam_scheme : public modulation_scheme
{
private:
  const generic_modulation_scheme<7> mod;

  std::vector< std::vector< std::vector< char > > > lut;

public:
  inline m128qam_scheme() : modulation_scheme(7)
  {
    lut = ofdmi_generate_128qam_lut();
  };

  inline void
  modulate(gr_complex*& sout, const char*& din, bool coding) const
  {
    mod.modulate(sout,din,coding);
  }

  inline void
  demodulate( const gr_complex & sym, char *& dout ) const
  {
    char * __restrict data = dout;

    const float norm = 1.0 / 0.220863;
    const float min_r = -6.000000;
    const float min_i = -6.000000;
    const float bound =  1.324074;
    const float x_r = gr::branchless_clip( sym.real(), bound );
    const float x_i = gr::branchless_clip( sym.imag(), bound );
    const int ind_r = static_cast< int >( x_r * norm - min_r );
    const int ind_i = static_cast< int >( x_i * norm - min_i );
    data[0] = lut[0][ind_r][ind_i];
    data[1] = lut[1][ind_r][ind_i];
    data[2] = lut[2][ind_r][ind_i];
    data[3] = lut[3][ind_r][ind_i];
    data[4] = lut[4][ind_r][ind_i];
    data[5] = lut[5][ind_r][ind_i];
    data[6] = lut[6][ind_r][ind_i];


    //std::cout << x_r << " " << x_i << " " << ind_r << " " << ind_i << std::endl;

//    assert( 0 <= ind_r && ind_r < 12 );
//    assert( 0 <= ind_i && ind_i < 12 );

    data[0] = lut[0][ind_r][ind_i];
    data[1] = lut[1][ind_r][ind_i];
    data[2] = lut[2][ind_r][ind_i];
    data[3] = lut[3][ind_r][ind_i];
    data[4] = lut[4][ind_r][ind_i];
    data[5] = lut[5][ind_r][ind_i];
    data[6] = lut[6][ind_r][ind_i];


    dout += 7;


  }
};




class m256qam_scheme : public modulation_scheme
{
private:
  const generic_modulation_scheme<8> mod;

public:
  inline m256qam_scheme() : modulation_scheme(8) {};

  inline void
  modulate(gr_complex*& sout, const char*& din,bool coding) const
  {
    mod.modulate(sout,din,coding);
  }

  inline void
  softdemodulate( const gr_complex & sym, float *& dout, float g, float max_g, bool coding) const
  {
	mod.softdemodulate(sym,dout,g,max_g,coding);
	dout += 8;
  }

  inline void
  demodulate( const gr_complex & sym, char *& dout ) const
  {
    char * __restrict data = dout;

    const float x_r = sym.real();
    const float x_i = sym.imag();

    if( 0.000000 < x_r )
      data[0] = 1;

    if( -0.613572 < x_r && x_r < 0.613572 )
      data[1] = 1;

    if( -0.920358 < x_r && x_r < -0.306786 )
      data[2] = 1;
    if( 0.306786 < x_r && x_r < 0.920358 )
      data[2] = 1;

    if( -1.073751 < x_r && x_r < -0.766965 )
      data[3] = 1;
    if( -0.460179 < x_r && x_r < -0.153393 )
      data[3] = 1;
    if( 0.766965 < x_r && x_r < 1.073751 )
      data[3] = 1;
    if( 0.153393 < x_r && x_r < 0.460179 )
      data[3] = 1;

    if( x_i < -0.000000 )
      data[4] = 1;

    if( -0.613572 < x_i && x_i < 0.613572 )
      data[5] = 1;

    if( 0.306786 < x_i && x_i < 0.920358 )
      data[6] = 1;
    if( -0.920358 < x_i && x_i < -0.306786 )
      data[6] = 1;

    if( 0.766965 < x_i && x_i < 1.073751 )
      data[7] = 1;
    if( 0.153393 < x_i && x_i < 0.460179 )
      data[7] = 1;
    if( -1.073751 < x_i && x_i < -0.766965 )
      data[7] = 1;
    if( -0.460179 < x_i && x_i < -0.153393 )
      data[7] = 1;

    dout += 8;


  }
};




void ofdmi_generic_decision(const std::vector<gr_complex> &constellation, const gr_complex &symbol, char* out, int &bits);
void ofdmi_bpsk_decision(const std::vector<gr_complex> &constellation, const gr_complex &symbol, char* out, int &bits);
void ofdmi_qpsk_decision(const std::vector<gr_complex> &constellation, const gr_complex &symbol, char* out, int &bits);
void ofdmi_16qam_decision(const std::vector<gr_complex> &constellation, const gr_complex &symbol, char* out, int &bits);
void ofdmi_64qam_decision(const std::vector<gr_complex> &dummy,
    const gr_complex &symbol, char* out, int &bits);



template <int bits>
inline void
generic_modulation_scheme<bits>::modulate( gr_complex*& sout,
    const char*& din, bool coding ) const
{
  unsigned int ind = 0;
  for(int b = 0; b < bits; ++b){
    ind = (ind << 1) | (*din++ & 1);
  }
  //std::cout << "ind " << ind << " constsize " << d_constellation.size() << std::endl;
  //assert(d_constellation.size() == static_cast<cplx_vector::size_type>(pow(2,bits)));
  assert(ind >= 0 && ind < d_constellation.size());
  *sout = d_constellation[ind];
}

template <int bits>
inline void
generic_modulation_scheme<bits>::demodulate(
    const gr_complex& sym, char*& dout) const
{
  int argmin = 0;
  const int indmax = static_cast< int >( pow( 2, bits ) );
  float mindist = std::abs( d_constellation[0] - sym );
  for( int ind = 1; ind < indmax; ++ind )
  {
    const float dist = std::abs( d_constellation[ ind ] - sym );
    if( dist < mindist )
    {
      mindist = dist;
      argmin = ind;
      if( mindist < d_mindist )
      { // safe decision
	break;
      } // if( mindist < d_mindist )
    } // if( dist < mindist )
  } // for( int ind = 1; ind < indmax; ++ind )

  bit_vector::const_iterator t = d_ind_to_bits[argmin].begin();
  for(int b = 0; b < bits; ++b)
    *dout++ = *t++;
}

template <int bits>
inline void
generic_modulation_scheme<bits>::softdemodulate(
    const gr_complex& sym, float*& dout, float g, float max_g, bool coding ) const
{
	const float in_r = sym.real();
	const float in_i = -sym.imag();

	float distance[3] = {0,0,0};
	float scale[10] = {1,0.7071,0.4082,0.3162,0.2236,0.1543,0.1104,0.07669,0.055,0.0382};

	if(bits==1)
	{
		//*dout = in_r * (-pow(g,2));
		*dout = in_r * (-g);
	}
	else
	{
		/* distance vector */
		if (bits==4)
		{
			distance[0]=2;
		}
		else if (bits==6)
		{
			distance[0]=4;
			distance[1]=2;
		}
		else if (bits==8)
		{
			distance[0]=8;
			distance[1]=4;
			distance[2]=2;
		}

		/* scale the distance vector if we are using normalized data */
		distance[0]=distance[0]*scale[bits-1];
		distance[1]=distance[1]*scale[bits-1];
		distance[2]=distance[2]*scale[bits-1];

		int start,middle,end;

		start=0;
		middle=start+bits/2;
		end=bits-1;

		dout[start] = in_r;
		dout[middle] = in_i;

		for (int i=1;i<bits/2;i++)
		{
			dout[i+start]=-fabs(dout[i-1+start])+distance[i-1];
			dout[i+middle]=-fabs(dout[i-1+middle])+distance[i-1];

			dout[i-1+start] = dout[i-1+start] * g;
			dout[i-1+middle] = dout[i-1+middle] * g;
		}
		dout[middle-1] = dout[middle-1] * g;
		dout[end] = dout[end] * g;
	}
	
	/* normalize outputs on maximum gain */

	for (int k=0;k<bits;k++)
		dout[k] = dout[k] / scale[bits-1] / pow(max_g,2);

	/* quantize the values with 3 bits
    
    double max = pow(g,2);
    int qbits = 3;
    int step,k;
    int steps = pow(2,qbits);
    double stepsize = 2*max/pow(2,qbits);
    
    for (k=0;k<bits;k++)
    {
        for (step=0;step<steps;step++)
        {
            if(dout[k]>max)
                dout[k]=max;
            if(dout[k]<-max)
                dout[k]=-max;
            
            if (dout[k]>=-max+step*stepsize&&dout[k]<=-max+(step+1)*stepsize)
            {
                dout[k] = -1+(double)step*2/(double)steps;
                break;
            }
        }
    }*/
}


template <int bits>
inline void
generic_modulation_scheme<bits>::demodulate_softbits(
    const gr_complex& sym, float*& dout ) const
{
  const int indmax = static_cast<int>(pow(2,bits-1));
  for(int b = 0; b < bits; ++b){
    float mindist0 = std::abs(d_soft0[b][0]-sym);
    float mindist1 = std::abs(d_soft1[b][0]-sym);
    for(bit_partition::size_type i = 1; i < indmax; ++i){
      mindist0 = std::min(mindist0,std::abs(d_soft0[b][i]-sym));
      mindist1 = std::min(mindist1,std::abs(d_soft1[b][i]-sym));
    }

    *dout++ = mindist0 - mindist1;
  }
}





class modulation_not_supported : public std::logic_error
{
public:
  modulation_not_supported( std::string x ) : std::logic_error( x ) {};
};


class ofdmi_modem
{
private:

  const bpsk_scheme d_m1;
//  const generic_modulation_scheme<1> d_m1;

  const qpsk_scheme d_m2;
//  const generic_modulation_scheme<2> d_m2;

//  const m8psk_scheme d_m3;
  const generic_modulation_scheme<3> d_m3;

  const m16qam_scheme d_m4;
//  const generic_modulation_scheme<4> d_m4;

  const m32qam_scheme d_m5;
//  const generic_modulation_scheme<5> d_m5;

  const m64qam_scheme d_m6;
//  const generic_modulation_scheme<6> d_m6;

  const m128qam_scheme d_m7;
//  const generic_modulation_scheme<7> d_m7;

  const m256qam_scheme d_m8;
//  const generic_modulation_scheme<8> d_m8;


public:

  inline void
  modulate(gr_complex*& sout, const char*& din, const char& cv, bool coding=false) const
  {
	if(coding)
	{
		switch(cv){
			case 1: d_m1.modulate(sout,din,coding); break;
			case 2: d_m2.modulate(sout,din,coding); break;
			case 3: d_m2.modulate(sout,din,coding); break;
			case 4: d_m4.modulate(sout,din,coding); break;
			case 5: d_m4.modulate(sout,din,coding); break;
			case 6: d_m6.modulate(sout,din,coding); break;
			case 7: d_m6.modulate(sout,din,coding); break;
			case 8: d_m6.modulate(sout,din,coding); break;
			case 9: d_m8.modulate(sout,din,coding); break;
			default: assert("should never get here");
		}
	}
	else {
		switch(cv){
			case 1: d_m1.modulate(sout,din,coding); break;
			case 2: d_m2.modulate(sout,din,coding); break;
			case 3: d_m3.modulate(sout,din,coding); break;
			case 4: d_m4.modulate(sout,din,coding); break;
			case 5: d_m5.modulate(sout,din,coding); break;
			case 6: d_m6.modulate(sout,din,coding); break;
			case 7: d_m7.modulate(sout,din,coding); break;
			case 8: d_m8.modulate(sout,din,coding); break;
			default: assert("should never get here");
		}
	}
  }

  inline void
  softdemodulate( const gr_complex& sym, float*& dout,
      const char& cv, float g, float max_g, bool coding=false) const
   {
     if(coding)
     {
    	 switch(cv){
			case 1: d_m1.softdemodulate(sym,dout,g,max_g,coding); break;
			case 2: d_m2.softdemodulate(sym,dout,g,max_g,coding); break;
			case 3: d_m2.softdemodulate(sym,dout,g,max_g,coding); break;
			case 4: d_m4.softdemodulate(sym,dout,g,max_g,coding); break;
			case 5: d_m4.softdemodulate(sym,dout,g,max_g,coding); break;
			case 6: d_m6.softdemodulate(sym,dout,g,max_g,coding); break;
			case 7: d_m6.softdemodulate(sym,dout,g,max_g,coding); break;
			case 8: d_m6.softdemodulate(sym,dout,g,max_g,coding); break;
			case 9: d_m8.softdemodulate(sym,dout,g,max_g,coding); break;
			default: assert( false && "should never get here" );
		}
     }
     else
     {
		switch(cv){
			case 1: d_m1.softdemodulate(sym,dout,g,max_g,coding); break;
			case 2: d_m2.softdemodulate(sym,dout,g,max_g,coding); break;
			case 4: d_m4.softdemodulate(sym,dout,g,max_g,coding); break;
			case 6: d_m6.softdemodulate(sym,dout,g,max_g,coding); break;
			case 8: d_m8.softdemodulate(sym,dout,g,max_g,coding); break;
			default: assert( false && "should never get here" );
		}
     }
   }

  inline void
  demodulate( const gr_complex& sym, char*& dout,
      const char& cv ) const
  {
    switch(cv){
      case 1: d_m1.demodulate(sym,dout); break;
      case 2: d_m2.demodulate(sym,dout); break;
      case 3: d_m3.demodulate(sym,dout); break;
      case 4: d_m4.demodulate(sym,dout); break;
      case 5: d_m5.demodulate(sym,dout); break;
      case 6: d_m6.demodulate(sym,dout); break;
      case 7: d_m7.demodulate(sym,dout); break;
      case 8: d_m8.demodulate(sym,dout); break;
      default: assert( false && "should never get here" );
    }
  }

  const std::vector<gr_complex>&
  get_constellation( int bits, bool coding=false ) const
  {
    if(coding)
    {
    	switch ( bits ) {
			case 1: return d_m1.get_constellation();
			case 2: return d_m2.get_constellation();
			case 3: return d_m2.get_constellation();
			case 4: return d_m4.get_constellation();
			case 5: return d_m4.get_constellation();
			case 6: return d_m6.get_constellation();
			case 7: return d_m6.get_constellation();
			case 8: return d_m6.get_constellation();
			case 9: return d_m8.get_constellation();
			default: throw modulation_not_supported( "" );
		}
    }
    else
    {
		switch ( bits ) {
			case 1: return d_m1.get_constellation();
			case 2: return d_m2.get_constellation();
			case 3: return d_m3.get_constellation();
			case 4: return d_m4.get_constellation();
			case 5: return d_m5.get_constellation();
			case 6: return d_m6.get_constellation();
			case 7: return d_m7.get_constellation();
			case 8: return d_m8.get_constellation();
			default: throw modulation_not_supported( "" );
		}
    }
  }
};

#endif /*ofdmi_MOD_H_*/
