from approximate_inference import *
#from exact_inference_main.exact_inference_main.exact_inference import *
import time
import statistics



metro_p = [0.75, 0.85, 0.95]

#QV: downstream vs upstream







qv = '3'
samples = 1000
E = {'1':0}
p = 0.95

bayes_nets = ['polytree10']#, 'polytree15']
approximation_methods = ['metropolis', 'likelihood', 'gibbs']

num_tests = 10

stats = {}
for bn_type in bayes_nets:
    for app_meth in approximation_methods:
        stats.update({bn_type + app_meth: [[], []]})

for i in range(num_tests):
    print(i)
    for bn_type in bayes_nets:

        with open('C:\\Users\\white\\Documents\\fall2021\\classes\\adv_ai\\project1\\' + bn_type + '.json') as f: 
            bn = json.load(f)

        for app_meth in approximation_methods:

            starttime = time.perf_counter()
            if(app_meth == 'likelihood'):
                C = likelihood_weighting(qv, bn, samples, E)
            elif(app_meth == 'gibbs'):
                C, x = gibbs_sampling(qv, bn, samples, {}, E)
            elif(app_meth == 'metropolis'):
                C = metropolis_hastings(p, qv, bn, samples, E)
            else: 
                print('err4021')
                exit()
            endtime = time.perf_counter()


            normed = [C[0]/(C[0]+C[1]), C[1]/(C[0]+C[1])]
            stats.get(bn_type+app_meth)[0].append(endtime-starttime)
            stats.get(bn_type + app_meth)[1].append(normed[1])
            
            #print(app_meth, bn_type, normed, endtime - starttime)

for bn_type in bayes_nets:
    for app_meth in approximation_methods:
        stats.get(bn_type + app_meth)[0] = [statistics.mean(stats.get(bn_type + app_meth)[0]), statistics.stdev(stats.get(bn_type + app_meth)[0])]
        stats.get(bn_type + app_meth)[1] = [statistics.mean(stats.get(bn_type + app_meth)[1]), statistics.stdev(stats.get(bn_type + app_meth)[1])]

print(stats)

# with open('C:\\Users\\white\\Documents\\fall2021\\classes\\adv_ai\\project1\\polytree10.json') as f: 
#     bn = json.load(f)
# metro_p_times = {
#     '0.95':[0, 0],
#     '0.85':[0,0], 
#     '0.75':[0,0], 

# }
# for i in range(10):
#     for p in [0.95, 0.85, 0.75]:
#         starttime = time.perf_counter()
#         C = metropolis_hastings(p, qv, bn, samples, E)
#         endtime = time.perf_counter()
#         normed = [C[0]/(C[0]+C[1]), C[1]/(C[0]+C[1])]

#         metro_p_times.get(str(p))[0] += endtime - starttime
#         metro_p_times.get(str(p))[1] += normed[1] / 10

# print(metro_p_times)










# a = time.perf_counter()

# for i in range(12):
#     print('hey')
# b=time.perf_counter()
# print(b-a)