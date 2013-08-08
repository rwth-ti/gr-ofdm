#include <stdio.h>
#include <cstdlib>
#include <malloc.h>
#include <ofdm/util_endian.h>
#include <ofdm/util_bmp.h>

/*
 * function to convert byte to 8 bytes containing 0 and 1
 */
void byte_to_bits(unsigned char cByte, unsigned char* cBits)
{
  cBits[0]=(cByte&128)!=0;
  cBits[1]=(cByte&64)!=0;
  cBits[2]=(cByte&32)!=0;
  cBits[3]=(cByte&16)!=0;
  cBits[4]=(cByte&8)!=0;
  cBits[5]=(cByte&4)!=0;
  cBits[6]=(cByte&2)!=0;
  cBits[7]=(cByte&1)!=0;
}

void short_to_bits(unsigned short sShort, unsigned char* cBits)
{
  cBits[0]=(sShort&32768)!=0;
  cBits[1]=(sShort&16384)!=0;
  cBits[2]=(sShort&8192)!=0;
  cBits[3]=(sShort&4096)!=0;
  cBits[4]=(sShort&2048)!=0;
  cBits[5]=(sShort&1024)!=0;
  cBits[6]=(sShort&512)!=0;
  cBits[7]=(sShort&256)!=0;
  cBits[8]=(sShort&128)!=0;
  cBits[9]=(sShort&64)!=0;
  cBits[10]=(sShort&32)!=0;
  cBits[11]=(sShort&16)!=0;
  cBits[12]=(sShort&8)!=0;
  cBits[13]=(sShort&4)!=0;
  cBits[14]=(sShort&2)!=0;
  cBits[15]=(sShort&1)!=0;
}

void int_to_bits(unsigned int iInt, unsigned char* cBits)
{
  cBits[0]=(iInt&0x80000000)!=0;
  cBits[1]=(iInt&0x40000000)!=0;
  cBits[2]=(iInt&0x20000000)!=0;
  cBits[3]=(iInt&0x10000000)!=0;
  cBits[4]=(iInt&0x08000000)!=0;
  cBits[5]=(iInt&0x04000000)!=0;
  cBits[6]=(iInt&0x02000000)!=0;
  cBits[7]=(iInt&0x01000000)!=0;
  cBits[8]=(iInt&0x00800000)!=0;
  cBits[9]=(iInt&0x00400000)!=0;
  cBits[10]=(iInt&0x00200000)!=0;
  cBits[11]=(iInt&0x00100000)!=0;
  cBits[12]=(iInt&0x00080000)!=0;
  cBits[13]=(iInt&0x00040000)!=0;
  cBits[14]=(iInt&0x00020000)!=0;
  cBits[15]=(iInt&0x00010000)!=0;
  cBits[16]=(iInt&32768)!=0;
  cBits[17]=(iInt&16384)!=0;
  cBits[18]=(iInt&8192)!=0;
  cBits[19]=(iInt&4096)!=0;
  cBits[20]=(iInt&2048)!=0;
  cBits[21]=(iInt&1024)!=0;
  cBits[22]=(iInt&512)!=0;
  cBits[23]=(iInt&256)!=0;
  cBits[24]=(iInt&128)!=0;
  cBits[25]=(iInt&64)!=0;
  cBits[26]=(iInt&32)!=0;
  cBits[27]=(iInt&16)!=0;
  cBits[28]=(iInt&8)!=0;
  cBits[29]=(iInt&4)!=0;
  cBits[30]=(iInt&2)!=0;
  cBits[31]=(iInt&1)!=0;
}

Bitmap::Bitmap()
{
}


Bitmap::~Bitmap()
{
}

unsigned int Bitmap::get_width()
{
    return d_IH.biWidth;
}

unsigned int Bitmap::get_height()
{
    return d_IH.biHeight;
}

void Bitmap::get_bitpointer(unsigned int pos, unsigned char** dst)
{
  *dst=&d_bits[pos];
  return;
}

void Bitmap::get_bytepointer(unsigned int pos, unsigned char** dst)
{
  *dst=&d_bytes[pos];
  return;
}

void Bitmap::write_test(std::string filename)
{
  /*FILE* out_file;
    if ((out_file = fopen(filename.c_str(), "w+b")) == NULL)
      {
      printf("Could not write file.\n");
      return;
      }

    unsigned char temp=0;
    for (int i=0; i<my_image.size(); ++i)
      {
        temp<<=1;
        temp+=my_image[i];
        if (i%8==0)
          {
        fwrite(&temp,1,1,out_file);
        temp=0;
          }
      }

  fclose(out_file);*/
}

