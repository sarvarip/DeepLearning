import numpy as np # linear algebra
import os # accessing directory structure
import gc
import pickle
#from difflib import SequenceMatcher
from multiprocessing import Pool, Array, Lock
import time
import Levenshtein
import ctypes as c
from itertools import chain

    
def levdiff(a, b):
    return Levenshtein.distance(a, b) / min(len(a), len(b))
    

def thefunction(i):
    siz = len(seqs)
    with lock:
        print("Working on: " + str(i) + "/" + str(siz-1))
        # print(seqs[i])
        print(" ")
    string1 = seqs[i]
    for j in range(i+1,siz,1):
        string2 = seqs[j]
        ar = np.frombuffer(arr.get_obj()) # mp_arr and arr share the same memory
        b = ar.reshape((siz,siz)) # make it two-dimensional
        val = levdiff(string1, string2)
        b[i,j] = val
 
def initializer(*args):
    global lock, seqs, arr
    lock, seqs, arr = args

def parse_append (lines, seqs=[]):
    length = 0
    data = ''
    for line in lines:
        seqs.append(line.strip())
        length = length + 1
    return seqs, length
    
def extract_pos():

    pos_dirpath = './positive_struc'
    print('Available pos files: ', os.listdir(pos_dirpath))
            
    pos_seqs = []
    pos_labels = []
    for fn in os.listdir(pos_dirpath):
        handle = open(os.path.join(pos_dirpath, fn), 'r')
        pos_seqs, num_seq = parse_append(handle.read().split('\n'), pos_seqs)
        labs = [fn]*num_seq
        pos_labels.append(labs)
        handle.close()
        
    pos_labels = list(chain.from_iterable(pos_labels))
        
    return pos_seqs, pos_labels
            
def extract_aa():

    neg_dirpath = './positive_seq'

    neg_seqs = []
    neg_labels = []
    for fn in os.listdir(neg_dirpath):
        handle = open(os.path.join(neg_dirpath, fn), 'r')
        neg_seqs, num_seq = parse_append(handle.read().split('\n'), neg_seqs)
        labs = [fn]*num_seq
        neg_labels.append(labs)
        handle.close()
        
    neg_labels = list(chain.from_iterable(neg_labels))
    
    return neg_seqs, neg_labels
    
def reduce(seqs, labels, prepend):

    siz = len(seqs)
    arr = Array(c.c_double, siz*siz) # shared, can be used from multiple processes
    lock = Lock()	         
    numcores = 7
    pool = Pool(numcores, initializer, (lock, seqs, arr))
    s_parallel = time.time()
    pool.map(thefunction, range(siz))
    e_parallel = time.time()
    print("Total time to calculate similarity matrix: " + str(e_parallel - s_parallel))
    
    ar = np.frombuffer(arr.get_obj()) # mp_arr and arr share the same memory
    b = ar.reshape((siz,siz)) # make it two-dimensional
    
    print(b)

    path = "./" + prepend + "_sim_array" + ".pickle"
    output = open(path, 'w+b')
    pickle.dump(b, output)
    output.close()

    if prepend == "pos":
        path = "./" + prepend + "_labels" + ".pickle"
        output = open(path, 'w+b')
        pickle.dump(labels, output)
        output.close()
  
if __name__ == '__main__':
    seqs, labels = extract_pos()
    reduce(seqs, labels, "pos")
    seqs, labels = extract_aa()
    reduce(seqs, labels, "aa")
    

    

    

    
    