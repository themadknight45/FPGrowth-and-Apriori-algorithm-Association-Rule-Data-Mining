import itertools
import time

#take input of file name and minimum support count
print("Enter the filename:")
filename = input()
print("Enter the minimum support count:")
minimum_sup = int(input())

#read data from txt file
with open(filename) as f:
    text = f.readlines()

text = [x.strip() for x in text]

Trans = []                  #to store Transactions
Freq_item_val = {}         #to store all frequent item sets

#to fill values in Trans from txt file
for ch in text:
    Trans.append(ch.split())

#function to get frequent one itemset
def frequent_one_item(Trans,minimum_sup):
    cand1 = {}

    for i in range(0,len(Trans)):
        for j in range(0,len(Trans[i])):
            if Trans[i][j] not in cand1:
                cand1[Trans[i][j]] = 1
            else:
                cand1[Trans[i][j]] += 1

    frequentitem1 = []                      #to get frequent 1 itemsets with minimum support count
    for value in cand1:
        if cand1[value] >= minimum_sup:
            frequentitem1 = frequentitem1 + [[value]]
            Freq_item_val[tuple(value)] = cand1[value]

    return frequentitem1
print("frequent one items are :")
values = frequent_one_item(Trans,minimum_sup)
print(*values, sep = "\n")


# to remove infrequent 1 itemsets from Trans
Trans1 = []
for i in range(0,len(Trans)):
    list_val = []
    for j in range(0,len(Trans[i])):
        if [Trans[i][j]] in values:
            list_val.append(Trans[i][j])
    Trans1.append(list_val)


#class of Hash node
class Hash_node:
    def __init__(own):
        own.children = {}           #pointer to its children
        own.Leaf_status = True      #to know the status whether current node is leaf or not
        own.bucket = {}             #contains itemsets in bucket

#class of constructing and getting hashtree
class HashTree:
    # class constructor
    def __init__(own, max_leaf_count, max_child_count):
        own.root = Hash_node()
        own.max_leaf_count = max_leaf_count
        own.max_child_count = max_child_count
        own.frequent_itemsets = []

    # function to recursive insertion to make hashtree
    def recursively_insert(own, node, itemset, ind, count):
        if ind == len(itemset):
            if itemset in node.bucket:
                node.bucket[itemset] += count
            else:
                node.bucket[itemset] = count
            return

        if node.Leaf_status:                             #if node is leaf
            if itemset in node.bucket:
                node.bucket[itemset] += count
            else:
                node.bucket[itemset] = count
            if len(node.bucket) == own.max_leaf_count:  #if bucket capacity increases
                for old_itemset, old_count in node.bucket.items():

                    hash_key = own.hash_function(old_itemset[ind])  #do hashing on next ind
                    if hash_key not in node.children:
                        node.children[hash_key] = Hash_node()
                    own.recursively_insert(node.children[hash_key], old_itemset, ind + 1, old_count)
                #since no more requirement of this bucket
                del node.bucket
                node.Leaf_status = False
        else:                                            #if node is not leaf
            hash_key = own.hash_function(itemset[ind])
            if hash_key not in node.children:
                node.children[hash_key] = Hash_node()
            own.recursively_insert(node.children[hash_key], itemset, ind + 1, count)

    def insert(own, itemset):
        itemset = tuple(itemset)
        own.recursively_insert(own.root, itemset, 0, 0)

    # to add support to candidate itemsets. Transverse the Tree and find the bucket in which this itemset is present.
    def add_support(own, itemset):
        Transverse_HNode = own.root
        itemset = tuple(itemset)
        ind = 0
        while True:
            if Transverse_HNode.Leaf_status:
                if itemset in Transverse_HNode.bucket:    #found the itemset in this bucket
                    Transverse_HNode.bucket[itemset] += 1 #increment the count of this itemset.
                break
            hash_key = own.hash_function(itemset[ind])
            if hash_key in Transverse_HNode.children:
                Transverse_HNode = Transverse_HNode.children[hash_key]
            else:
                break
            ind += 1

    # to transverse the hashtree to get frequent itemsets with minimum support count
    def get_frequent_itemsets(own, node, support_count,frequent_itemsets):
        if node.Leaf_status:
            for key, value in node.bucket.items():
                if value >= support_count:                       #if it satisfies the condition
                    frequent_itemsets.append(list(key))          #then add it to frequent itemsets.
                    Freq_item_val[key] = value
            return

        for child in node.children.values():
            own.get_frequent_itemsets(child, support_count,frequent_itemsets)

    # hash function for making HashTree
    def hash_function(own, val):
        return int(val) % own.max_child_count

