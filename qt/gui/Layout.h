/*
 * Layout.h
 *
 *  Created on: 23.01.2009
 *      Author: harries
 */

#ifndef LAYOUT_H_
#define LAYOUT_H_

#include <QGridLayout>
#include <string>
#include <QtGui>
#include <QWidget>

class Layout : public QGridLayout
{
public:
	Layout(QWidget* parent = 0) : QGridLayout(parent), x(1), y(1)
	{
		 setSpacing(10);
	};

	void add(QWidget* newWidget)
	{
		if (x<3)
		{
			this->addWidget(newWidget,x,y,0);
			x++;
		}
		else
		{
			this->addWidget(newWidget,x,y,0);
			y++; x=1;
		}
	};
	virtual ~Layout(){};

private:
	int x;
	int y;
};

#endif /* LAYOUT_H_ */
