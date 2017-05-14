from collections import defaultdict
from viterbi import Viterbi
import sys
import time
import fileinput
import heapq

import numpy as np


def read_file(file_name):
    data =[]
    fp=open(file_name)
    for line in fp.readlines():
        if line!='\n':
            data+=[line.split('\n')[0]]

    return data


def get_prob(data,Noise=False,three=False,noise_data={}):

    if three:
        data_dict = defaultdict(lambda : defaultdict(list))#defaultdict(lambda : defaultdict(lambda : defaultdict(float)))
    else:
        data_dict = defaultdict(lambda :defaultdict(float))

    if Noise:
        input_unique_words = set()
        #input_unique_words = []
        output_unique_words = set()
    else:
        input_unique_words = set()
        output_unique_words =[ None ]

    for i in range(len(data)):
        if Noise:
            temp_list = data[i].split(':')
            input = temp_list[0]
            output = temp_list[1].split('#')[0].strip()
            prob = float(temp_list[1].split('#')[-1])
            input = input.strip()

            data_dict[input][output] = prob


            output_unique_words.add(output)
            for temp in input.split(' ')[:-1]:
                input_unique_words.add(temp)
        else:

            temp_list = data[i].split(':')
            input = temp_list[0]
            output = temp_list[1].split('#')[0].strip()
            prob = float(temp_list[1].split('#')[-1])
            input_tuple = tuple(input.split(' ')[:-1])
            u=input_tuple[0]
            v=input_tuple[1]

            if three:
                # if u not in input_unique_words:
                #     input_unique_words+=[u]
                # if output not in input_unique_words:
                #     input_unique_words+=[output]
                # if v not in input_unique_words:
                #     input_unique_words+=[v]
                #Previously storing
                #data_dict[output][v][u] = prob
                data_dict[output][v]+= [(prob,u)] #k,k-1,k-2

                # for x in noise_data[v]:
                #     n1=len(x.split(' '))
                #     data_dict[output][v][n1]+=[(prob*noise_data[v][x],u,x,n1)]


            else:
                data_dict[input_tuple][output] = prob

            input_unique_words.add(output)
            input_unique_words.add(u)
            input_unique_words.add(v)

            # for temp in input.split(' ')[:-1]:
            #     input_unique_words.add(temp)

    if three:
        for key in data_dict:
            for key1 in data_dict[key]:
                data_dict[key][key1]=sorted(data_dict[key][key1],key=lambda tup:tup[0],reverse=True)



    return data_dict,[list(input_unique_words),list(output_unique_words)]






def farword_bottom_top(p_noise_channel,p_prior,u_prior,u_i_noise,u_o_noise,letter_list,start_tag,end_tag,markov_order,letter):
    s1 = time.clock()
    best = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    best[-1]['<s>']['<s>'] = 1.0
    x_dict = defaultdict(list)

    print(letter_list)

    for i in range(len(letter_list)+1):
        x_dict ={}
        for v in p_prior:
            for u in p_prior[v]:
                if i not in x_dict and i!=len(letter_list):

                    if i >= 2:
                        x_dict[i] = [(3, letter_list[i - 2] + ' ' + letter_list[i - 1] + ' ' + letter_list[i]),
                                     (2, letter_list[i - 1] + ' ' + letter_list[i]), (1, letter_list[i])]
                    if i == 1:
                        x_dict[i] = [(2, letter_list[i- 1] + ' ' + letter_list[i]), (1, letter_list[i])]
                    if i == 0:
                        x_dict[i] = [(1, letter_list[i])]
                    x_list = x_dict[i]
                else:
                    if i!=len(letter_list):
                        x_list = x_dict[i]

                if i == len(letter_list):
                    best[i][u][v] = max(best[i-1][t][u]*p for (p,t) in p_prior[v][u])
                #(prob*noise_data[v][x],u,x,n1)
                else:
                     best[i][u][v]=max(best[i - n1][t][u] * p * p_noise_channel[v][x]
                for (p,t) in p_prior[v][u][:20] for (n1,x) in x_list)
                # max_temp=float('-inf')
                # for n1 in p_prior[v][u]:
                #     for (p, t, x, n2) in p_prior[v][u][n1][:1]:
                #         print(v,u,n1)
                #         if i-n2>=-1:
                #             temp=best[i - n2][t][u] * p
                #             if temp>max_temp:
                #                 max_temp=temp
                # best[i][u][v] = max_temp


                # best[i][u][v]=max(best[i - n2][t][u] *p for n1 in p_prior[v][u] for (p,t,x,n2) in p_prior[v][u][n1])


    max_val = max([best[i][u]['</s>'] for u in p_prior['</s>']])
    s2 = time.clock()
    print('Forward Tracking', s2 - s1)
    # back_result = backward_new(best_path,letter_list)
    # print('Back tracking', time.clock() - s2)
    # , back_result
    return max_val











