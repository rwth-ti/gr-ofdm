%% eq_coef_check
%
% Burak Dayi
%
% This script will check validity of the equalizer coefficients.
% After running the block either from qa file or on grc, 
% sp_equ_cpp_output.txt file will be created under following folder:
% /gr-fbmc/matlab/
%
% This script will ask user to crop that file according to range of
% interest. The important point is all of the columns has to be selected
% and the selection should be loaded as matrix, which is not default but
% can be changed from the menu on the top.
%
% before running this script, recall to set correct eq_select.
%
% after running the script, check if any of A, B, C vectors has elements.
% If they do not, validity is checked.
%
% Created: 11-07-2014


clearvars -except spequcppoutput
% check = ;
if ~exist('spequcppoutput', 'var')
    uiimport('sp_equ_cpp_output.txt')
    disp('press any key when spequcppoutput is ready.')
    pause
end
rr = [spequcppoutput(:,1:2) spequcppoutput(:,3)+spequcppoutput(:,4) spequcppoutput(:,5)+spequcppoutput(:,6) spequcppoutput(:,7)+spequcppoutput(:,8) spequcppoutput(:,9)+spequcppoutput(:,10)];

num_frames = rr(end,1)+1;
M = rr(end,2)+1;
eq_select = 2; %3: linear, 2:geometric
threshold = 1e-6; % error that we should live with

eq_coefs = zeros(M*num_frames,3);
ro = .5;
for ii=1:num_frames
    for i=1:M
        EQi = 1/rr((ii-1)*M+i,3);
        EQ_min = 1/rr(mod(i-1-1,M)+1+(ii-1)*M,3);
        EQ_plu = 1/rr(mod(i,M)+1+(ii-1)*M,3);
        eqs = [EQ_min EQi EQ_plu];

        if eq_select == 2
            %   % geometric interpolation proposed by Aurelio & Bellanger
            %   % the coefficient computation from same paper
            %   % it's also approach 2 section 4.1.2 from D3.1
            EQ1 = EQ_min*(EQi/EQ_min)^ro;
            EQ2 = EQi*(EQ_plu/EQi)^ro;

        elseif eq_select == 3
            %   % approach 1 D3.1 section 4.1.1 linear interpolation
            EQ1 = (EQ_min+EQi)/2;
            EQ2 = (EQi+EQ_plu)/2;            
        end

        eq_coefs((ii-1)*M+i,1)= ((-1)^(i-1))*((EQ1-2*EQi+EQ2)+j*(EQ2-EQ1))/4;
        eq_coefs((ii-1)*M+i,2)= (EQ1+EQ2)/2;
        eq_coefs((ii-1)*M+i,3)= ((-1)^(i-1))*((EQ1-2*EQi+EQ2)-j*(EQ2-EQ1))/4;

        % %     re im re im ...
%         equalizer_output =conv(eq_coefs(i,:),rx_output(i,:));
%         sp_output(i,1+(ii-1)*2*syms_per_frame:2*syms_per_frame+(ii-1)*2*syms_per_frame)...
%             = equalizer_output(2*K+2+1+(ii-1)*2*(syms_per_frame+1)+(ii-1):2*K+2+1+(ii-1)*2*(syms_per_frame+1)+(ii-1)+2*syms_per_frame-1);
    end
end

res = [rr eq_coefs rr(:,4:6)-eq_coefs(:,1:3)];

A=find(abs(res(:,10))>threshold); % check eq-
B=find(abs(res(:,11))>threshold); % check eq
C=find(abs(res(:,12))>threshold); % check eq+

if (size(A,1)==0 && size(B,1)==0 && size(C,1)==0)
    disp('validity check is passed.')
else
    disp('validity check is failed.')
end