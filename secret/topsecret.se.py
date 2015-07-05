data clust[](cluster_tree[](vec[], id, distance, vectorLen))
data lenCluster

data i
data j

data numEvents

data distances[][]

data cluster_elements[]
data elementsLen

data extracted_clusters[]
data extractionLen

# root is 0
# left child is 2i+1
# right child is 2i+2

# -1 == none

def sqrt(n):
    approx = n/2
    better = (approx + n/approx)/2
    i = 0
    while i < 11:
        approx = better
        better = (approx + n/approx)/2
        i += 1
    return approx

def euclidDist(x, y):
    i = 0
    distSquare = 0
    while i < self.numEvents:
        distSquare += (self.clust[x].cluster_tree[0].vec[i] - self.clust[y].cluster_tree[0].vec[i])^2
        i += 1
    return(self.sqrt(distSquare))

def cluster(features: arr):
    # cluster that matrix
    currentclustid = -1
    numEvents = self.numEvents

    # initial clusters are the rows (individually) (will have pos. id)
    i = 0
    while i < (len(features)/numEvents):
        self.clust[i].cluster_tree[0].id = i + 1
        n = 0
        z = i*numEvents
        while n < numEvents:
            self.clust[i].cluster_tree[0].vec[n] = features[z]
            n += 1
            z += 1
        self.clust[i].cluster_tree[0].vectorLen = numEvents
        self.clust[i].cluster_tree[1].left = -1
        self.clust[i].cluster_tree[2].right = -1
        i += 1

    self.lenCluster = len(features)/numEvents
    
    while self.lenCluster > 1:
        i = 0
        j = 1
        closest = self.euclidDist(0, 1)

        # find the smallest dist.
        l = 0
        while l < self.lenCluster:
            m = l + 1
            while m < self.lenCluster:
                if(self.distances[self.clust[l].cluster_tree[0].id][self.clust[m].cluster_tree[0].id] == 0):
                    dist = self.euclidDist(l,m)
                    if(dist!=0):
                        self.distances[self.clust[l].cluster_tree[0].id][self.clust[m].cluster_tree[0].id] = dist

                d = self.distances[self.clust[l].cluster_tree[0].id][self.clust[m].cluster_tree[0].id]
                
                if d < closest:
                    closest = d
                    i = l
                    j = m
                m += 1
            l += 1

        # or broken due to closest / i and j
        # find the average of the two clusters
        o = 0
        length = self.clust[0].cluster_tree[0].vectorLen
        mergevec = array(length)
        while o < length:
            mergevec[o] = (self.clust[i].cluster_tree[0].vec[o] + self.clust[j].cluster_tree[0].vec[o])/2
            o += 1

        currentclustid -= 1
        leftNode = array(length + 3)
        rightNode = array(length + 3)
        q = 0
        while q < length:
            leftNode[q] = self.clust[i].cluster_tree[0].vec[q]
            rightNode[q] = self.clust[j].cluster_tree[0].vec[q]
            q += 1
        leftNode[q] = self.clust[i].cluster_tree[0].id
        leftNode[q+1] = self.clust[i].cluster_tree[0].distance
        leftNode[q+2] = self.clust[i].cluster_tree[0].vectorLen
        rightNode[q] = self.clust[j].cluster_tree[0].id
        rightNode[q+1] = self.clust[j].cluster_tree[0].distance
        rightNode[q+2] = self.clust[j].cluster_tree[0].vectorLen
        del(j)
        del(i)

        # make new cluster and append
        self.clust[self.lenCluster].cluster_tree[0].id = currentclustid
        self.clust[self.lenCluster].cluster_tree[0].distance = closest
        save(self.clust[self.lenCluster].cluster_tree[0].vec[0], mergevec, chars=32*length)
        self.clust[self.lenCluster].cluster_tree[0].vectorLen = length
        # left child is 2i+1
        # right child is 2i+2
        self.clust[self.lenCluster].cluster_tree[1].id = leftNode[q]
        self.clust[self.lenCluster].cluster_tree[2].id = rightNode[q]
        self.clust[self.lenCluster].cluster_tree[1].distance = leftNode[q+1]
        self.clust[self.lenCluster].cluster_tree[2].distance = rightNode[q+1]
        self.clust[self.lenCluster].cluster_tree[1].vectorLen = leftNode[q+2]
        self.clust[self.lenCluster].cluster_tree[2].vectorLen = rightNode[q+2]
        z = 0
        while z < length:
            self.clust[self.lenCluster].cluster_tree[1].vec[z] = leftNode[z]
            self.clust[self.lenCluster].cluster_tree[2].vec[z] = rightNode[z]
            z+=1            

    return(1)

