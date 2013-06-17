#ifndef WIDGET_SCATTER_CTRL_H
#define WIDGET_SCATTER_CTRL_H

#include <QtGui/QWidget>
#include "../interface/broker.h"
#include "ui_scatter_ctrl.h"
#include "../interface/types.h"


namespace Ui {
    class scatter_ctrl;
}

class widget_scatter_ctrl : public QWidget
{
    Q_OBJECT

public:
    explicit widget_scatter_ctrl(QWidget *parent = 0);
    ~widget_scatter_ctrl();

    void setData(boost::shared_ptr<IF_ident> dataSource);

public slots:
    void setSubcarrier();

private:
    Ui::scatter_ctrl *ui;
    scattercontrol Data;
    boost::shared_ptr<IF_scatter_control> if_ptr;
};

#endif // WIDGET_SCATTER_CTRL_H
