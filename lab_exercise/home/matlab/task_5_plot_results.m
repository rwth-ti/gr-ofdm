clear all; close all; clc;

outfinal = zeros(4,31);
snrdb = (5:5:20);
snr = 10.^(snrdb./10);

eps = linspace(0.01,0.4,31);

for ind = 1:4
    d = 1./((fnf(eps)).^2).*(1 + snr(ind)*(1-(fnf(eps)).^2));
    out = 10*log10(d);
    outfinal(ind,:) = out;
end

figure1 = figure (6);
semilogx1 = semilogx (eps,outfinal(1,:),'-r', eps,outfinal(2,:),'-g',eps,outfinal(3,:),'-b',eps,outfinal(4,:),'-m','LineWidth',1);
ylim([0 8]);
xlim([0.01 0.4]);
set(semilogx1(1),'Color',[1 0 0],'DisplayName','E_s/N_0 = 5 dB');
set(semilogx1(2),'Color',[0 1 0],'DisplayName','E_s/N_0 = 10 dB');
set(semilogx1(3),'Color',[0 0 1],'DisplayName','E_s/N_0 = 15 dB');
set(semilogx1(4),'Color',[1 0 1],'DisplayName','E_s/N_0 = 20 dB');

legend('toggle');
grid on;
hold on;
legend('toggle');

newData2 = importdata('~/Desktop/task_5_results.xls');

fields = fieldnames(newData2.data);
newData2.data = newData2.data.(fields{1});
% Create new variables in the base workspace from those fields.
vars = fieldnames(newData2);
for i = 1:length(vars)
    assignin('base', vars{i}, newData2.(vars{i}));
end

%data

 x_5 = data(1,:);
 y_5 = data(2,:);
 
 x_10 = data(1,:);
 y_10 = data(3,:);

 x_15 = data(1,:);
 y_15 = data(4,:);
 
 x_20 = data(1,:);
 y_20 = data(5,:);
 
 plot3 = plot (x_5,y_5,'--s', x_10,y_10,'--s',x_15,y_15,'--s',x_20,y_20,'--s','LineWidth',1);
 set(plot3(1),'Color',[1 0 0]);
 set(plot3(2),'Color',[0 1 0]);
 set(plot3(3),'Color',[0 0 1]);
 set(plot3(4),'Color',[1 0 1]);
 

%xlabel('$\alpha$','Interpreter','LaTex')
xlabel('\epsilon', 'Interpreter', 'tex');
ylabel('\gamma(\epsilon)[dB]', 'Interpreter', 'tex');
title (['SNR loss over frequency offset for different SNRs,',sprintf('\n'),'analytical and simulation results']);

legend1 = legend('toggle');
legend('show');
set(legend1,'Position',[0.2 0.7 0.1615 0.07309]);
grid on;

saveas(figure1,'~/latex/exercise_3', 'epsc');
