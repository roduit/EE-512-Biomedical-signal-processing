function x = AR2(n)

% x = AR2(n)
% generates a bandpass AR(2) process, central frequency 0.2
% values of coeffficients are a1=-0.5562  a2=0.8100
% n number of data points

% modules of the poles
r1 = 0.9 ;

e = randn(n,1);
x = filter(1,[1 -2*r1*cos(0.4*pi) r1*r1],e);

end