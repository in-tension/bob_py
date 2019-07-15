raw = """L1-L1: 1-13
L1-L2: 1-12
L1-L3: 1-13
L1-R1: 1-13
L1-R2: 1-12
L1-R4: 1-12
L2-L1: 1-18
L2-L2: 1-15
L2-L3: 1-15
L2-R1: 1-14
L2-R3: 1-15
L3-L1: 1-13
L3-L2: 1-13
L3-L3: 1-15
L3-R1: 1-13
L3-R2: 1-13
L3-R3: 1-12
L4-L1: 1-17
L4-L2: 1-14
L4-R1: 1-14
"""



lines = raw.splitlines()


for line in lines :
    hseg, slices = line.split(': ')
    top, bot = slices.split('-')
    print('"{}": [{},{}],'.format(hseg, top, bot))
