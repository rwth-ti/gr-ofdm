/*
 * WidgetControl.h
 *
 *  Created on: 13.01.2009
 *      Author: harries
 */

#ifndef WIDGETCONTROL_H_
#define WIDGETCONTROL_H_

class WidgetControl {
public:
	WidgetControl(){};
	virtual ~WidgetControl(){};
	virtual void refresh() = 0;
};

#endif /* WIDGETCONTROL_H_ */
