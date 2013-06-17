#include "MyGLWidget.hh"
#include <QPainter>
#include <math.h>

 MyGLWidget::MyGLWidget(QWidget *parent)
     : QGLWidget(QGLFormat(QGL::SampleBuffers), parent),
     d_pixel_pos(0)
     ,d_time(0),d_width(256),d_height(256),d_zoom(1.0)
{
    setFixedSize(d_width, d_height);
    setAutoFillBackground(false);
    d_pixels=(unsigned char*)malloc(d_width*d_height*3);
}

void
MyGLWidget::
resizeGL( int _w, int _h )
{
  update_projection_matrix();
  glViewport(0, 0, _w, _h);
  updateGL();
}

void
MyGLWidget::
update_projection_matrix()
{
  glMatrixMode(GL_PROJECTION);
  glLoadIdentity();
  glOrtho(0,d_width,0,d_height,1,-1);
}



void
MyGLWidget::
initializeGL()
{
  glClearColor(0.0, 0.0, 0.0, 0.0);
  glDisable( GL_DITHER );
  glDisable( GL_DEPTH_TEST );

  // scene pos and size
  glMatrixMode(GL_MODELVIEW);
  glLoadIdentity();
}


 void MyGLWidget::add_pixels(unsigned char* byte_array, unsigned int count, unsigned int position)
 {
   position%=d_width*d_height*3;

   if ((position+count)<d_width*d_height*3)
   {
     memcpy(&d_pixels[position],byte_array,count);++d_time;
   }
   else
   {
   memcpy(&d_pixels[position],byte_array,d_width*d_height*3-position);
   memcpy(&d_pixels[0],&byte_array[d_width*d_height*3-position],position+count-d_width*d_height*3);
   ++d_time;
   }

   glPixelZoom(d_zoom,d_zoom);
   glRasterPos2i(0,0);
   glDrawPixels(d_width,d_height,GL_RGB,GL_UNSIGNED_BYTE,d_pixels);
   //if (d_time%100==0)
   updateGL();
 }


 void MyGLWidget::reset()
 {
   d_pos=0;d_pixel_pos=0;
 }
