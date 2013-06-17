/*
 * broker.cpp
 *
 *  Created on: 03.12.2008
 *      Author: harries
 */

#include "broker.h"


broker::broker(std::string namingservice_id, std::string port, int id) : stationid(id)
{

    try
    {
        tx_data = get_corba_push_consumer_singleton(namingservice_id, port);
        rx_measure = get_corba_push_consumer_rx_singleton(namingservice_id,port,id);
        rx_bb = get_corba_push_consumer_rxbas_singleton(namingservice_id,port);
    }
    catch(...)
    {
        std::cerr << "ERROR: could not connect to naming service" << std::endl;
        return;
    }
    try
    {
        tx_data->subscribe_event_channel("GNUradio_EventChannel");
        rx_measure->subscribe_event_channel("himalaya");
        rx_bb->subscribe_event_channel("alps");
    }
    catch(...)
    {
        std::cerr << "ERROR: could not subscribe to event channel" << std::endl;
        return;
    }


    std::string name = "corbaloc:iiop:" + namingservice_id + ":" + port + "/NameService";

    wrapper = orb_wrapper::create(name);
}


broker::~broker()
{
}


bool broker::update(int stationID)
{
    IF_List.clear();

    try
    {
        if (tx_data->subscribed())
        {
            boost::shared_ptr<IF_ident> power_aloc (new IF_vector_float(unique_id(DataType(vector_float),IF_Type(power_aloc_scheme),stationID),tx_data));
            boost::shared_ptr<IF_ident> rate_aloc (new IF_vector_float(unique_id(DataType(vector_float),IF_Type(rate_aloc_scheme),stationID),tx_data));
            IF_List.push_back(power_aloc);
            IF_List.push_back(rate_aloc);
        }
    }
    catch (...)
    {
        std::cerr << "subscription error tx_data" << std::endl;
    }
    try
    {
        if (rx_measure->subscribed())
        {
            boost::shared_ptr<IF_ident> performance (new IF_rx_performance(unique_id(DataType(rx_performance_values),IF_Type(rx_performance),stationid),rx_measure));
            boost::shared_ptr<IF_ident> ctf (new IF_vector_float(unique_id(DataType(vector_float),IF_Type(CTF),stationid),rx_measure));
            boost::shared_ptr<IF_ident> est_sinr_sc (new IF_vector_float(unique_id(DataType(vector_float),IF_Type(SINRPSC),stationid),rx_measure));
            boost::shared_ptr<IF_ident> scatterplot (new IF_vector_complex(unique_id(DataType(vector_complex),IF_Type(scatter),stationid),rx_measure));
            IF_List.push_back(performance);
            IF_List.push_back(ctf);
            IF_List.push_back(est_sinr_sc);
            IF_List.push_back(scatterplot);
        }
    }
    catch(...)
    {
        std::cerr << "subscription error rx_measure" << std::endl;
    }
    try
    {
        if (rx_bb->subscribed())
        {
            boost::shared_ptr<IF_ident> bband (new IF_vector_float(unique_id(DataType(vector_float),IF_Type(rx_bband),stationid),rx_bb));
            IF_List.push_back(bband);
        }
    }
    catch(...)
    {
        std::cerr << "subscription error baseband" << std::endl;
    }

    boost::shared_ptr<IF_ident> pwr_ctrl (new IF_power_control(unique_id(DataType(power_strategy), IF_Type(power_control),stationID),wrapper));
    boost::shared_ptr<IF_ident> tx_ctrl (new IF_tx_control(unique_id(DataType(power_strategy), IF_Type(tx_control),stationID),wrapper));
    boost::shared_ptr<IF_ident> transmission (new IF_transmission_data( unique_id (DataType(transmission_data), IF_Type(TransmissionData),stationID),wrapper));
    boost::shared_ptr<IF_ident> scatter_ctrl (new IF_scatter_control(unique_id(DataType(scatter_ctrl_data), IF_Type(scatter_control),stationID),wrapper));
    IF_List.push_back(scatter_ctrl);
    IF_List.push_back(pwr_ctrl);
    IF_List.push_back(tx_ctrl);
    IF_List.push_back(transmission);

    return true;
}

std::list< boost::shared_ptr<IF_ident> > broker::find(int deviceNumber)
{
    update();
    std::list< boost::shared_ptr<IF_ident> > resultList;
    std::list< boost::shared_ptr<IF_ident> >::iterator it;

    for (it = IF_List.begin(); it != IF_List.end(); it++)
        if ((it->get())->getId().getDeviceNo() == deviceNumber) resultList.push_back(*it);
    return resultList;
}

std::list< boost::shared_ptr<IF_ident> > broker::find(IF_Type type)
{
    std::list< boost::shared_ptr<IF_ident> > resultList;
    std::list< boost::shared_ptr<IF_ident> >::iterator it;

    for (it = IF_List.begin(); it != IF_List.end(); it++)
        if ((it->get())->getId().getIfType() == type) resultList.push_back(*it);
    return resultList;
}

std::list< boost::shared_ptr<IF_ident> > broker::getIfList()
{
    update();
    return IF_List;
}
