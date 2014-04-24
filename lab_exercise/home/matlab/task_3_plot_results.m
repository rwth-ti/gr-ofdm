clear all; close all; clc;
newData2 = importdata('~/Desktop/task_3_results.xls');

fields = fieldnames(newData2.data);
newData2.data = newData2.data.(fields{1});
% Create new variables in the base workspace from those fields.
vars = fieldnames(newData2);
for i = 1:length(vars)
    assignin('base', vars{i}, newData2.(vars{i}));
end

%data

 y_em2 = data(2,2:end);
 x_em2 = [data(1,2); data(1,3)];
 
 y_em3 = data(3,2:end);
 x_em3 = [data(1,2); data(1,3)];
 
 %y_em4 = data(3,1:2:end)
 %x_em4 = data(3,2:2:end)
 
%  x_16qam = data(3,1:2:end);
%  y_16qam = data(3,2:2:end);
%  
%  x_64qam = data(4,1:2:end);
%  y_64qam = data(4,2:2:end);
 
%  x_256qam = data(9,:);
%  y_256qam = data(10,:);
 
 %plot3 = plot (x_bpsk,y_bpsk,'--s', x_4qam,y_4qam,'--s',x_16qam,y_16qam,'--s',x_64qam,y_64qam,'--s''LineWidth',1);
 figure10 = figure (5);
 plot2 = semilogy(x_em2, y_em2, x_em3, y_em3);%, x_em4, y_em4);%,x_16qam,y_16qam,x_64qam,y_64qam,'LineWidth',1);
 set(plot2(1),'Color','r','LineStyle','-','DisplayName','BER = 1e-2');
 set(plot2(2),'Color','g','LineStyle','-','DisplayName','BER = 1e-3');
 %set(plot2(3),'Color','b','LineStyle','-','DisplayName','BER = 1e-4');
 legend1 = legend('toggle');
 legend('show');
 set(legend1,'Position',[0.7092 0.1641 0.1368 0.1065]);
 
 hold on
 
 plot1 = semilogy(x_em2, y_em2, x_em3, y_em3);%, x_em4, y_em4);%,x_16qam,y_16qam,x_64qam,y_64qam,'LineWidth',1);
 set(plot1(1),'Color','k','Marker','x','DisplayName','BER = 1e-2','MarkerSize',12,'LineStyle','none');
 set(plot1(2),'Color','k','Marker','x','DisplayName','BER = 1e-3','MarkerSize',12,'LineStyle','none');
 %set(plot1(3),'Color','k','Marker','x','DisplayName','BER = 1e-4','MarkerSize',12,'LineStyle','none');
 %legend1 = legend('toggle');
 %legend('show');
 %set(legend1,'Position',[0.6849 0.2836 0.1615 0.07309]);
 hold on

 xx = [0 1.5];
 yy1 = [5e-2 5e-2];
 yy2 = [5e-3 5e-3];
 %yy3 = [1e-4 1e-4];
 
 plot3 = semilogy(xx,yy1,xx,yy2);%,xx,yy3);
 set(plot3(1),'Color','r','LineStyle','--');
 set(plot3(2),'Color','g','LineStyle','--');
 %set(plot3(3),'Color','b','LineStyle','--');
 hold on
 
 xxx1 = [0.5 0.5];
 xxx2 = [1 1];
 yyy1 = [1e-8 5e-1];
 yyy2 = [1e-8 5e-1];
 plot4 = plot(xxx1,yyy1,xxx2,yyy2);
 set(plot4(1),'Color','k','LineStyle','--');
 set(plot4(2),'Color','k','LineStyle','--');

 hold off
 
  
 % Create arrow
annotation(figure10,'arrow',[0.233 0.3742],[0.36 0.4]);

% Create textbox
annotation(figure10,'textbox','String',{'QPSK on','100 occupied carriers'},...
    'FontSize',12,...
    'LineStyle','none',...
    'Position',[0.1904 0.2644 0.1904 0.08904]);

% Create arrow
annotation(figure10,'arrow',[0.73 0.6605],[0.3997 0.42]);

% Create textbox
annotation(figure10,'textbox','String',{'BPSK on','200 occupied carriers'},...
    'FontSize',12,...
    'LineStyle','none',...
    'Position',[0.7084 0.3095 0.1904 0.08904]);
 
 
 axis ([0 1.5 1e-8 5e-1]);
 title (['BER for simulated OFDM system in frequency selective channel with 1MHz bandwidth,',sprintf('\n'),'200 data subcarriers, 256 fft length']);
 
 xlabel('Occupied bandwidth [MHz]');
 ylabel('BER');
 grid on;
 saveas(figure10,'~/latex/exercise_2', 'epsc');
 
 
 