def forward_bottom_top_kbest(p_noise_channel,p_prior,u_prior,u_i_noise,u_o_noise,letter_list,start_tag,end_tag,markov_order,letter,k_best=1):
    s1 = time.clock()
    best = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda : [0]*k_best)))
    best[-1]['<s>']['<s>'] = [1]*k_best


    '''
    This function takes best[.][.]=[list-->length k_best],i (the previous pointer), u(k-1),v(k),p_prior is the transition probability matrix 
    '''

    def pop_heapq(best, j, u, v, p_prior):

        max_num = float('-inf')
        for (p,t) in p_prior[v][u]:
            #print j,t,u,best[j][t][u]
            if best[j][t][u]!=[]:
                temp_num = best[j][t][u][0]

                if temp_num > max_num:
                    max_num = temp_num
                    max_t = t
                    max_p = p
        if max_t!='<s>' and u=='<s>':
            best[j][max_t][u] = best[j][max_t][u][1:]

        return max_num,t,p

    for i in range(len(letter_list)):
        x = letter_list[i]
        for v in p_prior:
            for u in p_prior[v]:
                temp_arr = []
                for o in range(k_best):
                    val,t,p=pop_heapq(best, i - 1, u, v,p_prior)
                    temp_arr+=[ val*p*p_noise_channel[v][x] ]

            best[i][u][v] = sorted(temp_arr,reverse=True)

    return best



def backward_new(best_path,letter_list):
    leng=len(letter_list)
    max_str = []
    while True:
        if leng==len(letter_list):
            key=list(best_path[leng].keys())[0]
            max_str+=[key[1],key[0]]
            leng-=1
        else:

            letter = best_path[leng][key][0]
            leng =best_path[leng][key][1]
            if letter == '<s>':
                break
            max_str+=[letter]
            key = (letter,key[0])





    return ' '.join(max_str[::-1])








#def __init__(self,p_noise_channel,p_prior,u_prior,u_i_noise,u_o_noise,word_list, start_tag='<s>', end_tag='<\s>',markov_order=2):
if __name__=='__main__':

    arguments = sys.argv




    file_name = 'epron.probs'
    file_name1 = 'epron-jpron.probs'
    start_tag = '<s>'
    end_tag = '</s>'
    markov_order = 2
    letter = 'P I'
    letter_list = letter.split()
    #sys.argv


    s1 = time.clock()
    ######


    data  = read_file(file_name1)
    p_noise_channel, unique_words = get_prob(data,Noise=True)
    u_i_noise,u_o_noise=unique_words[0], unique_words[1]
    ####

    epron_data = read_file(file_name)
    p_prior,unique_words = get_prob(epron_data,three=True,noise_data=p_noise_channel)
    #print(p_prior)
    if unique_words[1]==[None]:
        u_prior = unique_words[0]

    print('Time to read the files :',time.clock()-s1)

    # a = farword_bottom_top(p_noise_channel, p_prior, u_prior, u_i_noise, u_o_noise, letter_list, start_tag, end_tag,
    #                       markov_order, letter)

    a = forward_bottom_top_kbest(p_noise_channel, p_prior, u_prior, u_i_noise, u_o_noise, letter_list, start_tag, end_tag,
                          markov_order, letter,k_best=6)

    print(a)

    # for input in fileinput.input():
    #     print('#####')
    #     letter = input.split('\n')[0]
    #     letter_list=letter.split()
    #     #v=Viterbi(p_noise_channel,p_prior,u_prior,u_i_noise,u_o_noise,letter_list,start_tag,end_tag,markov_order)
    #     s1 = time.clock()
    #     #print(p_noise_channel)
    #     a=farword_bottom_top(p_noise_channel,p_prior,u_prior,u_i_noise,u_o_noise,letter_list,start_tag,end_tag,markov_order,letter)
    #     print(a)
    #     print('Running the algorithms:',time.clock()-s1)


































































































































