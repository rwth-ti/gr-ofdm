/*
 * viewWidget.cpp
 *
 *  Created on: 24.01.2009
 *      Author: harry
 */

#include "viewWidget.h"

viewWidget::viewWidget() : QWidget()
{
	QSize screen = QApplication::desktop()->size();
	this->setMaximumSize(screen);

}

viewWidget::~viewWidget() {
	// TODO Auto-generated destructor stub
}
