#include <QApplication>

#include "receiver.h"

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    Receiver receiver;
    receiver.show();
    return receiver.exec();
}