# def forward_new_v1(p_noise_channel, p_prior, u_prior, u_i_noise, u_o_noise, letter_list, start_tag, end_tag,
#                    markov_order):
#     '''
#     best : stores the best probability till now.  it takes length of the sentence completed, and for a (index,w1,w2)
#     :return:
#     '''
#     ##### Intialization for the probabilities
#     s1 = time.clock()
#     # Stores the prob.
#     best = defaultdict(float)
#     # start_gram = tuple([start_tag for i in range(markov_order)])
#     # print(start_gram)
#     # Initialization for <s> and <s> tag
#     best[(-1, '<s>', '<s>')] = 1.0
#     #######Intialization for the best path
#     best_path = defaultdict(lambda: defaultdict(str))
#
#     ######
#
#
#     def find_best(n, best, u, v):
#         if n == -1 and (u, v) != (start_tag, start_tag):
#             return best[(n, u, v)]
#
#         if (n, u, v) in best:
#             return best[(n, u, v)]
#
#         x_list = []
#         if n >= 2:
#             x_list += [(3, letter_list[n - 2] + ' ' + letter_list[n - 1] + ' ' + letter_list[n])]
#             x_list += [(2, letter_list[n - 1] + ' ' + letter_list[n])]
#             x_list += [(1, letter_list[n])]
#         if n == 1:
#             x_list += [(2, letter_list[n - 1] + ' ' + letter_list[n])]
#             x_list += [(1, letter_list[n])]
#         if n == 0:
#             x_list += [(1, letter_list[n])]
#
#         max_str = None
#         max_num = float('-inf')
#         for i in range(len(u_prior)):
#             w = u_prior[i]
#             for (n1, x) in x_list:
#
#                 temp_num = find_best(n - n1, best, w, u) * p_prior[(w, u, v)] * p_noise_channel[(v, x)]
#                 if temp_num > max_num:
#                     max_num = temp_num
#                     max_str = w
#                     num = n - n1
#
#         best[(n, u, v)] = max_num
#         best_path[n][(u, v)] = (max_str, num)
#
#         return best[(n, u, v)]
#
#     ############################
#
#
#     max_num = float('-inf')
#     max_str = None
#     n = len(letter_list)
#     for i in range(len(u_prior)):
#         for j in range(len(u_prior)):
#             u = u_prior[i]
#             v = u_prior[j]
#
#             temp_num1 = find_best(n - 1, best, u, v)
#             temp_num2 = p_prior[(u, v, end_tag)]
#
#             temp_num = temp_num1 * temp_num2
#             if temp_num > max_num:
#                 max_num = temp_num
#                 max_str = (u, v)
#     best_path[len(letter_list)][max_str] = ('</s>', 1)
#     s2 = time.clock()
#     print('Forward Tracking', s2 - s1)
#     back_result = backward_new(best_path, letter_list)
#     print('Back tracking', time.clock() - s2)
#     return max_num, back_result





# def get_prob_v1(data,Noise=False):
#
#     data_dict = defaultdict(float)
#
#     if Noise:
#         input_unique_words = set()
#         output_unique_words = set()
#     else:
#         input_unique_words = set()
#         output_unique_words =[ None ]
#
#     for i in range(len(data)):
#         if Noise:
#             temp_list = data[i].split(':')
#             input = temp_list[0]
#             output = temp_list[1].split('#')[0].strip()
#             prob = float(temp_list[1].split('#')[-1])
#             input = input.strip()
#
#             data_dict[(input,output)] = prob
#
#
#             output_unique_words.add(output)
#             for temp in input.split(' ')[:-1]:
#                 input_unique_words.add(temp)
#         else:
#
#             temp_list = data[i].split(':')
#             input = temp_list[0]
#             output = temp_list[1].split('#')[0].strip()
#             prob = float(temp_list[1].split('#')[-1])
#             input_tuple = tuple(input.split(' ')[:-1]+[output])
#             data_dict[input_tuple] = prob
#
#             input_unique_words.add(output)
#             for temp in input.split(' ')[:-1]:
#                 input_unique_words.add(temp)
#
#
#
#
#     return data_dict,[list(input_unique_words),list(output_unique_words)]




