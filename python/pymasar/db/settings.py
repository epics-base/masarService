'''
Created on Mar 7, 2012

@author: shengb
'''

"""
This is am template file how to config MASAR service configuration
and load service info, pv_group, and event configuration.
"""

# pv group name: [pv list file, description]
pvgroups= {
           # new pv groups for LN-LTB 20120511
           'LN_Sol_Set_20120511':          ['LN_LTB_Configure_20120511/LN_Sol_PV_Set.txt',           'linac solenoid current setpoint and on command'],
           'LN_Cor_Set_20120511':          ['LN_LTB_Configure_20120511/LN_Cor_PV_Set.txt',           'linac corrector x and y plane current setpoint and on command'],
           'LN_Quad_Set_20120511':         ['LN_LTB_Configure_20120511/LN_Quad_PV_Set.txt',          'linac Quads current setpoint and on command'],
           'LN_Gun_Set_20120511':          ['LN_LTB_Configure_20120511/LN_Gun_PV_Set.txt',           'linac gun operation Mode, grid voltage, SBM voltage, MBM voltage, and pulse voltage, and trigger event, delay, width setpoint'],
           'LN_LLRF_Set_20120511':         ['LN_LTB_Configure_20120511/LN_LLRF_PV_Set.txt',          'linac LLRF amplitude, phase, waveform, feedforward setting, tigger event, mode, delay, width including subharmonic buncher, pre-buncher, klystron 1, 2, and 3.'], 
           'LN_HLRF_Set_20120511':         ['LN_LTB_Configure_20120511/LN_HLRF_PV_Set.txt',          'linac HLRF modulator high voltage, pulse width, rep rate, tigger event, mode, delay, width of modulator 1, 2, and 3. '],
           'LN_LTB_Diag_Time_Set_20120511':['LN_LTB_Configure_20120511/LN_LTB_Diag_Time_PV_Set.txt', 'linac and LTB digitizer timing setpoint'],
           'LN_LTB_Dig_Time_Set_20120511': ['LN_LTB_Configure_20120511/LN_LTB_Diag_Scale_PV_Set.txt','linac and LTB digitizer scale setpoint'],
           'LN_LTB_CamGN_Set_20120511':    ['LN_LTB_Configure_20120511/LN_LTB_CamGN_PV_Set.txt',     'linac and LTB camera exposure time setpoint'],
           'LN_LTB_CamET_Set_20120511':    ['LN_LTB_Configure_20120511/LN_LTB_CamET_PV_Set.txt',     'linac and LTB camera gain setpoint'],
           'LN_LTB_CamTrig_Set_20120511':  ['LN_LTB_Configure_20120511/LN_LTB_CamTrig_PV_Set.txt',   'linac and LTB camera trigger setpoint and on command'],
           'LTB_MG_Set_20120511':          ['LN_LTB_Configure_20120511/LTB_MG_PV_Set.txt',           'LTB magnet setpoint and on command'],
           'LTB_CamFilt_Set_20120511':     ['LN_LTB_Configure_20120511/LTB_CamFilt_PV_Set.txt',      'LTB camera filter setpoint'],
           'LTB_ES_Set_20120511':          ['LN_LTB_Configure_20120511/LTB_ES_PV_Set.txt',           'LTB energy slit motor setpoint'],
           'LN_Time_PV_Set_20120511':      ['LN_LTB_Configure_20120511/LN_Time_PV_Set.txt',          'LN timing setpoint']
#           #LN-LTB-PhaseI-SBM-All_20120426
#           'LN_Sol_Set':           ['LN_Sol_PV_Set.txt',            "linac solenoid current setpoint"],
#           'LN_Cor_Set':           ['LN_Cor_PV_Set.txt',            "linac corrector x and y plane current setpoint"],
#           'LN_Quad_Set':          ['LN_Quad_PV_Set.txt',           "linac Quads current setpoint"],
#           'LN_Gun_SBM_Set':       ['LN_Gun_SBM_PV_Set.txt',        "linac gun operation Mode, grid voltage, SBM voltage, MBM voltage, and pulse voltage, and trigger event, delay, width setpoint"],
#           'LN_LLRF_SBM_Set':      ['LN_LLRF_SBM_PV_Set.txt',       "linac LLRF amplitude, phase, waveform, tigger event, mode, delay, width including subharmonic buncher, pre-buncher, klystron 1, 2, and 3."], 
#           'LN_HLRF_SBM_Set':      ['LN_HLRF_SBM_PV_Set.txt',       "linac HLRF modulator high voltage, pulse width, rep rate, tigger event, mode, delay, width of modulator 1, 2, and 3. "],
#           'LN_LTB_Diag_Time_Set': ['LN_LTB_Diag_Time_PV_Set.txt',  "linac and LTB digitizer timing setpoint"],
#           'LN_LTB_Dig_Time_Set':  ['LN_LTB_Diag_Scale_PV_Set.txt', "linac and LTB digitizer scale setpoint"],
#           'LN_LTB_CamGN_Set':     ['LN_LTB_CamGN_PV_Set.txt',      "linac and LTB camera exposure time setpoint"],
#           'LN_LTB_CamET_Set':     ['LN_LTB_CamET_PV_Set.txt',      "linac and LTB camera gain setpoint"],
#           'LN_LTB_CamTrig_Set':   ['LN_LTB_CamTrig_PV_Set.txt',    "linac and LTB camera trigger setpoint"],
#           'LTB_MG_Set':           ['LTB_MG_PV_Set.txt',            "LTB magnet setpoint"],
#           'LTB_CamFilt_Set':      ['LTB_CamFilt_PV_Set.txt',       "LTB camera filter setpoint"],
#           'LTB_ES_Set':           ['LTB_ES_PV_Set.txt',            "LTB energy slit motor setpoint"],
#           'LN_Dev_OnOff_Set':     ['LN_DeV_OnOff_PV_Set.txt',      "linac device on-off setpoint"],
#           'LTB_Dev_OnOff_Set':    ['LTB_DeV_OnOff_PV_Set.txt',     "LTB device on-off setpoint"]
#           'VA_SR_MAG_SET':       ['virtsr.masar.mg.sp.txt', "virtual storage ring magnet set point"]
#           'LN_RF_set_20120402':       ['LN/Set_PV/LN_RF_PV_set_20120402.txt', "linac RF amplitude, phase, new pvs added"]
#           # LN_PhaseI_SC_All
#           'LN_FC_read':      ['LN/Read_PV/LN_FC_PV_read.txt', "Linac faraday cup bunch number, aver. Charge, std. Charge Error, Interest shot number  and waveform readback"],
#           'LN_Flag_read':    ['LN/Read_PV/LN_Flag_read.txt',  "linac flag's image, x/y  min. start position, x/y range,  centriods and rms sizes"],
#           'LN_WCM_read':     ['LN/Read_PV/LN_WCM_PV_read.txt', "linac WCM waveform readback"],
#           'LN_BPM_read':     ['LN/Read_PV/LN_BPM_PV_read.txt', "Linac measured aver. , std. Error and Interest shot number for x, y position and sum signal readback"],
#           'LN_Timing_RF_Gun_Read':	['LN/Read_PV/LN_Timing_RF_Gun_Read.txt', "LN timing for PBU/SPB/LLRF 1,2,3/MOD 1,2,3/RF Det./PPT TDU/eGun SBM delay, width, divider,  timing mode readback"],
#           # LN_PhaseI_SCR_All
#           'LN_Gun_Set':      ['LN/Set_PV/LN_Gun_PV_set.txt', "linac gun operation Mode, grid voltage, MBM Voltage,  pulse voltage,"],
#           'LN_Cor_set':      ['LN/Set_PV/LN_Cor_PV_set.txt', "linac corrector x and y plane current setpoint"],
#           'LN_Sol_set':      ['LN/Set_PV/LN_Sol_PV_set.txt', "linac solenoid current setpoint"],
#           'LN_RF_set':       ['LN/Set_PV/LN_RF_PV_set.txt', "linac RF amplitude, phase"],
#           'LN_BPM_set':      ['LN/Set_PV/LN_BPM_PV_set.txt', "linac BPM golden traj x and y setpoint"],
#           'LN_aperture_set': ['LN/Set_PV/LN_aperture_PV_set.txt', "linac aperture position setpoint"],
#           'LN_WCM_Set':      ['LN/Set_PV/LN_WCM_PV_set.txt', "linac WCM zero offset, range, sample length setpoint"],
#           'LN_Quad_set':     ['LN/Set_PV/LN_Quad_PV_set.txt', "linac Quads current setpoint"],
#           'LN_FC_set':       ['LN/Set_PV/LN_FC_PV_set.txt', "linac faraday cup zero offset, range, sample length setpoint"],
#           'LN_Timing_RF_Gun_set':	['LN/Set_PV/LN_Timing_RF_Gun_set.txt', "LN timing for PBU/SPB/LLRF 1,2,3/MOD 1,2,3/RF Det./PPT TDU/eGun SBM delay, width, divider, ref. event, timing mode"],
#           # LTD1_PhaseI_SC_All
#           'LTD1_BPM_read':   ['LTD1/Read_PV/LTD1_BPM_PV_read.txt', "Linac to dump1 beam line measured aver. , std. Error and Interest shot number for x, y position and sum signal readback"],
#           'LTD1_Flag_read':  ['LTD1/Read_PV/LTD1_Flag_PV_read.txt',"Linac to dump1 beam line flag's image, x/y  min. start position, centriods and rms sizes"],
#           'LTD1_ICT_read':   ['LTD1/Read_PV/LTD1_ICT_PV_read.txt', "Linac to dump1 beam line ICT aver. Charge, std. Charge Error and Interest shot number readback"],
#           'LTD1_FC_read':    ['LTD1/Read_PV/LTD1_FC_PV_read.txt',  "Linac to dump1 beam line faraday cup aver. Charge, std. Charge Error, Interest shot number  and waveform readback"],
#           'LTB_Dump12_Timing_Read': ['LTD1/Read_PV/LTB_Dump12_Timing_Read.txt', "LTB dump12 timing for Flag, FC, FCT, ICT-output, BCM-output, BCM1-Trig and BCM2-Trig's delay, width, divider, ref. event"],
#           #LTD1_PhaseI_SCR_All
#           'LTD1_BPM_set':    ['LTD1/Set_PV/LTD1_BPM_PV_set.txt',  "Linac to dump1 beam line BPM golden traj x and y setpoint"],
#           'LTD1_Flag_set':   ['LTD1/Set_PV/LTD1_Flag_PV_set.txt', "Linac to dump1 beam line flag position and filter wheel position setpoint"],
#           'LTD1_Cor_set':    ['LTD1/Set_PV/LTD1_Cor_PV_set.txt',  "Linac to dump1 beam line corrector x and y plane current setpoint"],
#           'LTD1_Quad_set':   ['LTD1/Set_PV/LTD1_Quad_PV_set.txt', "Linac to dump1 beam line Quads current setpoint"],
#           'LTD1_ICT_set':    ['LTD1/Set_PV/LTD1_ICT_PV_set.txt',  "Linac to dump1 beam line ICT gain, BCM output's and signal's zerooffset, range, sample length setpoint"],
#           'LTD1_Bend_set':   ['LTD1/Set_PV/LTD1_Bend_PV_set.txt', "Linac to dump1 beam line dipole magnet setpoint"],
#           'LTD1_FC_set':     ['LTD1/Set_PV/LTD1_FC_PV_set.txt',   "Linac to dump1 beam line faraday cup zerooffset, range, sample length setpoint"],
#           'LTB_Dump12_Timing_set': ['LTD1/Set_PV/LTB_Dump12_Timing_set.txt', "LTB dump12 timing for Flag, FC, FCT, ICT-output, BCM-output, BCM1-Trig and BCM2-Trig's delay, width, divider, ref. event"],
#           #LTD2_PhaseI_SC_All
#           'LTD2_BPM_read':   ['LTD2/Read_PV/LTD2_BPM_PV_read.txt', "Linac to dump2 beam line measured aver. , std. Error and Interest shot number for x, y position and sum signal readback"],
#           'LTD2_Flag_read':  ['LTD2/Read_PV/LTD2_Flag_PV_read.txt',"Linac to dump2 beam line flag's image, x/y min. start position,  centriods and rms sizes"],
#           'LTD2_ES_read':    ['LTD2/Read_PV/LTD2_ES_PV_read.txt',  "Linac to dump2 beam line flag's image, x plane min. start position, centriods and rms sizes"],
#           'LTD2_FCT_read':   ['LTD2/Read_PV/LTD2_FCT_PV_read.txt', "Linac to dump2 beam line FCT waveform readback"],
#           'LTD2_ICT_read':   ['LTD2/Read_PV/LTD2_ICT_PV_read.txt', "Linac to dump2 beam line ICT aver. Charge, std. Charge Error and Interest shot number readback"],
#           'LTD2_FC_read':    ['LTD2/Read_PV/LTD2_FC_PV_read.txt',  "Linac to dump2 beam line faraday cup aver. Charge, std. Charge Error, Interest shot number  and waveform readback"],
#           #LTD2_PhaseI_SCR_All
#           'LTD2_BPM_set':    ['LTD2/Set_PV/LTD2_BPM_PV_set.txt',  "Linac to dump2 beam line BPM golden traj x and y setpoint"],
#           'LTD2_Flag_set':   ['LTD2/Set_PV/LTD2_Flag_PV_set.txt', "Linac to dump2 beam line flag position and filter wheel position setpoint"],
#           'LTD2_Cor_set':    ['LTD2/Set_PV/LTD2_Cor_PV_set.txt',  "Linac to dump2 beam line corrector x and y plane current setpoint"],
#           'LTD2_Quad_set':   ['LTD2/Set_PV/LTD2_Quad_PV_set.txt', "Linac to dump2 beam line Quads current setpoint"],
#           'LTD2_Bend_set':   ['LTD2/Set_PV/LTD2_Bend_PV_set.txt', "Linac to dump2 beam line dipole magnet setpoint"],
#           'LTD2_ES_set':     ['LTD2/Set_PV/LTD2_ES_PV_set.txt',   "Linac to dump2 beam line energy slit blade position setpoint"],
#           'LTD2_FCT_set':    ['LTD2/Set_PV/LTD2_FCT_PV_set.txt',  "Linac to dump2 beam line  FCT zerooffset, range, sample length setpoint"],
#           'LTD2_ICT_set':    ['LTD2/Set_PV/LTD2_ICT_PV_set.txt',  "Linac to dump2 beam line ICT gain, BCM output's and signal's zerooffset, range, sample length setpoint"],
#           'LTD2_FC_set':     ['LTD2/Set_PV/LTD2_FC_PV_set.txt',   "Linac to dump2 beam line faraday cup zerooffset, range, sample length setpoint"]
}

