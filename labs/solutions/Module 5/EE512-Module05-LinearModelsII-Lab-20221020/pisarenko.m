function [f,P,s2] = pisarenko(x,p,Fe,Aff)

% [f,P,s2] = pisarenko(x,p,Fe,Aff)
% Compute the the modal frequencies using Pisarenko's method,
% then find the amplitudes
% x signal
% p number of sinusoïds
% Fe sampling frequency
% f vector of frequencies
% P  vector of amplitudes
% s2 noise variance


le = length(x);
rx = xcorr(x,'biased');
Rxx = zeros(2*p+1,2*p+1);
for k=1:2*p+1,
   for l=1:2*p+1,
      Rxx(k,l) = rx(le+abs(k-l));
   end
end

n = 2*p+1;
[v,u] = eig(Rxx);
[s2,ind] = min(diag(u));
vm = v(:,ind);               % get eigenvector from smallest eigenvalue
r = roots(vm);             % find roots of the polynomial
f = angle(r)/(2*pi); % get angle and convert to Hz/sample
f = f(find(f>0));
% Now compute the amplitudes
% Build up the coefficient matrix
for k=1:p
   A(k,:) = cos(2*pi*k .* f)';
end
r = rx(le+1:le+p);
P = A\r;
f = f*Fe;

if Aff
    subplot(211)
    plot((1:length(x))/Fe,x)
    title('Signal')
    xlabel('seconds')
    subplot(212)
    %stem(f,P)
    plot([0 Fe/2],[s2 s2],'LineWidth',2);
    hold on
    for k=1:p,
        plot([f(k) f(k)],[s2 s2+P(k)],'LineWidth',2)
    end
    axis([0 Fe/2 0 1.2*(max(P)+s2)])
    hold off
    title('Pisarenko spectrum')
    xlabel('Hertz')
    subplot(111)
end

end