def delete(array:arr, index):
    i = index
    while i < len(array):
       array[i] = array[i+1]
       i += 1
    return(array:arr)

# needs fixing
macro del(index):
    i = index
    data clust[](cluster_tree[](vec[], id, distance, vectorLen))

    while i < self.lenCluster:
        self.clust[i].cluster_tree[0].id = self.clust[i+1].cluster_tree[0].id
        self.clust[i].cluster_tree[0].distance = self.clust[i+1].cluster_tree[0].distance
        self.clust[i].cluster_tree[0].vectorLen = self.clust[i+1].cluster_tree[0].vectorLen
        vecArr = array(self.clust[i+1].cluster_tree[0].vectorLen)
        vecArr = load(self.clust[i+1].cluster_tree[0].vec[0], chars=32*self.clust[i+1].cluster_tree[0].vectorLen)
        save(self.clust[i].cluster_tree[0].vec[0], vecArr, chars=32*self.clust[i+1].cluster_tree[0].vectorLen)
        
        # this moves root, but what about children and children's children
        # root is 0
        # left child is 2i+1
        # right child is 2i+2


        i += 1

    self.lenCluster -= 1
    $1

def extract_clusters(nodeIndex, dist):
    if self.cluster_node[nodeIndex].distance < dist:
        self.extracted_clusters[self.extractionLen] = nodeIndex
        extractionLen += 1
    else:
        if(self.cluster_node[nodeIndex].left!=-1):
            self.extract_clusters(self.cluster_node[nodeIndex].left, dist)
        if(self.cluster_node[nodeIndex].right!=-1):
            self.extract_clusters(self.cluster_node[nodeIndex].right, dist)
    return(1)


def get_cluster_elements(nodeIndex):
    id = self.cluster_node[nodeIndex].id 
    if id >= 0:
        self.cluster_elements[self.elementsLen] = id
        elementsLen += 1
    else:
        if(self.cluster_node[nodeIndex].left!=-1):
            self.get_cluster_elements(self.cluster_node[nodeIndex].left)
        if(self.cluster_node[nodeIndex].right!=-1):
            self.get_cluster_elements(self.cluster_node[nodeIndex].right)
    return(1)

def get_extractionLen():
    return(self.extractionLen)

def get_elementsLen():
    return(self.elementsLen)

def get_numEvents():
    return(self.numEvents)

def get_i():
    return(self.i)

def get_j():
    return(self.j)

def get_lenCluster():
    return(self.lenCluster)

def get_extracted_clusters(x):
    return(self.extracted_clusters[x])

def get_cluster_elementss(x):
    return(self.cluster_elements[x])

def get_distances(x,y):
    return(self.distances[x][y])

def get_cluster_node_left(nodeIndex):
    return(self.cluster_node[nodeIndex].left)

def get_cluster_node_right(nodeIndex):
    return(self.cluster_node[nodeIndex].right)

def get_cluster_node_id(nodeIndex):
    return(self.cluster_node[nodeIndex].id)

def get_cluster_node_distance(nodeIndex):
    return(self.cluster_node[nodeIndex].distance)

def get_cluster_node_vec(nodeIndex, vecIndex):
    return(self.cluster_node[nodeIndex].vec[vecIndex])

def set_numEvents(num):
    self.numEvents = num

# what if the 0 cluster is an extracted cluster?