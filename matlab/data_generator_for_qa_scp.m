%% data_generator_for_qa_scp
%
% Burak Dayi
%
% This script will generate source sequence for quality assurance tests on
% subchannel processing block implemented on top of gnu radio.
%
% This script will generate source data that will be fed into the block as 
% well as expected result of the block. The expected result is computed
% with a simple convolution summation. The expected result can also be
% verified by validity_check which compares convolution summation output
% that we use as expected_result and output of the built-in conv function.
% One more thing to remark, the comparison is made only over data vectors,
% we did not care values on preamble vectors, as it did not affect block
% output in gnu radio implementation.
%
% This should be used along with following shell script:
% /gr-fbmc/build/python/qa_subchannel_processing_vcvc_test.sh 
%
% Created: 11-07-2014


clear all
clc
%% parameters
M=2^8;
syms_per_frame = 10;
num_frames = 2^8;
center = ((-j).^(0:M-1)).';

mul = ceil(rand(M*num_frames,1)*9);
samples = ceil(rand(M*num_frames*2*syms_per_frame,1)*10);

check_validity = 1;
valid_threshold = 1e-7;

parameters = struct;
parameters.M=M;
parameters.syms_per_frame=syms_per_frame;
parameters.num_frames = num_frames;
parameters.center = center;

frame_length = M*(3+2*syms_per_frame);
eq_select = 3;
eq_coefs = zeros(M*num_frames,3);
ro = .5;

%% src_data generation
src_data=zeros(num_frames*frame_length,1);
for i=1:num_frames
    % append preamble
    src_data((i-1)*frame_length+1:(i-1)*frame_length+3*M,1) = [zeros(M,1);(center.*mul((i-1)*M+1:i*M,1));zeros(M,1)];
    % append data
    mull = [];
    for u=1:2*syms_per_frame
        mull =[mull; mul((i-1)*M+1:i*M,1)];
    end
    src_data((i-1)*frame_length+3*M+1:i*frame_length,1) = mull.*samples((i-1)*2*syms_per_frame*M+1:i*2*syms_per_frame*M,1);
end

% add a pair of 0 vectors so that the conv can be completed
src_data=[src_data; zeros(2*M,1)];
clear samples u

%% equalizer coeff. generation
for ii=1:num_frames
    for i=1:M
        EQi = 1/mul((ii-1)*M+i,1);
        EQ_min = 1/mul(mod(i-1-1,M)+1+(ii-1)*M,1);
        EQ_plu = 1/mul(mod(i,M)+1+(ii-1)*M,1);
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

clear EQ1 EQ2 EQi EQ_min EQ_plu eqs


%% expected_result generation
src_w_history = [zeros(2*M,1); src_data];
AA=reshape(src_w_history,M,frame_length*num_frames/M+2+2);

% in gnuradio implementation the equalizer coefficients are changed at the
% end of the preamble centers. that meanswe should take the block starting
% from the next vector upto the preamble center of the following frame.

coefs=ones(M,3);
for i=1+2*M:2*M+M*(3+2*syms_per_frame)*num_frames+2*M
    expected_result(i-2*M,1) = src_w_history(i)*coefs(mod(i-1,M)+1,1)+src_w_history(i-M)*coefs(mod(i-1,M)+1,2)+src_w_history(i-2*M)*coefs(mod(i-1,M)+1,3);
%     disp(sprintf('i: %d\tfr: %d\tM: %d\test: %d\tout: %2.5f%+2.5fj\tcoefs: %f%+fj, %f%+fj, %f%+fj\tsrc: %5.1f+%5.1fj, %5.1f%+5.1fj, %5.1f%+5.1fj', ...
%     i, floor((i-2*M-1)/frame_length),mod(i-1,M),mul(floor((i-2*M-1)/frame_length)*M+mod(i-1,M)+1), real(expected_result(i-2*M,1)), imag(expected_result(i-2*M,1)), ...
% real(coefs(mod(i-1,M)+1,1)),imag(coefs(mod(i-1,M)+1,1)),real(coefs(mod(i-1,M)+1,2)),imag(coefs(mod(i-1,M)+1,2)),real(coefs(mod(i-1,M)+1,3)),imag(coefs(mod(i-1,M)+1,3)),...
% real(src_w_history(i)),imag(src_w_history(i)),real(src_w_history(i-M)),imag(src_w_history(i-M)),real(src_w_history(i-2*M)),imag(src_w_history(i-2*M))));
    if mod(i-2*M,frame_length)==2*M
%         disp('change coefs')
        if i < 2*M+M*(3+2*syms_per_frame)*num_frames+2*M
            coefs = eq_coefs(1+floor(i/frame_length)*M:M+floor(i/frame_length)*M,:);
        end
    end
    if mod(i,10000)==0
        % percent indicator for generation of long sequences
        clc
        disp(sprintf('expected_result is being generated... %6.2f%%',100*i/(2*M+M*(3+2*syms_per_frame)*num_frames+2*M)))
    end
end

if eq_select == 3
    save('src_data_linear.mat','src_data');
    save('expected_result_linear.mat','expected_result');
    save('parameters_linear.mat','parameters')
else
    save('src_data_geometric.mat','src_data');
    save('expected_result_geometric.mat','expected_result');
    save('parameters_geometric.mat','parameters')
end
clear ii i

% convolution of the filters & data sequence by built-in conv function
% it is used to check the validity of generated expected_result
% convs starts from the last vector of the preamble of each frame
% due to conv, we will discard first and last vectors on each row
% due to the first sample will be the part of the preamble, whose value
% we did not care in gnu radio implementation, while comparing we will
% also ignore second sample.
if check_validity % avoid unnecessary computation 
    convs=zeros(M,num_frames*2*syms_per_frame);
    for k=1:M
        for l=1:num_frames        
            temp = conv(eq_coefs((l-1)*M+k,:),AA(k,5+(l-1)*frame_length/M:5-1+l*frame_length/M));
            convs(k,(l-1)*2*syms_per_frame+1:2*l*syms_per_frame) = temp(3:2+2*syms_per_frame);
            if mod((k-1)*num_frames+l,10000)==0
                clc
                disp(sprintf('validity check data is being generated... %6.2f%%',100*((k-1)*num_frames+l)/(M*num_frames)))
            end
        end
    end


    % prepare expected_result data
    expected_result = reshape(expected_result,M,(num_frames*frame_length/M)+2);
    expected_result = expected_result(:,5:end);
    comp_exp = [];
    for i=1:num_frames
        comp_exp = [comp_exp expected_result(:,1+(i-1)*(2*syms_per_frame+3):i*2*syms_per_frame+3*i-3)];
        if mod((k-1)*num_frames+l,10000)==0
            clc
            disp(sprintf('expected_result is being prepared for validity check... %6.2f%%',100*i/num_frames))
        end
    end
    
    % execute comparisons
    if size(find(abs(comp_exp-convs)>valid_threshold),1)==0
        disp('validity check... passed')
    else
        disp('validity check... failed')
        valid_threshold
    end
end

% expected_num_of_samples = M*(num_frames*(3+2*syms_per_frame)+3-1)
% size(expected_result)
% difff = expected_num_of_samples - size(expected_result,1)
disp('done!')