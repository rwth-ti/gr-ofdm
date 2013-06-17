#include "widget_scatter_ctrl.h"


widget_scatter_ctrl::widget_scatter_ctrl(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::scatter_ctrl)
{
    ui->setupUi(this);
    connect(ui->lineEdit_subc, SIGNAL(returnPressed()),this,SLOT(setSubcarrier()));
}

widget_scatter_ctrl::~widget_scatter_ctrl()
{
    delete ui;
}

void widget_scatter_ctrl::setData(boost::shared_ptr<IF_ident> dataSource)
{
    if_ptr = boost::dynamic_pointer_cast<IF_scatter_control>(dataSource);
}

void widget_scatter_ctrl::setSubcarrier()
{
    int subc = ui->lineEdit_subc->text().toInt();
    if_ptr->set_subc(subc);
}
