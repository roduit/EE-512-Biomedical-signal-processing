import pylab as py
import numpy as np

def plot_time(x, t, main_title=''):
    py.figure(figsize=[8,8])
    py.subplot(3,1,1)
    py.plot(t,x['rr'],'k')
    py.xlabel('time (s)')
    py.ylabel('interbeats (ms)')
    py.title('cardiac interbeat intervals')
    py.subplot(3,1,2)
    py.plot(t,x['bp'],'k')
    py.xlabel('time (s)')
    py.ylabel('mean blood pressure (mmHg)')
    py.title('mean blood pressure')
    py.subplot(3,1,3)
    py.plot(t,x['resp'],'k')
    py.xlabel('time (s)')
    py.ylabel('respiratory volume (a.u.)')
    py.title('respiratory volume')
    py.suptitle(main_title, fontsize=14)
    py.tight_layout()
    
def plot_rxx(x, main_title=''):
    K = np.arange(len(x['rxx_rr']))-len(x['rr'])+1
    py.figure(figsize=[8,8])
    py.subplot(3,1,1)
    py.plot(K,x['rxx_rr'],'k')
    py.xlabel('$k$')
    py.ylabel('power (ms$^2$)')
    py.title('cardiac interbeat intervals')
    py.subplot(3,1,2)
    py.plot(K,x['rxx_bp'],'k')
    py.xlabel('$k$')
    py.ylabel('power (mmHg$^2$)')
    py.title('mean blood pressure')
    py.subplot(3,1,3)
    py.plot(K,x['rxx_resp'],'k')
    py.xlabel('$k$')
    py.ylabel('power (a.u.)')
    py.title('respiratory volume')
    py.suptitle(main_title, fontsize=14)

def plot_X(x, fs, main_title=''):
    f = np.arange(len(x['RR']))/len(x['RR'])*fs
    py.figure(figsize=[8,8])
    py.subplot(3,1,1)
    py.plot(f,x['RR'],'k')
    py.xlabel('f (Hz)')
    py.ylabel('power (ms$^2$/Hz)')
    py.title('cardiac interbeat intervals')
    py.xlim(0,0.5)
    py.subplot(3,1,2)
    py.plot(f,x['BP'],'k')
    py.xlabel('frequency (Hz)')
    py.ylabel('power (mmHg$^2$/Hz)')
    py.title('mean blood pressure')
    py.xlim(0,0.5)
    py.subplot(3,1,3)
    py.plot(f,x['RESP'],'k')
    py.xlabel('frequency (Hz)')
    py.ylabel('power (a.u.)')
    py.title('respiratory volume')
    py.xlim(0,0.5)
    py.suptitle(main_title, fontsize=14)

def plot_XY(x, y, fs, main_title=''):
    f = np.arange(len(x['RR']))/len(x['RR'])*fs
    py.figure(figsize=[8,8])
    py.subplot(3,1,1)
    py.plot(f,x['RR'],'k', label='normal')
    py.plot(f,y['RR'],'r', label='alcool')
    py.xlabel('f (Hz)')
    py.ylabel('power (ms$^2$/Hz)')
    py.title('cardiac interbeat intervals')
    py.xlim(0,0.5)
    py.legend()
    py.subplot(3,1,2)
    py.plot(f,x['BP'],'k', label='normal')
    py.plot(f,y['BP'],'r', label='alcool')
    py.xlabel('frequency (Hz)')
    py.ylabel('power (mmHg$^2$/Hz)')
    py.title('mean blood pressure')
    py.xlim(0,0.5)
    py.legend()
    py.subplot(3,1,3)
    py.plot(f,x['RESP'],'k', label='normal')
    py.plot(f,y['RESP'],'r', label='alcool')
    py.xlabel('frequency (Hz)')
    py.ylabel('power (a.u.)')
    py.title('respiratory volume')
    py.xlim(0,0.5)
    py.legend()
    py.suptitle(main_title, fontsize=14)
