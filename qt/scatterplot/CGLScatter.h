#ifndef MY_GL
#define MY_GL

#include <GL/gl.h>
#include <QGLWidget>
#include <QPixmap>
#include <QTimer>
#include <boost/thread.hpp>

#include "util_ipc.h" //for the Interprocess-Communication
#define POINT_BUFFER_SIZE 2048

class CGLScatter : public QGLWidget
{
  Q_OBJECT
private:
  c_interprocess* d_ipc;

  unsigned int d_width;
  unsigned int d_height;

  bool d_sharedmemory;
  c_point* newpoints;
  unsigned char* where_to_put;
  double d_zoom;

  c_point d_points[POINT_BUFFER_SIZE * 8];
  int d_lastpoint[8];

  unsigned int d_bufferlength, d_buffercount;

  GLuint d_texture;

  void update_projection_matrix();

  void load_texture( const char* filename );
public:
  CGLScatter( QWidget *parent, unsigned int width, unsigned int height,
    bool shared_memory, int shm_bufferlength, int shm_buffercount,
    std::string shm_id = std::string() );

  void cleanup_shm();

  void add_point( unsigned char index, double x, double y );
  void set_zoom( double zoom )
  {
    d_zoom = zoom;
  }
  void set_width( unsigned int width )
  {
    d_width = width;
    setFixedSize( ( double ) d_width, ( double ) d_height );
    //d_pixels=(unsigned char*)realloc(d_pixels,d_width*d_height*3);
  }
  void set_height( unsigned int height )
  {
    d_height = height;
    setFixedSize( ( double ) d_width, ( double ) d_height );
    //d_pixels=(unsigned char*)realloc(d_pixels,d_width*d_height*3);
  }
  void draw_points();
  void draw_all();
protected:
  // initialize OpenGL states (triggered by Qt)
  virtual void initializeGL();
  // handle resize events (triggered by Qt)
  virtual void resizeGL( int w, int h );
};

#endif
