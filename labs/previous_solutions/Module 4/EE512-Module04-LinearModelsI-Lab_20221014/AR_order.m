function omdl = AR_order(x,omax,Aff)

% omdl = AR_order(x,omax,Aff);
% Order determination with MDL
% x signal
% omax maximum possible order
% Aff = 0 no graphic display; Aff = 1 display
%  
% omdl : order estimated with MDL

N = length(x);
mdl = zeros(omax,1);

for k=1:omax,
   [a,err] = arcov(x,k);
    mdl(k) = N * log(err) + (k+1) * log(N);
end

if Aff == 1,
  plot(1:omax,mdl,'*b')
  title('MDL')
end

[bid,omdl]=min(mdl);

end