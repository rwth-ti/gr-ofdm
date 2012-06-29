#ifndef __Bitmap_h__
#define __Bitmap_h__

#include <string>
#include <vector>
#include <stdint.h>

void int_to_bits(unsigned int iInt, unsigned char* cBits);
void byte_to_bits(unsigned char cByte, unsigned char* cBits);

class Bitmap
{
public:
  Bitmap();
  ~Bitmap();
  bool load(std::string filename);
  bool save(std::string filename);

  void write_test(std::string filename);
  void get_bitpointer(unsigned int pos,unsigned char** dst);
  void get_bytepointer(unsigned int pos, unsigned char** dst);
  unsigned int get_width();
  unsigned int get_height();
private:
  void readBMPHeaders(FILE* bmp_file);
  void writeBMPHeaders(FILE* out_file);
  bool checkBMPHeaders();
  bool createEmptyBitmap(unsigned int size_x, unsigned int size_y, unsigned int channels);
private:
  std::vector<unsigned char> d_header;
  std::vector<unsigned char> d_bits, d_bytes;
  struct BMP_FILEHEADER
  {
      uint16_t bfType;
      uint32_t bfSize;
      uint32_t bfReserved;
      uint32_t bfOffBits;
  };
  struct BMP_INFOHEADER
  {
      uint32_t biSize;
      int32_t biWidth;
      int32_t biHeight;
      uint16_t biPlanes;
      uint16_t biBitCount;
      uint32_t biCompression;
      uint32_t biSizeImage;
      int32_t biXPelsPerMeter;
      int32_t biYPelsPerMeter;
      uint32_t biClrUsed;
      uint32_t biClrImportant;
  };
  std::string d_filename;
  BMP_FILEHEADER d_FH;
  BMP_INFOHEADER d_IH;
};

#endif
