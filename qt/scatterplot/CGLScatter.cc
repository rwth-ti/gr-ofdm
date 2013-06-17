#include "CGLScatter.h"
#include <QPainter>
#include <math.h>
#include <cstring>      // std::memcpy
#include <iostream>

CGLScatter::CGLScatter( QWidget *parent, unsigned int width,
  unsigned int height, bool shared_memory, int shm_bufferlength,
  int shm_buffercount, std::string shm_id )

  : QGLWidget( QGLFormat( QGL::SampleBuffers ), parent )
  , d_width( width )
  , d_height( height )
  , d_sharedmemory( shared_memory )
  , d_zoom( 1.0 )
  , d_bufferlength( shm_bufferlength )
  , d_buffercount( shm_buffercount )

{
  setFixedSize( d_width * 2, d_height * 4 );
  setAutoFillBackground( false );
  memset( d_points, 0, POINT_BUFFER_SIZE * 8 );
  memset( d_lastpoint, 0, sizeof(int) * 8 );

  if( d_sharedmemory )
    d_ipc = c_interprocess::create( d_bufferlength, d_buffercount, shm_id );

  newpoints = new c_point[d_bufferlength];
  where_to_put = new unsigned char[d_bufferlength];

  std::cout << "Initialized everything perfectly!\n";
}

void CGLScatter::cleanup_shm()
{
  d_ipc->cleanup_shm();
}

void CGLScatter::load_texture( const char* filename )
{
  QImage image( filename );
  QImage pixels = convertToGLFormat( image );
  glBindTexture( GL_TEXTURE_2D, d_texture );
  glTexImage2D( GL_TEXTURE_2D, 0, GL_RGB, image.width(), image.height(), 0,
    GL_RGBA, GL_UNSIGNED_BYTE, pixels.bits() );
}

void CGLScatter::resizeGL( int _w, int _h )
{
  update_projection_matrix();
  glViewport( 0, 0, _w, _h );
  updateGL();
}

void CGLScatter::update_projection_matrix()
{
  glMatrixMode( GL_PROJECTION );
  glLoadIdentity();
  glOrtho( 0, d_width * 2, d_height * 4, 0, 1, -1 );
}

void CGLScatter::initializeGL()
{
  glClearColor( 0.0, 0.0, 0.0, 0.0 );
  glDisable( GL_DITHER );
  //  glDisable( GL_DEPTH_TEST );

  glGenTextures( 1, &d_texture );
  glBindTexture( GL_TEXTURE_2D, d_texture );
  glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR );
  glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR );
  glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT );
  glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT );
  glTexEnvf( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE );

  load_texture( "./single_grid.jpg" );
  // scene pos and size
  glMatrixMode( GL_MODELVIEW );
  glLoadIdentity();
}

void CGLScatter::add_point( unsigned char index, double x, double y )
{
  ++d_lastpoint[index];
  x *= d_zoom;
  y *= d_zoom;
  x = std::max( -1.0, std::min( x, 1.0 ) );
  y = std::max( -1.0, std::min( y, 1.0 ) );
  if( d_lastpoint[index] == POINT_BUFFER_SIZE )
    d_lastpoint[index] = 0;
  d_points[index * POINT_BUFFER_SIZE + d_lastpoint[index]].x = x;
  d_points[index * POINT_BUFFER_SIZE + d_lastpoint[index]].y = y;
}

void CGLScatter::draw_points()
{

}

void CGLScatter::draw_all()
{
  glMatrixMode( GL_MODELVIEW );
  glLoadIdentity();

  glClear( GL_DEPTH_BUFFER_BIT );

  glDisable( GL_DEPTH_TEST );
  glEnable( GL_TEXTURE_2D );
  glBindTexture( GL_TEXTURE_2D, d_texture );
  glBegin( GL_QUADS );
  glColor3f( 1, 1, 1 );
  double x_off, y_off;
  for( int i = 0; i < 8; ++i )
  {
    x_off = i % 2* d_width ;
    y_off = i / 2* d_height ;
    glTexCoord2f( 0, 0 );
    glVertex3f( x_off, y_off, 0 );
    glTexCoord2f( 1, 0 );
    glVertex3f( d_width + x_off - 1, y_off, 0 );
    glTexCoord2f( 1, 1 );
    glVertex3f( d_width + x_off - 1, d_height + y_off - 1, 0 );
    glTexCoord2f( 0, 1 );
    glVertex3f( x_off, d_height + y_off - 1, 0 );
  }
  glEnd();
  glEnable( GL_DEPTH_TEST );

  glDisable( GL_TEXTURE_2D );

  int has_new_points[9];
  std::memset( has_new_points, 0, sizeof(int) * 9 );
  if( d_sharedmemory )
  {
    d_ipc->read_points( newpoints, where_to_put );

    glPointSize( 5.0 );
    glBegin( GL_POINTS );
    int x_off, y_off;
    for( unsigned int i = 0; i < d_bufferlength; ++i )
    {

      if( ( where_to_put[i] > 0 ) && ( where_to_put[i] <= 8 ) )
      {
        x_off = ( where_to_put[i] - 1 ) % 2* d_width + ( i % ( d_bufferlength
            / 2 ) ) * d_width / ( d_bufferlength / 2 );
        y_off = ( where_to_put[i] - 1 ) / 2* d_height + ( i > ( d_bufferlength
            / 2 ) ) * 5.0;
        this->add_point( where_to_put[i] - 1, newpoints[i].x, newpoints[i].y );
        glColor3f( ( double ) i / ( double ) d_bufferlength, 0, 0 );
        glVertex3f( x_off, y_off, 0 );
        ++has_new_points[where_to_put[i]];
      }
    }
    glEnd();
  }
  for( int i = 1; i < 9; ++i )
  {
    if( has_new_points[i] == 0 )
    {
      for( int k = 0; k < POINT_BUFFER_SIZE / 128; ++k )
        this->add_point( i - 1, 0, 0 );
    }
  }
  double color = 0.0;
  int correct_pos = 0;
  for( int j = 0; j < 8; ++j )
  {
    glLoadIdentity();
    glTranslatef( d_width * ( j % 2 ) + d_width / 2, d_height
        * ( int ) ( j / 2 ) + d_height / 2, 0 );
    glPointSize( 2.0 );
    glBegin( GL_POINTS );
    glColor3f( 1, 1, 1 );
    for( int i = 0; i < POINT_BUFFER_SIZE; ++i )
    {
      correct_pos = i - d_lastpoint[j] - 1;
      while( correct_pos < 0 )
        correct_pos += POINT_BUFFER_SIZE;
      color = 1 - ( double ) correct_pos / ( double ) POINT_BUFFER_SIZE;
      glColor3f( color, color, color );
      glVertex3f( d_points[i + j * POINT_BUFFER_SIZE].x * d_width / 2,
        d_points[i + j * POINT_BUFFER_SIZE].y * d_height / 2, color );
    }
    glEnd();
  }
  updateGL();
}
