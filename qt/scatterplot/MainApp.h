#ifndef RECEIVER_H
#define RECEIVER_H

#include <QDialog>
#include <QLineEdit>
#include <QScrollBar>
#include <QTimer>
#include "CGLScatter.h"
#include <fstream>
#include <iostream>
#include <boost/thread/thread.hpp>
#include <boost/bind.hpp>

QT_BEGIN_NAMESPACE
class QLabel;
class QPushButton;
QT_END_NAMESPACE

class MainApp : public QDialog
{
  Q_OBJECT

private slots:
  void timer_func();
  void cleanup();
  void zoom_change();

public:
  MainApp( QWidget *parent, int size, int shm_bufferlength,
    int shm_buffercount, std::string shm_id = std::string() );
  ~MainApp();

public:
  int d_count;
  QPushButton *cleanbutton;
  QScrollBar *scrollbar;

  CGLScatter* scatterplot;
  QTimer* d_timer;
};

#endif
