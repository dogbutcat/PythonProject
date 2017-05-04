import multiprocessing
from thread_crawler import thread_crawler

def process_link_crawler(args,**kwargs):
    num_cpus = multiprocessing.cpu_count()
    print 'Start {} processess'.format(num_cpus)
    processes=[]
    for i in range(num_cpus):
        p = multiprocessing.Process(target=thread_crawler,args=[args],kwargs=kwargs)
        p.start()
        processes.append(p)
    for p in processes:
        p.join()
