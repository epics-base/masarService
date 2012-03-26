'''
Created on Mar 7, 2012

@author: shengb
'''

"""
This is am template file how to config MASAR serviceconfiguration
and load service info, pv_group, and event configuration.
"""

# pv group name: [pv list file, description]
pvgroups= {
           #test
           'test':            ['example.txt', 'server test'],
           'wftest':          ['exampleWf.txt', 'server test with waveform'],
           'bigwftest':       ['exampleBigWf.txt', 'server test with big waveform'],
           #LTD2_SC_Daily_All
           'LTD2_BPM_read':   ['LTD2/Read_PV/LTD2_BPM_PV_read.txt', "Linac to dump2 beam line measured aver. , std. Error and Interest shot number for x, y position and sum signal readback"],
           'LTD2_Flag_read':  ['LTD2/Read_PV/LTD2_Flag_PV_read.txt',"Linac to dump2 beam line flag's image, x/y min. start position,  centriods and rms sizes"],
           'LTD2_ES_read':    ['LTD2/Read_PV/LTD2_ES_PV_read.txt',  "Linac to dump2 beam line flag's image, x plane min. start position, centriods and rms sizes"],
           'LTD2_FCT_read':   ['LTD2/Read_PV/LTD2_FCT_PV_read.txt', "Linac to dump2 beam line FCT waveform readback"],
           'LTD2_ICT_read':   ['LTD2/Read_PV/LTD2_ICT_PV_read.txt', "Linac to dump2 beam line ICT aver. Charge, std. Charge Error and Interest shot number readback"],
           'LTD2_FC_read':    ['LTD2/Read_PV/LTD2_FC_PV_read.txt',  "Linac to dump2 beam line faraday cup aver. Charge, std. Charge Error, Interest shot number  and waveform readback"],
           #LTD2_SCR_Daily_All
           'LTD2_BPM_set':    ['LTD2/Set_PV/LTD2_BPM_PV_set.txt',  "Linac to dump2 beam line BPM golden traj x and y setpoint"],
           'LTD2_Flag_set':   ['LTD2/Set_PV/LTD2_Flag_PV_set.txt', "Linac to dump2 beam line flag position and filter wheel position setpoint"],
           'LTD2_Cor_set':    ['LTD2/Set_PV/LTD2_Cor_PV_set.txt',  "Linac to dump2 beam line corrector x and y plane current setpoint"],
           'LTD2_Quad_set':   ['LTD2/Set_PV/LTD2_Quad_PV_set.txt', "Linac to dump2 beam line Quads current setpoint"],
           'LTD2_Bend_set':   ['LTD2/Set_PV/LTD2_Bend_PV_set.txt', "Linac to dump2 beam line dipole magnet setpoint"],
           'LTD2_ES_set':     ['LTD2/Set_PV/LTD2_ES_PV_set.txt',   "Linac to dump2 beam line energy slit blade position setpoint"],
           'LTD2_FCT_set':    ['LTD2/Set_PV/LTD2_FCT_PV_set.txt',  "Linac to dump2 beam line  FCT zerooffset, range, sample length setpoint"],
           'LTD2_ICT_set':    ['LTD2/Set_PV/LTD2_ICT_PV_set.txt',  "Linac to dump2 beam line ICT gain, BCM output's and signal's zerooffset, range, sample length setpoint"],
           'LTD2_FC_set':     ['LTD2/Set_PV/LTD2_FC_PV_set.txt',   "Linac to dump2 beam line faraday cup zerooffset, range, sample length setpoint"],
           # LTD1_SC_Daily_All
           'LTD1_BPM_read':   ['LTD1/Read_PV/LTD1_BPM_PV_read.txt', "Linac to dump1 beam line measured aver. , std. Error and Interest shot number for x, y position and sum signal readback"],
           'LTD1_Flag_read':  ['LTD1/Read_PV/LTD1_Flag_PV_read.txt',"Linac to dump1 beam line flag's image, x/y  min. start position, centriods and rms sizes"],
           'LTD1_ICT_read':   ['LTD1/Read_PV/LTD1_ICT_PV_read.txt', "Linac to dump1 beam line ICT aver. Charge, std. Charge Error and Interest shot number readback"],
           'LTD1_FC_read':    ['LTD1/Read_PV/LTD1_FC_PV_read.txt',  "Linac to dump1 beam line faraday cup aver. Charge, std. Charge Error, Interest shot number  and waveform readback"],
           #LTD1_SCR_Daily_All
           'LTD1_BPM_set':    ['LTD1/Set_PV/LTD1_BPM_PV_set.txt',  "Linac to dump1 beam line BPM golden traj x and y setpoint"],
           'LTD1_Flag_set':   ['LTD1/Set_PV/LTD1_Flag_PV_set.txt', "Linac to dump1 beam line flag position and filter wheel position setpoint"],
           'LTD1_Cor_set':    ['LTD1/Set_PV/LTD1_Cor_PV_set.txt',  "Linac to dump1 beam line corrector x and y plane current setpoint"],
           'LTD1_Quad_set':   ['LTD1/Set_PV/LTD1_Quad_PV_set.txt', "Linac to dump1 beam line Quads current setpoint"],
           'LTD1_ICT_set':    ['LTD1/Set_PV/LTD1_ICT_PV_set.txt',  "Linac to dump1 beam line ICT gain, BCM output's and signal's zerooffset, range, sample length setpoint"],
           'LTD1_Bend_set':   ['LTD1/Set_PV/LTD1_Bend_PV_set.txt', "Linac to dump1 beam line dipole magnet setpoint"],
           'LTD1_FC_set':     ['LTD1/Set_PV/LTD1_FC_PV_set.txt',   "Linac to dump1 beam line faraday cup zerooffset, range, sample length setpoint"]
}