#To generate hash tree from candidate itemsets
def generate_hash_tree(candidate_itemsets, max_leaf_count, max_child_count):
    htree = HashTree(max_child_count, max_leaf_count)             #create instance of HashTree
    for itemset in candidate_itemsets:
        htree.insert(itemset)                                     #to insert itemset into Hashtree
    return htree

#to generate subsets of itemsets of size k
def generate_k_subsets(dataset, length):
    subsets = []
    for itemset in dataset:
        subsets.extend(map(list, itertools.combinations(itemset, length)))
    return subsets

def subset_generation(ck_data,l):
    return map(list,set(itertools.combinations(ck_data,l)))

#apriori generate function to generate ck
def apriori_generate(dataset,k):
    ck = []
    #join step
    lenlk = len(dataset)
    for i in range(lenlk):
        for j in range(i+1,lenlk):
            L1 = list(dataset[i])[:k - 2]
            L2 = list(dataset[j])[:k - 2]
            if L1 == L2:
                ck.append(sorted(list(set(dataset[i]) | set(dataset[j]))))

    #prune step
    f_ck = []
    for candidate in ck:
        all_subsets = list(subset_generation(set(candidate), k - 1))
        found = True
        for i in range(len(all_subsets)):
            value = list(sorted(all_subsets[i]))
            if value not in dataset:
                found = False
        if found == True:
            f_ck.append(candidate)

    return ck,f_ck

def generateL(ck,minimum_sup):
    support_ck = {}
    for val in Trans1:
        for val1 in ck:
            value = set(val)
            value1 = set(val1)

            if value1.issubset(value):
                if tuple(val1) not in support_ck:
                    support_ck[tuple(val1)] = 1
                else:
                    support_ck[tuple(val1)] += 1
    frequent_item = []
    for item_set in support_ck:
        if support_ck[item_set] >= minimum_sup:
            frequent_item.append(sorted(list(item_set)))
            Freq_item_val[item_set] = support_ck[item_set]

    return frequent_item

# main apriori algorithm function
def apriori(L1,minimum_sup):
    L = []
    L.append(0)
    L.append(L1)
    k = 2;
    print("enter max_leaf_count")              #maximum number of items in bucket i.e. bucket capacity of each node
    max_leaf_count = int(input())
    print("enter max_child_count")             #maximum number of child you want for a node
    max_child_count = int(input())

    start = time.time()
    while(len(L[k-1])>0):
        ck,f_ck = apriori_generate(L[k-1],k)                 #to generate candidate itemsets
        print("C%d" %(k))
        print(*f_ck, sep = "\n")
        h_tree = generate_hash_tree(ck,max_leaf_count,max_child_count)       #to generate hashtree
        if (k > 2):
            while(len(L[k-1])>0):
                l = generateL(f_ck, minimum_sup)
                L.append(l)
                print("Frequent %d item" % (k))
                print(l)
                k = k + 1
                ck, f_ck = apriori_generate(L[k - 1], k)
                print("C%d" % (k))
                print(*f_ck, sep = "\n")
            break
        k_subsets = generate_k_subsets(Trans1,k)                  #to generate subsets of each Trans
        for subset in k_subsets:
            h_tree.add_support(subset)                                  #to add support count to itemsets in hashtree
        lk = []
        h_tree.get_frequent_itemsets(h_tree.root,minimum_sup,lk)                  #to get frequent itemsets
        print("Frequent %d item" %(k))
        print(*lk,sep = "\n")
        L.append(lk)
        k = k + 1
    end = time.time()
    return L,(end-start)


L_value,time_taken = apriori(values,minimum_sup)
print("Total time taken:")
print(time_taken)
print("All frequent itemsets with their support count:")
print(Freq_item_val)
