clear all
s=read_char_binary('fbmcdata__source.dat');
e=read_char_binary('fbmcdata__estimated.dat');
cc = [(1:size(e,1)).' s(1:size(e,1)) e abs(s(1:size(e,1))-e)];
k=[find(cc(:,4)>0) cc(find(cc(:,4)>0),4)];
delete('fbmcdata__source.dat');
delete('fbmcdata__estimated.dat');