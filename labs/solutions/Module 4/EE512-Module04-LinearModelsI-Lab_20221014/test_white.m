function pc = test_white(x,Aff)

% pc = test_white(x,Aff);
% Computation of the ratio of normalized autocorrelation estimates 
% larger than the 5% threshold. If this percentage is larger than 0.05, the signal 
% is probably not white.
% x signal
% Aff = 0 no plot, plot otherwise
% pc ratio

K = length(x);
v = xcov(x,'biased');
thresh = 1.96/sqrt(K);
pc = sum(abs(v(K+1:2*K-1)/v(K))>thresh) / (K-1);

if Aff~=0
    figure;
    ml = min(30,K-1);
    stem(-ml:ml,v(K-ml:K+ml)/v(K));
    hold on
    plot([-ml ml],[thresh thresh],'r')
    plot([-ml ml],-[thresh thresh],'r')
    title('Estimated normalized correlation and 95% confidence interval')
    hold off
end

end