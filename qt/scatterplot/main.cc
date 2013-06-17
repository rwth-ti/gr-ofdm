#include <QApplication>

#include "MainApp.h"
#include <string>

#include <sstream>

int StringToInt( std::string stringValue )
{
  std::stringstream ssStream( stringValue );
  int iReturn;
  ssStream >> iReturn;

  return iReturn;
}

std::string IntToString( int iValue )
{
  std::stringstream ssStream;
  ssStream << iValue;
  return ssStream.str();
}

int main( int argc, char *argv[] )
{
  QApplication app( argc, argv );
  MainApp* mainapp;
  if( argc == 1 )
  {
    mainapp = new MainApp( 0, 200, 200, 64 );
    mainapp->show();
  }
  else if( argc == 2 )
  {
    std::string size( argv[1] );

    mainapp = new MainApp( 0, StringToInt( size ), 200, 64 );
    mainapp->show();
  }
  else if( argc == 3 )
  {
    std::string size( argv[1] );
    std::string bufferlength( argv[2] );

    mainapp = new MainApp( 0, StringToInt( size ), StringToInt( bufferlength ),
      64 );
    mainapp->show();
  }
  else if( argc == 4 )
  {
    std::string size( argv[1] );
    std::string bufferlength( argv[2] );
    std::string buffercount( argv[3] );

    mainapp = new MainApp( 0, StringToInt( size ), StringToInt( bufferlength ),
      StringToInt( buffercount ) );
    mainapp->show();
  }
  else if( argc == 5 )
  {
    std::string size( argv[1] );
    std::string bufferlength( argv[2] );
    std::string buffercount( argv[3] );
    std::string shm_id ( argv[4] );

    mainapp = new MainApp( 0, StringToInt( size ), StringToInt( bufferlength ),
      StringToInt( buffercount ), shm_id );
    mainapp->show();
  }
  else
    return 0;
  return mainapp->exec();
}
