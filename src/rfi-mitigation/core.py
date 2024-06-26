
import numpy as np
import os,sys
import matplotlib.pyplot as plt

import scipy as sp
import scipy.optimize
import scipy.special
import math as math

import argparse

import time

from blimpy import GuppiRaw

from utils import *

import iqrm

import RFI_detection as rfi
from tqdm import tqdm






class mitigateRFI:
    """
    blah blah blah
    
    Parameters
    ----------
        det_method : str
            RFI detection method used.
        inputfile : str
            input file
        repl_method : str
            replacement method
        cust : str
            
    
    """
    def __init__(self):


        #default/hardcoded attributes
        self.in_dir = '/data/rfimit/unmitigated/rawdata/'#move to actual data dir
        self._rawFile = GuppiRaw(infile)


    def run_all(self):
        #do all the rfi mitigation steps

       start_time = time.time()
       if self.output_bool:
                template_check_outfile(infile,outfile)
                out_rawFile = open(outfile,'rb+')

        
        template_check_nblocks(rawFile,mb)
        numblocks = self.rawFile.find_n_data_blocks()

        for bi in range(numblocks//mb):
            print('------------------------------------------')
            print(f'Block: {(block*mb)+1}/{numblocks}')


            #print header for the first block
            if bi == 0:
                template_print_header(rawFile)


            #loading multiple blocks at once?        
            for mb_i in range(mb):
                if mb_i==0:
                header,data = rawFile.read_next_data_block()
                data = np.copy(data)
                d1s = data.shape[1]
            else:
                h2,d2 = rawFile.read_next_data_block()
                data = np.append(data,np.copy(d2),axis=1)

            #find data shape
            num_coarsechan = data.shape[0]
            num_timesamples= data.shape[1]
            num_pol = data.shape[2]
            print(f'Data shape: {data.shape} || block size: {data.nbytes}')

            #save raw data?
            if rawdata:
                template_save_npy(data,block,npy_base)    
       

            spect_block = template_averager(data, self.ave_factor)


            #===============================================
            #***********************************************

            if self.method = 'SK':
                flags_block, ss_sk_block, ms_sk_block = sk-rfi.SK_detection(self,data)
                if bi == 0:
                    self.ss_sk_all = ss_sk_block
                    self.ms_sk_all = ms_sk_block
                else:
                    self.ss_sk_all = np.concatenate((self.ss_sk_all, ss_sk_block),axis=1)
                    self.ms_sk_all = np.concatenate((self.ms_sk_all, ms_sk_block),axis=1)

            elif self.method = 'IQRM':
                pass



            #track intermediate results
            if bi == 0:
                self.flags_all = flags_block
                self.spect_all = spect_block
            else:
                self.flags_all = np.concatenate((self.flags_all, flags_block),axis=1)
                self.spect_all = np.concatenate((self.spect_all, spect_block),axis=1)


            #***********************************************
            #===============================================

            



            #track flags
            print(f'Pol 0: {np.around(np.mean(flags_block[:,:,0]),2)}% flagged')
            print(f'Pol 1: {np.around(np.mean(flags_block[:,:,1]),2)}% flagged')

            uf = flags_block[:,:,0]
            uf[flags_block[:,:,1] == 1] = 1

            print(f'Union: {np.around(np.mean(uf),2)}% flagged')

            #now flag shape is (chan,spectra,pol)
            #apply union of flags between the pols
            if combine_flag_pols:
                flags_block[:,:,0][flags_block[:,:,1]==1]=1
                flags_block[:,:,1][flags_block[:,:,0]==1]=1


            ts_factor = data.shape[1] // flags_block.shape[1]
            if (data.shape[1] % flags_block.shape[1] != 0):
                print('Flag chunk size is incompatible with block size')
                sys.exit()
                

            if repl_method == 'nans':
                data = repl_nans(data,flags_block
            if repl_method == 'zeros':
                #replace data with zeros
                data = repl_zeros(data,flags_block)

            if repl_method == 'previousgood':
                #replace data with previous (or next) good
                data = previous_good(data,flags_block,ts_factor)

            if repl_method == 'stats':
                #replace data with statistical noise derived from good datapoints
                data = statistical_noise_fir(data,flags_block,ts_factor)


            #save the regenerated spectra
            regen_block = template_averager(data, self.ave_factor)

            if bi == 0:
                self.regen_all = regen_block
            else:
                self.regen_all = np.concatenate((self.regen_all, regen_block),axis=1)


            #write back raw data
            if output_bool:
                print('Re-formatting data and writing back to file...')
                for mb_i in range(mb):
                    out_rawFile.seek(headersize,1)
                    d1 = template_guppi_format(data[:,d1s*mb_i:d1s*(mb_i+1),:])
                    out_rawFile.write(d1.tostring())


        #===============================================
        #***********************************************

        #save output numpy arrays

        print(f'Flags: {self._flags_filename}')
        np.save(self._flags_filename, self.flags_all)
        print(f'Spect: {self._spect_filename}')
        np.save(self._spect_filname, self.spect_all)
        print(f'Regen: {self._regen_filename}')
        np.save(self._regen_filname, self.regen_all)


        if det_method = 'SK':
            print(f'SS-SK: {self._ss_sk_filename}')
            np.save(self._sk_filename, self.ss_sk)
            print(f'MS-SK: {self._ms_sk_filename}')
            np.save(self._mssk_filname, self.ms_sk)
            #need to add the logging thing


        #***********************************************
        #===============================================

        
        #flagging stuff
        template_print_flagstats(flags_all)



        #umm... done?
        end_time = time.time()
        dur = np.around((end_time-start_time)/60, 2)

        print(f'Duration: {dur} minutes')

































