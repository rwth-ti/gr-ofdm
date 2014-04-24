clear all; close all; clc;
newData1 = importdata('~/Desktop/task_2_results.xls');

fields = fieldnames(newData1.data);
newData1.data = newData1.data.(fields{1});
% Create new variables in the base workspace from those fields.
vars = fieldnames(newData1);
for i = 1:length(vars)
    assignin('base', vars{i}, newData1.(vars{i}));
end

%data

x_em2 = data(2:3:end,1);
y_em2 = data(4:3:end,1);

x_em4 = data(2:3:end,2);
y_em4 = data(4:3:end,2);

x_em2_plot = [0 ];
y_em2_plot = [0 0];
x_em4_plot = [0 ];
y_em4_plot = [0 0];


for x = 1:length(x_em2)
    if x == length(x_em2)
        x_em2_plot = [x_em2_plot x_em2(x) x_em2(x) 45];
        x_em4_plot = [x_em4_plot x_em4(x) x_em4(x) 45];
    else
        x_em2_plot = [x_em2_plot x_em2(x) x_em2(x) ];
        x_em4_plot = [x_em4_plot x_em4(x) x_em4(x) ];
    end
    y_em2_plot = [y_em2_plot y_em2(x) y_em2(x)];
    y_em4_plot = [y_em4_plot y_em4(x) y_em4(x)];
end

bpsk_x =[0 x_em2(1)];
bpsk_y =[y_em2(1) y_em2(1)];

qpsk_x =[0 x_em2(2)];
qpsk_y =[y_em2(2) y_em2(2)];

psk8_x =[0 x_em2(3)];
psk8_y =[y_em2(3) y_em2(3)];

qam16_x =[0 x_em2(4)];
qam16_y =[y_em2(4) y_em2(4)];

qam64_x =[0 x_em2(5)];
qam64_y =[y_em2(5) y_em2(5)];

qam128_x =[0 x_em2(6)];
qam128_y =[y_em2(6) y_em2(6)];


ber_em2 = data(3:3:end,1);

ber_em4 = data(3:3:end,2);

figure2 = figure (2);
plot3 = semilogy (x_em2,ber_em2,x_em4,ber_em4);
set(plot3(1),'Color','r','DisplayName','BER = 1e-2','LineWidth',1.5);
set(plot3(2),'Color','b','DisplayName','BER = 1e-3','LineWidth',1.5);
legend1 = legend('toggle');
legend('show');
grid on;
hold on

plot4 = semilogy (x_em2,ber_em2,x_em4,ber_em4);
set(plot4(1),'Color','k','Marker','x','DisplayName','BER = 1e-3','MarkerSize',12,'LineStyle','none');
set(plot4(2),'Color','k','Marker','x','DisplayName','BER = 1e-3','MarkerSize',12,'LineStyle','none');
hold off

title (['BER for OFDM system with 1 MHz bandwidth,',sprintf('\n'),'200 data subcarriers, 256 FFT length']);

xlabel('E_S/N_0 [dB]');
ylabel('BER');


figure1 = figure (1);
plot1 = plot (x_em2_plot,y_em2_plot, x_em4_plot,y_em4_plot);%,x_16qam,y_16qam,x_64qam,y_64qam,'LineWidth',1);
set(plot1(1),'Color',[1 0 0],'DisplayName','BER = 1e-2','LineWidth',2);
set(plot1(2),'Color',[0 0 1],'DisplayName','BER = 1e-3','LineWidth',2);
legend1 = legend('toggle');
legend('show');
set(legend1,'Position',[0.6849 0.2836 0.1615 0.07309]);
hold on

plot2 = plot(bpsk_x,bpsk_y,qpsk_x,qpsk_y,psk8_x,psk8_y,qam16_x,qam16_y,qam64_x,qam64_y,qam128_x,qam128_y);
set(plot2,'Color','g','LineStyle','--');
hold off


% Create textbox
annotation(figure1,'textbox','String',{'BPSK'},'FontSize',12,...
    'LineStyle','none',...
    'LineWidth',1,...
    'Position',[0.15 0.23 0.08962 0.05308]);

% Create textbox
annotation(figure1,'textbox','String',{'QPSK'},'FontSize',12,...
    'LineStyle','none',...
    'LineWidth',1,...
    'Position',[0.15 0.33 0.09277 0.05308]);

% Create textbox
annotation(figure1,'textbox','String',{'8-PSK'},'FontSize',12,...
    'LineStyle','none',...
    'LineWidth',1,...
    'Position',[0.15 0.43 0.10277 0.05308]);

% Create textbox
annotation(figure1,'textbox','String',{'16-QAM'},'FontSize',12,...
    'LineStyle','none',...
    'LineWidth',1,...
    'Position',[0.15 0.59 0.1116 0.05308]);

% Create textbox
annotation(figure1,'textbox','String',{'64-QAM'},'FontSize',12,...
    'LineStyle','none',...
    'LineWidth',1,...
    'Position',[0.15 0.74 0.1116 0.05308]);

% Create textbox
annotation(figure1,'textbox','String',{'128-QAM'},'FontSize',12,...
    'LineStyle','none',...
    'LineWidth',1,...
    'Position',[0.15 0.84 0.1226 0.05308]);

axis ([0 35 0 4.5e6]);
title (['Rate-power functions for OFDM system in AWGN channel with 1 MHz bandwidth,',sprintf('\n'),'200 data subcarriers, 256 FFT length']);

xlabel('E_S/N_0 [dB]');
ylabel('Data rate [bps]');

set(0,'Units','pixels') ;
scnsize = get(0,'ScreenSize');
position = get(figure1,'Position');
outerpos = get(figure1,'OuterPosition');
borders = outerpos - position;

edge = -borders(1)/2;
pos1 = [edge,...
    scnsize(4) * (1/2),...
    scnsize(3)/2 - edge,...
    scnsize(4)/2];
pos2 = [scnsize(3)/2 + edge,...
    pos1(2),...
    pos1(3),...
    pos1(4)];
grid on;
set(figure1,'OuterPosition',pos1);
set(figure2,'OuterPosition',pos2);

saveas(figure2,'~/latex/exercise_12', 'epsc');
saveas(figure1,'~/latex/exercise_11', 'epsc');