# config name: [config desc, system]
configs= {
          # test
          'sr_test':              ['test pv config', 'test'],
          'wf_test':              ['waveform test pv config', 'test'],
          'bwf_test':             ['big waveform test pv config', 'test'],
          # LTD2
          'LTD2_SC_Daily_All':    ['LTD2 daily reference',    'LTD2'],
          'LTD2_SCR_Daily_All':   ['LTD2 daily SCR setpoint', 'LTD2'],
          # LTD1
          'LTD1_SC_Daily_All':    ['LTD1 daily reference',    'LTD1'],
          'LTD1_SCR_Daily_All':   ['LTD1 daily SCR setpoint', 'LTD1'] 
}

# config name: [pvgroup,]
pvg2config= {
             # test
             'sr_test':             ['test'],
             'wf_test':             ['wftest'],
             'bwf_test':            ['wftest', 'bigwftest'],
             # LTD2
             'LTD2_SC_Daily_All':   ['LTD2_BPM_read', 'LTD2_Flag_read', 'LTD2_ES_read', 'LTD2_FCT_read', 'LTD2_ICT_read', 'LTD2_FC_read'],
             'LTD2_SCR_Daily_All':  ['LTD2_BPM_set', 'LTD2_Flag_set', 'LTD2_Cor_set', 'LTD2_Quad_set', 'LTD2_Bend_set', 'LTD2_ES_set', 'LTD2_FCT_set', 'LTD2_ICT_set', 'LTD2_FC_set'],
             # LTD1
             'LTD1_SC_Daily_All':   ['LTD1_BPM_read', 'LTD1_Flag_read', 'LTD1_ICT_read', 'LTD1_FC_read'],
             'LTD1_SCR_Daily_All':  ['LTD1_BPM_set', 'LTD1_Flag_set', 'LTD1_Cor_set', 'LTD1_Quad_set', 'LTD1_ICT_set', 'LTD1_Bend_set', 'LTD1_FC_set']
}
