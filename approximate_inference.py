import json
import random
import time

#from exact_inference_main.exact_inference_main.exact_inference import Bayes_Net


############################
def likelihood_weighting(qv_name, bn, N, E = {}):

    W = [0, 0]
    order = get_topological_order(bn)

    for j in range(N):
        eventx, w = _weighted_sample(bn, E, order)
        xval = eventx.get(qv_name)
        if(xval == 0):
            W[0] += w
        elif(xval == 1):
            W[1] += w
        else: 
            print(xval)
            print('err894')
            exit()

    return W

def _weighted_sample(bn, E, order): #returns event and weight
    w = 1
    eventx = dict.fromkeys(bn.keys(), -1)
    for v in E: 
        if(v in eventx): 
            eventx.update({v: E.get(v)})
        else:
            print('error 190')
            exit()
    #the event has been made

    #iterates over keys(vars) in eventx
    for X in order:
        X = str(X)

        if(X in E):
            xval = E.get(X)
            if(xval == 0):
                w = w * (1-exact_prob_given_parents(X, bn, eventx))
            elif(xval == 1):
                w = w * exact_prob_given_parents(X, bn, eventx)
        else:
            prob = exact_prob_given_parents(X, bn, eventx)
            xval = -1
            rval = random.random()
            if(rval < prob):
                xval = 1
            elif(rval >= prob):
                xval = 0
            else:
                print('err829')
                exit()
            eventx.update({X: xval})
    return eventx, w
############################




##########################
def gibbs_sampling(qv_name, bn, N, x = {}, E = {}):

    #counter of values for qv_name
    C = [0, 0]

    #add child pointers
    bn = add_child_pointers(bn)

    #nonevid vars
    z = list(bn.keys())

    if(not bool(x)):
        #init x
        x = dict.fromkeys(bn.keys(), random.randint(0, 1))

        for v in E: 
            z.remove(v)
            if(v in x): 
                x.update({v: E.get(v)})
            else:
                print('error 191')
                exit()
    
    for k in range(N):
        var_to_change = random.choice(z)
        p_of_var_to_change = exact_prob_given_markov_blanket(var_to_change, bn, x)
        r_val = random.random()

        if(r_val < p_of_var_to_change):
            x.update({var_to_change:1})
        elif(r_val >= p_of_var_to_change):
            x.update({var_to_change:0})
        else:
            print('err7583')
            exit()
        
        if(x.get(qv_name) == 0):
            C[0] += 1
        elif(x.get(qv_name) == 1):
            C[1] += 1
        else:
            print('err589')
            exit()
        
    return C, x

        


def metropolis_hastings(p, qv_name, bn, N, E = {}):

    order = get_topological_order(bn)

    counts = [0, 0]

    x = {}
    
    r_val = random.random()
    true_count = 0

    while(N>0): 

        while(r_val < p and N>1):

            true_count+=1
            r_val = random.random()
            N-=1
        
        C, x = gibbs_sampling(qv_name, bn, true_count, x, E)

        counts = [x + y for (x, y) in zip(C, counts)] 

        x, weight = _weighted_sample(bn, E, order)
        N-=1

        if(x.get(qv_name) == 1):
            counts[1] += 1
        elif(x.get(qv_name) == 0):
            counts[0] += 1
        else: 
            print('err8413')

    return counts
        






#qv_name: string containing query var name
#bn: dict w/ bayesian network
#E: dict w/ evidence vars. All parents of qv must be given
#returns: float w/ prob of qv=True based on parents of qv
def exact_prob_given_parents(qv_name, bn, E):
    qv = bn.get(str(qv_name))
    par_vals = []
    for p in qv.get('parents'):
        
        par_val = E.get(str(p))

        if(par_val == -1):
            print('err9082')
            exit()
        par_vals.append(par_val)

    for l in qv.get('prob'):
        if(l[0] == par_vals):
            return l[1]

    print("failure901")
    exit()

#qv_name: string containing query var name
#bn: dict w/ bayesian network
#E: dict w/ evidence vars. All parents of qv must be given
#returns: float w/ prob of qv=True based on markov blanket of qv
def exact_prob_given_markov_blanket(qv_name, bn, x):

    x_true_copy = x.copy()
    x_true_copy.update({qv_name: 1})
    x_false_copy = x.copy()
    x_false_copy.update({qv_name: 0})

    true_factor = exact_prob_given_parents(qv_name, bn, x)
    false_factor = 1 - true_factor


    for child in bn.get(qv_name).get('children'):
        
        if(x.get(child) == 0):
            true_factor = true_factor * (1-exact_prob_given_parents(child, bn, x_true_copy))
            false_factor = false_factor * (1-exact_prob_given_parents(child, bn, x_false_copy))
        elif(x.get(child) == 1):
            true_factor = true_factor * exact_prob_given_parents(child, bn, x_true_copy)
            false_factor = false_factor * exact_prob_given_parents(child, bn, x_false_copy)
    
    
    normed = [false_factor/(false_factor+true_factor), true_factor/(false_factor+true_factor)]

    return normed[1]


    


    child_prob = 1
    for child in bn.get(qv_name).get('children'):
        child_prob = child_prob * exact_prob_given_markov_blanket(child, bn, x)
    
    return prob_considering_pars*child_prob
    

#input bn
#returns bn
#adds a list to the dicts in bn to point to children
def add_child_pointers(bn):
    for var in bn:
        bn.get(var).update({'children': []})

    for var in bn:
        for p in bn.get(var).get('parents'):
            p = str(p)
            bn.get(p).get('children').append(var)

    return bn
            
            


#input bn, return list of ints with topological order for the bn
def get_topological_order(bn):
    order = []
    vars = list(bn.keys())

    while(len(order) < len(vars)):
        for v in vars: 
            pars = bn.get(v).get('parents')
            if(set(pars).issubset(set(order))):
                if(not int(v) in order):
                    order.append(int(v))
        
    return order


if __name__ == '__main__': 

    filename = 'C:\\Users\\white\\Documents\\fall2021\\classes\\adv_ai\\project1\\polytree10.json'
    qv = '5'
    samples = 100
    E = {}

    p = 0.95

    with open(filename) as f:
        bn = json.load(f)


    W = likelihood_weighting(qv, bn, samples, E)
    zeroes = (W[0])
    ones = (W[1])
    normed_l = [zeroes/(zeroes+ones), ones/(zeroes+ones)]
    print('likelihood: ',W, normed_l)

    C, x = gibbs_sampling(qv, bn, samples)
    normed_g = [C[0]/(C[0]+C[1]), C[1]/(C[0]+C[1])]
    print('gibbs', C, normed_g)

    C = metropolis_hastings(p, qv, bn, samples)
    normed_m = [C[0]/(C[0]+C[1]), C[1]/(C[0]+C[1])]
    print('metro', C, normed_m)