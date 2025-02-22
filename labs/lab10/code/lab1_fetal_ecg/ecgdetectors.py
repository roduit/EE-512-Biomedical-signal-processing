"""
A collection of ECG heartbeat detection algorithms implemented
in Python. Developed in conjunction with a new ECG database:
http://researchdata.gla.ac.uk/716/

This is a modified version of the file available here:
https://github.com/berndporr/py-ecg-detectors/blob/master/ecgdetectors.py

Copyright (C) 2019-2023 Luis Howell & Bernd Porr
GPL GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

import numpy as np

try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib
import scipy.signal as signal


class Detectors:
    """ECG heartbeat detection algorithms
    General useage instructions:
    r_peaks = detectors.the_detector(ecg_in_samples)
    The argument ecg_in_samples is a single channel ECG in volt
    at the given sample rate.
    """

    def __init__(self, sampling_frequency = False):
        """
        The constructor takes the sampling rate in Hz of the ECG data.
        The constructor can be called without speciying a sampling rate to
        just access the detector_list, however, detection won't
        be possible.
        """

        ## Sampling rate
        self.fs = sampling_frequency

        ## This is set to a positive value for benchmarking
        self.engzee_fake_delay = 0

        ## 2D Array of the different detectors: [[description,detector]]
        self.detector_list = [
            ["Elgendi et al (Two average)",self.two_average_detector],
            ["Engzee",self.engzee_detector],
            ["Christov",self.christov_detector],
            ["Hamilton",self.hamilton_detector],
            ["Pan Tompkins",self.pan_tompkins_detector],
            ["WQRS",self.wqrs_detector]
        ]

    def get_detector_list(self):
        """
        Returns a 2D array of the different detectors in the form:
        [[description1,detector1],[description2,detector2], ...]
        where description is a string and detector a function pointer
        to the detector. Use this for benchmarking to loop through
        detectors.
        """
        return self.detector_list

    def hamilton_detector(self, unfiltered_ecg):
        """
        P.S. Hamilton, 
        Open Source ECG Analysis Software Documentation, E.P.Limited, 2002.
        """
        
        f1 = 8/self.fs
        f2 = 16/self.fs

        b, a = signal.butter(1, [f1*2, f2*2], btype='bandpass')

        filtered_ecg = signal.lfilter(b, a, unfiltered_ecg)

        diff = abs(np.diff(filtered_ecg))

        b = np.ones(int(0.08*self.fs))
        b = b/int(0.08*self.fs)
        a = [1]

        ma = signal.lfilter(b, a, diff)

        ma[0:len(b)*2] = 0

        n_pks = []
        n_pks_ave = 0.0
        s_pks = []
        s_pks_ave = 0.0
        QRS = [0]
        RR = []
        RR_ave = 0.0

        th = 0.0

        i=0
        idx = []
        peaks = []  

        for i in range(len(ma)):

            if i>0 and i<len(ma)-1:
                if ma[i-1]<ma[i] and ma[i+1]<ma[i]:
                    peak = i
                    peaks.append(i)

                    if ma[peak] > th and (peak-QRS[-1])>0.3*self.fs:        
                        QRS.append(peak)
                        idx.append(i)
                        s_pks.append(ma[peak])
                        if len(n_pks)>8:
                            s_pks.pop(0)
                        s_pks_ave = np.mean(s_pks)

                        if RR_ave != 0.0:
                            if QRS[-1]-QRS[-2] > 1.5*RR_ave:
                                missed_peaks = peaks[idx[-2]+1:idx[-1]]
                                for missed_peak in missed_peaks:
                                    if missed_peak-peaks[idx[-2]]>int(0.360*self.fs) and ma[missed_peak]>0.5*th:
                                        QRS.append(missed_peak)
                                        QRS.sort()
                                        break

                        if len(QRS)>2:
                            RR.append(QRS[-1]-QRS[-2])
                            if len(RR)>8:
                                RR.pop(0)
                            RR_ave = int(np.mean(RR))

                    else:
                        n_pks.append(ma[peak])
                        if len(n_pks)>8:
                            n_pks.pop(0)
                        n_pks_ave = np.mean(n_pks)

                    th = n_pks_ave + 0.45*(s_pks_ave-n_pks_ave)

                    i+=1

        QRS.pop(0)

        return QRS

    
    def christov_detector(self, unfiltered_ecg):
        """
        Ivaylo I. Christov, 
        Real time electrocardiogram QRS detection using combined 
        adaptive threshold, BioMedical Engineering OnLine 2004, 
        vol. 3:28, 2004.
        """
        total_taps = 0

        b = np.ones(int(0.02*self.fs))
        b = b/int(0.02*self.fs)
        total_taps += len(b)
        a = [1]

        MA1 = signal.lfilter(b, a, unfiltered_ecg)

        b = np.ones(int(0.028*self.fs))
        b = b/int(0.028*self.fs)
        total_taps += len(b)
        a = [1]

        MA2 = signal.lfilter(b, a, MA1)

        Y = []
        for i in range(1, len(MA2)-1):
            
            diff = abs(MA2[i+1]-MA2[i-1])

            Y.append(diff)

        b = np.ones(int(0.040*self.fs))
        b = b/int(0.040*self.fs)
        total_taps += len(b)
        a = [1]

        MA3 = signal.lfilter(b, a, Y)

        MA3[0:total_taps] = 0

        ms50 = int(0.05*self.fs)
        ms200 = int(0.2*self.fs)
        ms1200 = int(1.2*self.fs)
        ms350 = int(0.35*self.fs)

        M = 0
        newM5 = 0
        M_list = []
        MM = []
        M_slope = np.linspace(1.0, 0.6, ms1200-ms200)
        F = 0
        F_list = []
        R = 0
        RR = []
        Rm = 0
        R_list = []

        MFR = 0
        MFR_list = []

        QRS = []

        for i in range(len(MA3)):

            # M
            if i < 5*self.fs:
                M = 0.6*np.max(MA3[:i+1])
                MM.append(M)
                if len(MM)>5:
                    MM.pop(0)

            elif QRS and i < QRS[-1]+ms200:
                newM5 = 0.6*np.max(MA3[QRS[-1]:i])
                if newM5>1.5*MM[-1]:
                    newM5 = 1.1*MM[-1]

            elif QRS and i == QRS[-1]+ms200:
                if newM5==0:
                    newM5 = MM[-1]
                MM.append(newM5)
                if len(MM)>5:
                    MM.pop(0)    
                M = np.mean(MM)    
            
            elif QRS and i > QRS[-1]+ms200 and i < QRS[-1]+ms1200:

                M = np.mean(MM)*M_slope[i-(QRS[-1]+ms200)]

            elif QRS and i > QRS[-1]+ms1200:
                M = 0.6*np.mean(MM)

            # F
            if i > ms350:
                F_section = MA3[i-ms350:i]
                max_latest = np.max(F_section[-ms50:])
                max_earliest = np.max(F_section[:ms50])
                F = F + ((max_latest-max_earliest)/150.0)

            # R
            if QRS and i < QRS[-1]+int((2.0/3.0*Rm)):

                R = 0

            elif QRS and i > QRS[-1]+int((2.0/3.0*Rm)) and i < QRS[-1]+Rm:

                dec = (M-np.mean(MM))/1.4
                R = 0 + dec


            MFR = M+F+R
            M_list.append(M)
            F_list.append(F)
            R_list.append(R)
            MFR_list.append(MFR)

            if not QRS and MA3[i]>MFR:
                QRS.append(i)
            
            elif QRS and i > QRS[-1]+ms200 and MA3[i]>MFR:
                QRS.append(i)
                if len(QRS)>2:
                    RR.append(QRS[-1]-QRS[-2])
                    if len(RR)>5:
                        RR.pop(0)
                    Rm = int(np.mean(RR))

        QRS.pop(0)
        
        return QRS

    
    def engzee_detector(self, unfiltered_ecg):
        """
        C. Zeelenberg, A single scan algorithm for QRS detection and
        feature extraction, IEEE Comp. in Cardiology, vol. 6,
        pp. 37-42, 1979 with modifications A. Lourenco, H. Silva,
        P. Leite, R. Lourenco and A. Fred, “Real Time
        Electrocardiogram Segmentation for Finger Based ECG
        Biometrics”, BIOSIGNALS 2012, pp. 49-54, 2012.
        """
                
        f1 = 48/self.fs
        f2 = 52/self.fs
        b, a = signal.butter(4, [f1*2, f2*2], btype='bandstop')
        filtered_ecg = signal.lfilter(b, a, unfiltered_ecg)

        diff = np.zeros(len(filtered_ecg))
        for i in range(4, len(diff)):
            diff[i] = filtered_ecg[i]-filtered_ecg[i-4]

        ci = [1,4,6,4,1]        
        low_pass = signal.lfilter(ci, 1, diff)

        low_pass[:int(0.2*self.fs)] = 0
      
        ms200 = int(0.2*self.fs)
        ms1200 = int(1.2*self.fs)        
        ms160 = int(0.16*self.fs)
        neg_threshold = int(0.01*self.fs)

        M = 0
        M_list = []
        neg_m = []
        MM = []
        M_slope = np.linspace(1.0, 0.6, ms1200-ms200)

        QRS = []
        r_peaks = []

        counter = 0

        thi_list = []
        thi = False
        thf_list = []
        thf = False
        newM5 = False

        for i in range(len(low_pass)):

            # M
            if i < 5*self.fs:
                M = 0.6*np.max(low_pass[:i+1])
                MM.append(M)
                if len(MM)>5:
                    MM.pop(0)

            elif QRS and i < QRS[-1]+ms200:

                newM5 = 0.6*np.max(low_pass[QRS[-1]:i])

                if newM5>1.5*MM[-1]:
                    newM5 = 1.1*MM[-1]

            elif newM5 and QRS and i == QRS[-1]+ms200:
                MM.append(newM5)
                if len(MM)>5:
                    MM.pop(0)    
                M = np.mean(MM)    
            
            elif QRS and i > QRS[-1]+ms200 and i < QRS[-1]+ms1200:

                M = np.mean(MM)*M_slope[i-(QRS[-1]+ms200)]

            elif QRS and i > QRS[-1]+ms1200:
                M = 0.6*np.mean(MM)

            M_list.append(M)
            neg_m.append(-M)


            if not QRS and low_pass[i]>M:
                QRS.append(i)
                thi_list.append(i)
                thi = True
            
            elif QRS and i > QRS[-1]+ms200 and low_pass[i]>M:
                QRS.append(i)
                thi_list.append(i)
                thi = True

            if thi and i<thi_list[-1]+ms160:
                if low_pass[i]<-M and low_pass[i-1]>-M:
                    #thf_list.append(i)
                    thf = True
                    
                if thf and low_pass[i]<-M:
                    thf_list.append(i)
                    counter += 1
                
                elif low_pass[i]>-M and thf:
                    counter = 0
                    thi = False
                    thf = False
            
            elif thi and i>thi_list[-1]+ms160:
                    counter = 0
                    thi = False
                    thf = False                                        
            
            if counter>neg_threshold:
                unfiltered_section = unfiltered_ecg[thi_list[-1]-int(0.01*self.fs):i]
                r_peaks.append(self.engzee_fake_delay+
                               np.argmax(unfiltered_section)+thi_list[-1]-int(0.01*self.fs))
                counter = 0
                thi = False
                thf = False

        # removing the 1st detection as it 1st needs the QRS complex amplitude for the threshold
        r_peaks.pop(0)
        return r_peaks


    def pan_tompkins_detector(self, unfiltered_ecg, MWA_name='cumulative'):
        """
        Jiapu Pan and Willis J. Tompkins.
        A Real-Time QRS Detection Algorithm. 
        In: IEEE Transactions on Biomedical Engineering 
        BME-32.3 (1985), pp. 230–236.
        """
        
        maxQRSduration = 0.150 #sec
        f1 = 5/self.fs
        f2 = 15/self.fs

        b, a = signal.butter(1, [f1*2, f2*2], btype='bandpass')

        filtered_ecg = signal.lfilter(b, a, unfiltered_ecg)        

        diff = np.diff(filtered_ecg) 

        squared = diff*diff

        N = int(maxQRSduration*self.fs)
        mwa = MWA_from_name(MWA_name)(squared, N)
        mwa[:int(maxQRSduration*self.fs*2)] = 0

        mwa_peaks = panPeakDetect(mwa, self.fs)

        return mwa_peaks


    def two_average_detector(self, unfiltered_ecg, MWA_name='cumulative'):
        """
        Elgendi, Mohamed & Jonkman, 
        Mirjam & De Boer, Friso. (2010).
        Frequency Bands Effects on QRS Detection.
        The 3rd International Conference on Bio-inspired Systems 
        and Signal Processing (BIOSIGNALS2010). 428-431.
        """
        
        f1 = 8/self.fs
        f2 = 20/self.fs

        b, a = signal.butter(2, [f1*2, f2*2], btype='bandpass')

        filtered_ecg = signal.lfilter(b, a, unfiltered_ecg)

        window1 = int(0.12*self.fs)
        mwa_qrs = MWA_from_name(MWA_name)(abs(filtered_ecg), window1)

        window2 = int(0.6*self.fs)
        mwa_beat = MWA_from_name(MWA_name)(abs(filtered_ecg), window2)

        blocks = np.zeros(len(unfiltered_ecg))
        block_height = np.max(filtered_ecg)

        for i in range(len(mwa_qrs)):
            if mwa_qrs[i] > mwa_beat[i]:
                blocks[i] = block_height
            else:
                blocks[i] = 0

        QRS = []

        for i in range(1, len(blocks)):
            if blocks[i-1] == 0 and blocks[i] == block_height:
                start = i
            
            elif blocks[i-1] == block_height and blocks[i] == 0:
                end = i-1

                if end-start>int(0.08*self.fs):
                    detection = np.argmax(filtered_ecg[start:end+1])+start
                    if QRS:
                        if detection-QRS[-1]>int(0.3*self.fs):
                            QRS.append(detection)
                    else:
                        QRS.append(detection)

        return QRS

    def wqrs_detector(self, unfiltered_ecg):
        """
        based on W Zong, GB Moody, D Jiang 
        A Robust Open-source Algorithm to Detect Onset and Duration of QRS
        Complexes 
        In: 2003 IEEE
        """
        def butter_lowpass_filter(data, cutoff):
            nyq = 0.5 * self.fs
            order = 2

            normal_cutoff = cutoff / nyq
            
            b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
            y = signal.lfilter(b, a, data)
            return y

        def length_transfrom(x, w):
            tmp = []
            for i in range(w, len(x)):
                chunk = x[i-w:i]
                ll = np.sum(
                    np.sqrt( np.power(1/self.fs,2)*np.ones(w-1) + np.power(np.diff(chunk),2) )
                )
                tmp.append(ll)
            l = [tmp[0]]*w
            
            return l+tmp
        
        def threshold(x):
            peaks = []
            u = MWA_convolve(x, 10*self.fs)
            for i in range(len(x)):
                if (len(peaks) == 0 or i > peaks[-1]+(self.fs*0.35)) and x[i] > u[i]:
                    peaks.append(i)
            return peaks
        
        y = butter_lowpass_filter(unfiltered_ecg, 15)
        y = length_transfrom(y, int(np.ceil(self.fs*0.13)))
        return threshold(y)

def MWA_from_name(function_name):
    if function_name == "cumulative":
        return MWA_cumulative
    elif function_name == "convolve":
        return MWA_convolve
    elif function_name == "original":
        return MWA_original
    else: 
        raise RuntimeError('invalid moving average function!')

#Fast implementation of moving window average with numpy's cumsum function 
def MWA_cumulative(input_array, window_size):
    
    ret = np.cumsum(input_array, dtype=float)
    ret[window_size:] = ret[window_size:] - ret[:-window_size]
    
    for i in range(1,window_size):
        ret[i-1] = ret[i-1] / i
    ret[window_size - 1:]  = ret[window_size - 1:] / window_size
    
    return ret

#Original Function 
def MWA_original(input_array, window_size):

    mwa = np.zeros(len(input_array))
    mwa[0] = input_array[0]
    
    for i in range(2,len(input_array)+1):
        if i < window_size:
            section = input_array[0:i]
        else:
            section = input_array[i-window_size:i]        
        
        mwa[i-1] = np.mean(section)

    return mwa

#Fast moving window average implemented with 1D convolution 
def MWA_convolve(input_array, window_size):
    
    ret = np.pad(input_array, (window_size-1,0), 'constant', constant_values=(0,0))
    ret = np.convolve(ret,np.ones(window_size),'valid')
    
    for i in range(1,window_size):
        ret[i-1] = ret[i-1] / i
    ret[window_size-1:] = ret[window_size-1:] / window_size
    
    return ret


def normalise(input_array):

    output_array = (input_array-np.min(input_array))/(np.max(input_array)-np.min(input_array))

    return output_array


def panPeakDetect(detection, fs):    

    min_distance = int(0.25*fs)

    signal_peaks = [0]
    noise_peaks = []

    SPKI = 0.0
    NPKI = 0.0

    threshold_I1 = 0.0
    threshold_I2 = 0.0

    RR_missed = 0
    index = 0
    indexes = []

    missed_peaks = []
    peaks = []

    for i in range(1,len(detection)-1):
        if detection[i-1]<detection[i] and detection[i+1]<detection[i]:
            peak = i
            peaks.append(i)

            if detection[peak]>threshold_I1 and (peak-signal_peaks[-1])>0.3*fs:
                    
                signal_peaks.append(peak)
                indexes.append(index)
                SPKI = 0.125*detection[signal_peaks[-1]] + 0.875*SPKI
                if RR_missed!=0:
                    if signal_peaks[-1]-signal_peaks[-2]>RR_missed:
                        missed_section_peaks = peaks[indexes[-2]+1:indexes[-1]]
                        missed_section_peaks2 = []
                        for missed_peak in missed_section_peaks:
                            if missed_peak-signal_peaks[-2]>min_distance and signal_peaks[-1]-missed_peak>min_distance and detection[missed_peak]>threshold_I2:
                                missed_section_peaks2.append(missed_peak)

                        if len(missed_section_peaks2)>0:
                            signal_missed = [detection[i] for i in missed_section_peaks2]
                            index_max = np.argmax(signal_missed)
                            missed_peak = missed_section_peaks2[index_max]
                            missed_peaks.append(missed_peak)
                            signal_peaks.append(signal_peaks[-1])
                            signal_peaks[-2] = missed_peak   

            else:
                noise_peaks.append(peak)
                NPKI = 0.125*detection[noise_peaks[-1]] + 0.875*NPKI

            threshold_I1 = NPKI + 0.25*(SPKI-NPKI)
            threshold_I2 = 0.5*threshold_I1

            if len(signal_peaks)>8:
                RR = np.diff(signal_peaks[-9:])
                RR_ave = int(np.mean(RR))
                RR_missed = int(1.66*RR_ave)

            index = index+1      
    
    signal_peaks.pop(0)

    return signal_peaks
