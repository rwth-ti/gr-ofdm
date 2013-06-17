#ifndef RECEIVER_H
#define RECEIVER_H

#include <QDialog>
#include <QLineEdit>
#include "MyGLWidget.hh"
#include <fstream>
#include <iostream>

QT_BEGIN_NAMESPACE
class QLabel;
class QPushButton;
class QUdpSocket;
QT_END_NAMESPACE

class Receiver : public QDialog
{
    Q_OBJECT

public:
    Receiver(QWidget *parent = 0);
    ~Receiver();

private slots:
    void processPendingDatagrams();
    void reset();

private:
    QLabel *statusLabel;
    QPushButton *quitButton;
    QPushButton *resetButton;
    QUdpSocket *udpSocket;
    QLineEdit *widthLineEdit, *heightLineEdit, *zoomLineEdit;
    MyGLWidget *gl;

    int dataNo;
};

#endif
