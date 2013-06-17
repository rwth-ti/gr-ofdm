#include <QtGui>
#include <QtNetwork>
#include <iomanip>

#include "receiver.h"

Receiver::Receiver(QWidget *parent)
    : QDialog(parent)
{
    dataNo = 0;
    statusLabel = new QLabel(tr("Listening for broadcasted messages"));
    quitButton = new QPushButton(tr("&Quit"));
    resetButton = new QPushButton(tr("&Reset"));

    widthLineEdit = new QLineEdit("256");
    heightLineEdit = new QLineEdit("256");
    zoomLineEdit = new QLineEdit("1.0");

    udpSocket = new QUdpSocket(this);
    QHostAddress myaddr( "127.0.0.1" );
    udpSocket->bind(myaddr,45454);
    connect(udpSocket, SIGNAL(readyRead()),this, SLOT(processPendingDatagrams()));
    connect(quitButton, SIGNAL(clicked()),this, SLOT(close()));
    connect(resetButton, SIGNAL(clicked()),this, SLOT(reset()));

    QHBoxLayout *buttonLayout = new QHBoxLayout;
    buttonLayout->addStretch(1);
    buttonLayout->addWidget(quitButton);
    buttonLayout->addWidget(resetButton);
    buttonLayout->addStretch(1);
    gl = new MyGLWidget(this);
    QVBoxLayout *mainLayout = new QVBoxLayout;
    QHBoxLayout *lineeditLayout = new QHBoxLayout;
    lineeditLayout->addWidget(widthLineEdit);
    lineeditLayout->addWidget(heightLineEdit);
    lineeditLayout->addWidget(zoomLineEdit);
    mainLayout->addWidget(statusLabel);
    mainLayout->addLayout(lineeditLayout);
    mainLayout->addWidget(gl);
    mainLayout->addLayout(buttonLayout);
    setLayout(mainLayout);
    setWindowTitle(tr("Radio Receiver"));
}

Receiver::~Receiver()
{
}

void Receiver::reset()
{
  gl->set_width(widthLineEdit->text().toInt());
  gl->set_height(heightLineEdit->text().toInt());
  gl->set_zoom(zoomLineEdit->text().toFloat());
}

/*	Gets all Datagrams, which have been received since last Get     */
void Receiver::processPendingDatagrams()
{
    QByteArray datagram;
    unsigned int position=0;
    unsigned int data_size=0;
    while (udpSocket->hasPendingDatagrams()) {


      data_size=udpSocket->pendingDatagramSize();

      datagram.resize(data_size);
      udpSocket->readDatagram(datagram.data(), data_size);

//      std::cout << "New datagram, size " << data_size << std::endl;

      if(data_size<=4)
        continue;
      position=*(unsigned int*)&datagram.data()[0];

//      std::cout << " position=" << position << std::endl;
      gl->add_pixels((unsigned char*)&datagram.data()[4],data_size-4,position);
    }
    statusLabel->setText(tr("Received %1 Bytes!").arg(data_size));
}