bool Bitmap::load(std::string filename)
{
  d_filename = filename;

  FILE* bmp_file;
  if (!(bmp_file = fopen(d_filename.c_str(), "rb")))
  {
    printf("Could not open image file: %s \n",d_filename.c_str());
          return false;
  }

  readBMPHeaders(bmp_file);
  if(!(checkBMPHeaders()))
  {
      printf("Header wrong.\n");
      return false;
  }

  /* 8 times as big, because single Bits are stored!! */
  d_bits.resize(d_IH.biWidth*d_IH.biHeight*3*8);
  d_bytes.resize(d_IH.biWidth*d_IH.biHeight*3);

  // move to beginning of color-data
  fseek(bmp_file, d_FH.bfOffBits, SEEK_SET);
  // read color-data
  int unused_bytes = d_IH.biWidth % 4;
  for(int i = 0; i<d_IH.biHeight ; i++) // for all rows; reversed: bottom-up bmp
  {
    for (int j = 0; j < d_IH.biWidth; j++) // for all columns
    {
      for (int c = 0; c < 3; c++) // for all channels
      {
        fread(&d_bytes[d_IH.biWidth*3*i+j*3+2-c], 1, 1, bmp_file);
        byte_to_bits(d_bytes[d_IH.biWidth*3*i+j*3+2-c], &d_bits[(d_IH.biWidth*3*i+j*3+2-c)*8]);
      }
    }
    fseek(bmp_file, unused_bytes, SEEK_CUR);
  }

  fclose(bmp_file);

  printf("Loaded image file %s successfully! \n",d_filename.c_str());
  return true;
}

bool Bitmap::save(std::string filename)
{
  FILE* out_file;
  if ((out_file = fopen(filename.c_str(), "w+b")) == NULL)
    {
    printf("Could not write file.\n");
        return false;
    }

  int unused_bytes = 0;//mImage->getWidth() % 4;

  writeBMPHeaders(out_file);

  for(int i = /*mImage->getHeight() - 1*/1024; i >= 0; i--) /* for all rows; reversed: bottom-up bmp*/
    {
        for (unsigned int j = 0; j < 768/*mImage->getWidth()*/; j++) /* for all columns */
        {
            for (unsigned int c = 0; c < 3; c++) /* for all channels */
            {
                //fwrite(&(mImage->getData()[c][tile_x][tile_y][(i%TILESIZE)*TILESIZE + j%TILESIZE]), 1, 1, out_file);//fwrite(&((*mImage.data[c*mImage.tileCnt +  tile_y*mImage.tileCntX + tile_x])[(i%TILESIZE)*TILESIZE + j%TILESIZE]), 1, 1, out_file);
      }
        }

    uint8_t padbyte = 0;
        for(int l = 0; l < unused_bytes; l++)
        {
            fwrite(&padbyte, 1, 1, out_file);
        }
    }

    fclose(out_file);

  return true;
}

void Bitmap::readBMPHeaders(FILE* bmp_file)
{
    // file header
    fread(&d_FH.bfType, 2, 1, bmp_file);
    d_FH.bfType = leth_uint16(d_FH.bfType);

    fread(&d_FH.bfSize, 4, 1, bmp_file);
    d_FH.bfSize = leth_uint32(d_FH.bfSize);

    fread(&d_FH.bfReserved, 4, 1, bmp_file);
    d_FH.bfReserved = leth_uint32(d_FH.bfReserved);

    fread(&d_FH.bfOffBits, 4, 1, bmp_file);
    d_FH.bfOffBits = leth_uint32(d_FH.bfOffBits);

    // information header
    fread(&d_IH.biSize, 4, 1, bmp_file);
    d_IH.biSize = leth_uint32(d_IH.biSize);

    fread(&d_IH.biWidth, 4, 1, bmp_file);
    d_IH.biWidth = leth_int32(d_IH.biWidth);

    fread(&d_IH.biHeight, 4, 1, bmp_file);
    d_IH.biHeight = leth_int32(d_IH.biHeight);

    fread(&d_IH.biPlanes, 2, 1, bmp_file);
    d_IH.biPlanes = leth_uint16(d_IH.biPlanes);

    fread(&d_IH.biBitCount, 2, 1, bmp_file);
    d_IH.biBitCount = leth_uint16(d_IH.biBitCount);

    fread(&d_IH.biCompression, 4, 1, bmp_file);
    d_IH.biCompression = leth_uint32(d_IH.biCompression);

    fread(&d_IH.biSizeImage, 4, 1, bmp_file);
    d_IH.biSizeImage = leth_uint32(d_IH.biSizeImage);

    fread(&d_IH.biXPelsPerMeter, 4, 1, bmp_file);
    d_IH.biXPelsPerMeter = leth_int32(d_IH.biXPelsPerMeter);

    fread(&d_IH.biYPelsPerMeter, 4, 1, bmp_file);
    d_IH.biYPelsPerMeter = leth_int32(d_IH.biYPelsPerMeter);

    fread(&d_IH.biClrUsed, 4, 1, bmp_file);
    d_IH.biClrUsed = leth_uint32(d_IH.biClrImportant);

    fread(&d_IH.biClrImportant, 4, 1, bmp_file);
    d_IH.biClrImportant = leth_uint32(d_IH.biClrImportant);
}


