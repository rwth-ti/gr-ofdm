clear all

src =read_complex_binary('hebe1.dat');
snk =read_complex_binary('hebe2.dat');

ref=[];
for i=1:floor(length(src)/10)
    ref=[ref; src((i-1)*10+1:i*10); src((i-1)*10+1:i*10)];
end

diff = abs(snk-ref(1:length(snk)));

difind = find(diff>0);