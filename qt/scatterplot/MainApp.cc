#include <QtGui>
#include <iostream>
#include "MainApp.h"

MainApp::MainApp( QWidget *parent, int size, int shm_bufferlength,
  int shm_buffercount, std::string shm_id )

  : QDialog( parent )
  , d_count( 0 )

{
  cleanbutton = new QPushButton( tr( "&Clear shm" ) );
  connect( cleanbutton, SIGNAL( clicked() ), this, SLOT( cleanup() ) );

  d_timer = new QTimer( this );
  scatterplot = new CGLScatter( this, size, size, true, shm_bufferlength,
    shm_buffercount, shm_id );
  scrollbar = new QScrollBar( Qt::Horizontal );
  scrollbar->setRange( 1, 100 );
  scrollbar->setSliderPosition( 10 );

  QVBoxLayout *layout;
  layout = new QVBoxLayout();
  layout->addWidget( scatterplot );
  layout->addWidget( scrollbar );
  layout->addWidget( cleanbutton );
  connect( d_timer, SIGNAL( timeout() ), this, SLOT( timer_func() ) );
  connect( scrollbar, SIGNAL( sliderReleased() ), this, SLOT( zoom_change() ) );
  d_timer->start( 0 );

  this->setLayout( layout );

  std::cout << "Timer started\n";
  setWindowTitle( tr( "IPC Scatterplot sink" ) );
}

MainApp::~MainApp()
{

}

void MainApp::cleanup()
{
  scatterplot->cleanup_shm();
}

void MainApp::timer_func()
{
  scatterplot->draw_all();
}

void MainApp::zoom_change()
{
  scatterplot->set_zoom( 10.0 / ( double ) scrollbar->sliderPosition() );
}
