# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import os
import xmltodict
import glob
import json
import collections

def make_string_key_for_a_cut(cut_coefs):
    "make a string key for a cut using all it's variable names and value"
    "note that the key might be very long"
    key = ""
    for var_name, coef in cut_coefs.items():
        key = key + var_name + "{:.2f}".format(coef)

    return key

def check_sol_validity(sol: dict, cut: dict):
    sum  = 0
    for var_name, val in cut.items():
        if var_name == 'rhs':
            continue
        if var_name in sol:
            sum += val*sol[var_name]
        else:
            print("Error: variable does not exist in solution: {}".format(var_name))

    return sum <= cut['rhs']



#test_dict = { "test1":2.8877, "test2":9.89234798}

#key = make_string_key_for_a_cut(test_dict)


instancePath = '/Users/fqiu/JupyterNotes/savecpxcuts/Data/case1888rte/'
cwd = os.getcwd()
#os.chdir('/Users/fqiu/JupyterNotes/savecpxcuts/Data/case1888rte/')

# check each cut and they how many instances it appears in.
os.chdir('/Users/fqiu/JupyterNotes/savecpxcuts/Data/case1888rte/cuts/')
cwd = os.getcwd()

# define dicts for all types of cuts
f_stat = {}
i_stat = {}
L_stat = {}
m_stat = {}
r_stat = {}
v_stat = {}
z_stat = {}

f_cuts = []
i_cuts = []
L_cuts = []
m_cuts = []
r_cuts = []
v_cuts = []
z_cuts = []

cut_file_names = glob.glob('*_cuts.json')
# read each cut file
num_cuts = 0
for cut_file_name in cut_file_names:
    with open(cut_file_name) as json_file:
        data = json.load(json_file)
        instance_name = data['file name']
        cut_dict = data['cuts']
        for cut_name, coefs in cut_dict.items():
            num_cuts += 1
            coefs = dict(sorted(coefs.items()))
            key = make_string_key_for_a_cut(coefs)
            if cut_name[0] == 'f':
                f_cuts.append(coefs)
                if key in f_stat:
                    f_stat[key].append(instance_name)
                else:
                    f_stat[key] = []
                    f_stat[key].append(instance_name)
            elif cut_name[0] == 'i':
                i_cuts.append(coefs)
                if key in i_stat:
                    i_stat[key].append(instance_name)
                else:
                    i_stat[key] = []
                    i_stat[key].append(instance_name)
            elif cut_name[0] == 'L':
                L_cuts.append(coefs)
                if key in L_stat:
                    L_stat[key].append(instance_name)
                else:
                    L_stat[key] = []
                    L_stat[key].append(instance_name)
            elif cut_name[0] == 'm':
                m_cuts.append(coefs)
                if key in m_stat:
                    m_stat[key].append(instance_name)
                else:
                    m_stat[key] = []
                    m_stat[key].append(instance_name)
            elif cut_name[0] == 'r':
                r_cuts.append(coefs)
                if key in r_stat:
                    r_stat[key].append(instance_name)
                else:
                    r_stat[key] = []
                    r_stat[key].append(instance_name)
            elif cut_name[0] == 'v':
                v_cuts.append(coefs)
                if key in v_stat:
                    v_stat[key].append(instance_name)
                else:
                    v_stat[key] = []
                    v_stat[key].append(instance_name)
            elif cut_name[0] == 'z':
                z_cuts.append(coefs)
                if key in z_stat:
                    z_stat[key].append(instance_name)
                else:
                    z_stat[key] = []
                    z_stat[key].append(instance_name)
            else:
                pass


# statistics about how many times a cut appears in the instances
f_freq = {}
i_freq = {}
L_freq = {}
m_freq = {}
r_freq = {}
v_freq = {}
z_freq = {}

for value in f_stat.values():
    if len(value) in f_freq:
        f_freq[len(value)] += 1
    else:
        f_freq[len(value)] = 1
for value in i_stat.values():
    if len(value) in i_freq:
        i_freq[len(value)] += 1
    else:
        i_freq[len(value)] = 1
for value in L_stat.values():
    if len(value) in L_freq:
        L_freq[len(value)] += 1
    else:
        L_freq[len(value)] = 1
for value in m_stat.values():
    if len(value) in m_freq:
        m_freq[len(value)] += 1
    else:
        m_freq[len(value)] = 1
for value in r_stat.values():
    if len(value) in r_freq:
        r_freq[len(value)] += 1
    else:
        r_freq[len(value)] = 1
for value in v_stat.values():
    if len(value) in v_freq:
        v_freq[len(value)] += 1
    else:
        v_freq[len(value)] = 1
for value in z_stat.values():
    if len(value) in z_freq:
        z_freq[len(value)] += 1
    else:
        z_freq[len(value)] = 1

# print out the statistic results
print("f cuts: ", len(f_stat))
print(sorted(f_freq.items()))
print("i cuts: ", len(i_stat))
print(sorted(i_freq.items()))
print("L cuts: ", len(L_stat))
print(sorted(L_freq.items()))
print("m cuts: ", len(m_stat))
print(sorted(m_freq.items()))
print("r cuts: ", len(r_stat))
print(sorted(r_freq.items()))
print("v cuts: ", len(v_stat))
print(sorted(v_freq.items()))
print("z cuts: ", len(z_stat))
print(sorted(z_freq.items()))


# read all the json files in a dictionary


# take each cut from file and generate a key, and put it into a dictionary
sol_file_names = glob.glob(instancePath+'*.final.sol')

# read each solution file 
for sol_file_name in sol_file_names:
    with open(sol_file_name) as sol_file:
        sol = xmltodict.parse(sol_file.read())
        variables = sol['CPLEXSolution']['variables']['variable']
        solDict = {}
        # make a dict from a sol xml
        for var in variables:
            solDict[var['@name']] = float(var['@value'])
        # plug this solution into each cut and see the feasibility
        for cut in f_cuts:
            check_sol_validity(solDict, cut)
#        i_cuts = []
#        L_cuts = []
#        m_cuts = []
#        r_cuts = []
#        v_cuts = []
#        z_cuts = []

#with open(instancePath + './2017-01-01.1.final.sol') as fd:
#    doc = xmltodict.parse(fd.read())
#variables = doc['CPLEXSolution']['variables']['variable']


for var in variables:
    solDict[var['@name']] = float(var['@value'])

#

