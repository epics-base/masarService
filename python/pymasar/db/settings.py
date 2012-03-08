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
#    'test':         ['example.txt', 'server test'],
#    'wftest':       ['exampleWf.txt', 'server test with waveform'],
#    'bigwftest':    ['exampleBigWf.txt', 'server test with big waveform']
}

# config name: [config desc, system]
configs= {
#    'sr_test':      ['test pv config', 'test'],
#    'wf_test':      ['waveform test pv config', 'test'],
#    'bwf_test':     ['big waveform test pv config', 'test']
}

# config name: [pvgroup,]
pvg2config= {
#    'sr_test':   ['test'],
#    'wf_test':   ['wftest'],
#    'bwf_test':  ['wftest', 'bigwftest']
}
