#ifndef MY_GL
#define MY_GL

#include <GL/gl.h>
#include <QGLWidget>
#include <QPixmap>
#include <QTimer>

class MyGLWidget : public QGLWidget
{
  Q_OBJECT
private:
        unsigned int first_received_byte;
        unsigned int d_pixel_pos;
        unsigned int d_pos;
        unsigned int d_color;
        unsigned int d_time;

        unsigned int d_width;
        unsigned int d_height;

        double d_zoom;

        unsigned char* d_pixels;

        void update_projection_matrix();
public:
        MyGLWidget(QWidget *parent);

        void set_width(unsigned int width)
        {
          d_width=width;
          setFixedSize((double)d_width*d_zoom, (double)d_height*d_zoom);
          d_pixels=(unsigned char*)realloc(d_pixels,d_width*d_height*3);
        }
        void set_height(unsigned int height)
        {
          d_height=height;
          setFixedSize((double)d_width*d_zoom, (double)d_height*d_zoom);
          d_pixels=(unsigned char*)realloc(d_pixels,d_width*d_height*3);
        }
        void set_zoom(double zoom)
        {
          d_zoom=zoom;
          setFixedSize((double)d_width*d_zoom, (double)d_height*d_zoom);
        }
        void add_pixels(unsigned char *byte_array, unsigned int count, unsigned int position);
        void reset();
protected:
    // initialize OpenGL states (triggered by Qt)
    virtual void initializeGL();
    // handle resize events (triggered by Qt)
    virtual void resizeGL( int w, int h );
};

#endif