# config name: [config desc, system]
configs= {
          'LN-LTB-PhaseI-All_20120511': ['Linac and LTB daily SCR setpoint', 'Linac, LTB']
#          'LN-LTB-PhaseI-SBM-All_20120426': ['Linac and LTB daily SCR setpoint', 'Linac, LTB']
#          'VA_SR_MAG_SET':   ['virtual storage magnet setpoint on Apr 05, 2012','virtac']
#          'LN_PhaseI_SCR_All_20120402':   ['Linac daily SCR setpoint on Apr 02, 2012','Linac']
#          'LN_PhaseI_SC_All':    ['Linac daily reference',   'Linac'],
#          'LN_PhaseI_SCR_All':   ['Linac daily SCR setpoint','Linac'],
#          'LTD1_PhaseI_SC_All':  ['LTD1 daily reference',    'LTD1'],
#          'LTD1_PhaseI_SCR_All': ['LTD1 daily SCR setpoint', 'LTD1'], 
#          'LTD2_PhaseI_SC_All':  ['LTD2 daily reference',    'LTD2'],
#          'LTD2_PhaseI_SCR_All': ['LTD2 daily SCR setpoint', 'LTD2']
}

# config name: [pvgroup,]
pvg2config= {
             'LN-LTB-PhaseI-All_20120511': ['LN_Sol_Set_20120511',
                                            'LN_Cor_Set_20120511',
                                            'LN_Quad_Set_20120511',
                                            'LN_Gun_Set_20120511',
                                            'LN_LLRF_Set_20120511',
                                            'LN_HLRF_Set_20120511',
                                            'LN_LTB_Diag_Time_Set_20120511',
                                            'LN_LTB_Dig_Time_Set_20120511',
                                            'LN_LTB_CamGN_Set_20120511',
                                            'LN_LTB_CamET_Set_20120511',
                                            'LN_LTB_CamTrig_Set_20120511',
                                            'LTB_MG_Set_20120511',
                                            'LTB_CamFilt_Set_20120511',
                                            'LTB_ES_Set_20120511',
                                            'LN_Time_PV_Set_20120511'
                                            ]
#             'LN-LTB-PhaseI-SBM-All_20120426': ['LN_Sol_Set','LN_Cor_Set','LN_Quad_Set','LN_Gun_SBM_Set','LN_LLRF_SBM_Set','LN_HLRF_SBM_Set',
#                                                'LN_LTB_Diag_Time_Set','LN_LTB_Dig_Time_Set','LN_LTB_CamGN_Set','LN_LTB_CamET_Set','LN_LTB_CamTrig_Set',
#                                                'LTB_MG_Set','LTB_CamFilt_Set','LTB_ES_Set','LN_Dev_OnOff_Set','LTB_Dev_OnOff_Set']
#             'VA_SR_MAG_SET':    ['VA_SR_MAG_SET']
#             'LN_PhaseI_SCR_All_20120402': ['LN_Gun_Set', 'LN_Cor_set', 'LN_Sol_set', 'LN_RF_set_20120402', 'LN_BPM_set', 'LN_aperture_set', 'LN_WCM_Set', 'LN_Quad_set', 'LN_FC_set', 'LN_Timing_RF_Gun_set'],
#             'LN_PhaseI_SC_All':     ['LN_FC_read', 'LN_Flag_read', 'LN_WCM_read', 'LN_BPM_read', 'LN_Timing_RF_Gun_Read'],
#             'LN_PhaseI_SCR_All':    ['LN_Gun_Set', 'LN_Cor_set', 'LN_Sol_set', 'LN_RF_set', 'LN_BPM_set', 'LN_aperture_set', 'LN_WCM_Set', 'LN_Quad_set', 'LN_FC_set', 'LN_Timing_RF_Gun_set'],
#             'LTD1_PhaseI_SC_All':   ['LTD1_BPM_read', 'LTD1_Flag_read', 'LTD1_ICT_read', 'LTD1_FC_read', 'LTB_Dump12_Timing_Read'],
#             'LTD1_PhaseI_SCR_All':  ['LTD1_BPM_set', 'LTD1_Flag_set', 'LTD1_Cor_set', 'LTD1_Quad_set', 'LTD1_ICT_set', 'LTD1_Bend_set', 'LTD1_FC_set', 'LTB_Dump12_Timing_set'],
#             'LTD2_PhaseI_SC_All':   ['LTD2_BPM_read', 'LTD2_Flag_read', 'LTD2_ES_read', 'LTD2_FCT_read', 'LTD2_ICT_read', 'LTD2_FC_read'],
#             'LTD2_PhaseI_SCR_All':  ['LTD2_BPM_set', 'LTD2_Flag_set', 'LTD2_Cor_set', 'LTD2_Quad_set', 'LTD2_Bend_set', 'LTD2_ES_set', 'LTD2_FCT_set', 'LTD2_ICT_set', 'LTD2_FC_set']
}
