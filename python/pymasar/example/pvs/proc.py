import os
f = open('example.txt', 'r')
lines = f.readlines()
f.close()

for line in lines:
    cmd_string = 'caput %s.PROC 1' %(line[:-1])
    os.system(cmd_string)