void Bitmap::writeBMPHeaders(FILE* out_file)
{
  // Big-Endian -> Little-Endian
  d_FH.bfType = leth_uint16(d_FH.bfType);
    d_FH.bfSize = leth_uint32(d_FH.bfSize);
    d_FH.bfReserved = leth_uint32(d_FH.bfReserved);
    d_FH.bfOffBits = leth_uint32(d_FH.bfOffBits);
    d_IH.biSize = leth_uint32(d_IH.biSize);
    d_IH.biWidth = leth_int32(d_IH.biWidth);
    d_IH.biHeight = leth_int32(d_IH.biHeight);
    d_IH.biPlanes = leth_uint16(d_IH.biPlanes);
    d_IH.biBitCount = leth_uint16(d_IH.biBitCount);
    d_IH.biCompression = leth_uint32(d_IH.biCompression);
    d_IH.biSizeImage = leth_uint32(d_IH.biSizeImage);
    d_IH.biXPelsPerMeter = leth_int32(d_IH.biXPelsPerMeter);
    d_IH.biYPelsPerMeter = leth_int32(d_IH.biYPelsPerMeter);
    d_IH.biClrUsed = leth_uint32(d_IH.biClrImportant);
    d_IH.biClrImportant = leth_uint32(d_IH.biClrImportant);

  // write data
    fwrite(&d_FH.bfType, 2, 1, out_file);
    fwrite(&d_FH.bfSize, 4, 1, out_file);
    fwrite(&d_FH.bfReserved, 4, 1, out_file);
    fwrite(&d_FH.bfOffBits, 4, 1, out_file);
    fwrite(&d_IH.biSize, 4, 1, out_file);
    fwrite(&d_IH.biWidth, 4, 1, out_file);
    fwrite(&d_IH.biHeight, 4, 1, out_file);
    fwrite(&d_IH.biPlanes, 2, 1, out_file);
    fwrite(&d_IH.biBitCount, 2, 1, out_file);
    fwrite(&d_IH.biCompression, 4, 1, out_file);
    fwrite(&d_IH.biSizeImage, 4, 1, out_file);
    fwrite(&d_IH.biXPelsPerMeter, 4, 1, out_file);
    fwrite(&d_IH.biYPelsPerMeter, 4, 1, out_file);
    fwrite(&d_IH.biClrUsed, 4, 1, out_file);
    fwrite(&d_IH.biClrImportant, 4, 1, out_file);
}


bool Bitmap::checkBMPHeaders()
{
    if(d_FH.bfType != 19778)
  {
    printf("bfType wrong\n");
    return true;
  }

    if(d_FH.bfReserved != 0)
  {
    printf("bfReserved not 0\n");
    return false;
  }
    if(d_FH.bfOffBits < 54)
  {
    printf("data offset wrong\n");
    return false;
  }

    if(d_IH.biSize != 40)
  {
    printf("biSize must be 40\n");
    return false;
  }

    if((d_IH.biWidth < 0) || (d_IH.biHeight < 0))
  {
    printf("only bottom-up BMPs supported\n");
    return false;
  }

    if(d_IH.biPlanes != 1)
  {
    printf("biPlanes must be 1\n");
    return false;
  }

    if(d_IH.biBitCount != 24)
  {
    printf("only 24bpp supported\n");
    return false;
  }

    if(d_IH.biCompression != 0)
  {
    printf("no compression supported\n");
    return false;
  }

  //everything OK
    return true;
}