#
# def forward_new(p_noise_channel,p_prior,u_prior,u_i_noise,u_o_noise,letter_list,start_tag,end_tag,markov_order,letter):
#     s1 = time.clock()
#     best = defaultdict(lambda :defaultdict(lambda : defaultdict(float)))
#     best[-1]['<s>']['<s>'] = 1.0
#     x_dict = defaultdict(list)
#
#     def find_best(n, best, u, v):
#
#         if n==-1 and (u,v)==('<s>','<s>'):
#             return best[-1]['<s>']['<s>']
#         if n==-1:
#             return 0
#         if n in best:
#             if u in best[n]:
#                 if v in best[n][u]:
#                     #print('I A  HERE')
#                     return best[n][u][v]
#         if n not in x_dict:
#             if n >= 2:
#                 x_dict[n] = [(3,letter_list[n - 2] + ' ' + letter_list[n - 1] + ' ' + letter_list[n]),(2,letter_list[n - 1] + ' ' + letter_list[n]),(1, letter_list[n])]
#             if n == 1:
#                 x_dict[n] = [(2,letter_list[n - 1] + ' ' + letter_list[n]),(1, letter_list[n]),]
#             if n == 0:
#                 x_dict[n]= [(1, letter_list[n])]
#             x_list = x_dict[n]
#         else:
#             x_list=x_dict[n]
#
#
#         max_str = None
#         max_num = float('-inf')
#         for w in sorted(p_prior[v][u],key=p_prior[v][u].get,reverse=True)[:20]:
#             for (n1,x) in x_list:
#                 #best[n-n1][w][u]=find_best(n - n1, best, w, u)
#                 temp_num = find_best(n - n1, best, w, u) * p_prior[v][u][w] * p_noise_channel[v][x]
#                 if temp_num > max_num:
#                     max_num = temp_num
#                     max_str = w
#                     #num = n-n1
#
#         best[n][u][v] = max_num
#         #best_path[n][(u,v)] = (max_str,num)
#
#         return best[n][u][v]
#
#     ############################
#
#
#
#
#
#
#
#
#     max_num = float('-inf')
#     max_str = None
#     n=len(letter_list)
#     temp_best=defaultdict(float)
#     for v in p_prior[end_tag]:
#         for u in sorted(p_prior[end_tag][v],key=p_prior[end_tag][v].get,reverse=True)[:3]:
#             if (u,v) not in temp_best:
#                 temp_best[(u,v)] = find_best(n-1, best, u, v) * p_prior[end_tag][v][u]
#
#             if temp_best[(u,v)]> max_num:
#                 max_num = temp_best[(u,v)]
#                 max_str = (u,v)
#
#
#
#
#
#
#
#     #best_path[len(letter_list)][max_str] = ('</s>',1)
#     s2 = time.clock()
#     print('Forward Tracking',s2-s1)
#     #back_result = backward_new(best_path,letter_list)
#     print('Back tracking',time.clock()-s2)
#     #, back_result
#     return max_num
#
#
#
# def farword_bottom_top_v1(p_noise_channel,p_prior,u_prior,u_i_noise,u_o_noise,letter_list,start_tag,end_tag,markov_order,letter):
#     s1 = time.clock()
#     best = np.zeros((len(letter_list)+2, len(u_prior),len(u_prior)))#defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
#     mapping = {u_prior[i]:i for i in range(len(u_prior))}
#     best[0][mapping['<s>']][mapping['<s>']] = 1.0
#     x_dict = defaultdict(list)
#
#     print(letter_list)
#
#     for i in range(1,len(letter_list)+1):
#         x_dict ={}
#         for v in p_prior:
#             for u in p_prior[v]:
#                 n=i-1
#                 #print(n,i)
#                 if n not in x_dict and n!=len(letter_list)+1:
#
#                     if n >= 2:
#                         x_dict[n] = [(3, letter_list[n - 2] + ' ' + letter_list[n - 1] + ' ' + letter_list[n]),
#                                      (2, letter_list[n - 1] + ' ' + letter_list[n]), (1, letter_list[n])]
#                     if n == 1:
#                         x_dict[n] = [(2, letter_list[n- 1] + ' ' + letter_list[n]), (1, letter_list[n])]
#                     if n == 0:
#                         x_dict[n] = [(1, letter_list[n])]
#                     x_list = x_dict[n]
#                 else:
#                     if i!=len(letter_list):
#                         x_list = x_dict[n]
#
#                 if i == len(letter_list)+1:
#
#                     best[i][mapping[u]][mapping[v]] = max(best[i-1][mapping[t]][mapping[u]]*p_prior[v][u][t] for t in p_prior[v][u])
#                 else:
#                     best[i][mapping[u]][mapping[v]]=max(best[i - n1][mapping[t]][mapping[u]] * p_prior[v][u][t] * p_noise_channel[v][x]
#                 for t in p_prior[v][u] for (n1,x) in x_list)
#
#     max_val = max([best[i][mapping[v]][mapping['</s>']] for v in p_prior['</s>']])
#     s2 = time.clock()
#     print('Forward Tracking', s2 - s1)
#     # back_result = backward_new(best_path,letter_list)
#     print('Back tracking', time.clock() - s2)
#     # , back_result
#     return max_val
#
