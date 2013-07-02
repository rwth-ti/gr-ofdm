#ifndef INCLUDED_OFDM_DEPUNCTURE_FF_H_
#define INCLUDED_OFDM_DEPUNCTURE_FF_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <boost/shared_array.hpp>

class ofdm_depuncture_ff;
typedef boost::shared_ptr<ofdm_depuncture_ff> ofdm_depuncture_ff_sptr;

OFDM_API ofdm_depuncture_ff_sptr ofdm_make_depuncture_ff (int vlen,float fillval);

/*!
  This block does puncturing of a given bitstream (softbits).
  The argument is the number of subcarriers.
 */
class OFDM_API ofdm_depuncture_ff : public gr_block
{
	private:
		friend OFDM_API ofdm_depuncture_ff_sptr ofdm_make_depuncture_ff (int vlen,float fillval);

		ofdm_depuncture_ff (int vlen,float fillval);
 
		void forecast (int noutput_items, gr_vector_int &ninput_items_required);
		//unsigned int weight (const std::vector<unsigned char> &punctpat);
		void set_punctpat (char mode);
		
		int d_need_bits;
		int d_out_bits;
		int d_vlen;
		float d_fillval;
		std::vector<unsigned char> d_punctpat;

		int d_need_modemap;
		boost::shared_array<char> d_modemap;
		int d_rep_per_mode[9];

		int calc_bit_amount( const char* modemap, const int& vlen);
		int calc_out_bit_amount( const char* modemap, const int& vlen);

	public:
		virtual ~ofdm_depuncture_ff() {};
		
		int general_work (int noutput_items,
						gr_vector_int &ninput_items,
						gr_vector_const_void_star &input_items,
						gr_vector_void_star &output_items);

		virtual int noutput_forecast( gr_vector_int &ninput_items,
						int available_space, int max_items_avail,
						std::vector<bool> &input_done );
};

#endif /* INCLUDED_OFDM_DEPUNCTURE_FF_H_ */
