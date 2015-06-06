data cluster_node[](left, right, vec[], id, distance)
data lenCluster
data i
data j
data numEvents
data distances[][]
data cluster_elements[]
data elementsLen
data extracted_clusters[]
data extractionLen

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
		distSquare += (self.cluster_node[x].vec[i] - self.cluster_node[y].vec[i])^2
		i += 1
	return(self.sqrt(distSquare))

def cluster(features: arr):
    # cluster that matrix
    currentclustid = -1
    numEvents = self.numEvents

    # initial clusters are the rows (individually) (will have pos. id)
    i = 0
    while i < (len(features)/numEvents):
        self.cluster_node[i].id = i
        n = 0
        z = i*numEvents
        while n < numEvents:
            self.cluster_node[i].vec[n] = features[z]
            n += 1
            z += 1
        i += 1
    self.lenCluster = len(features)/numEvents
    lenCluster = self.lenCluster
    while lenCluster > 1:
        i = 0
        j = 1
        closest = self.euclidDist(0, 1)

        # find the smallest dist.
        l = 0
        while l < lenCluster:
            m = l + 1
            while m < lenCluster:
                if(self.distances[self.cluster_node[i].id][self.cluster_node[j].id] == 0):
                    self.distances[self.cluster_node[i].id][self.cluster_node[j].id] = self.euclidDist(i,j)

                d = self.distances[self.cluster_node[i].id][self.cluster_node[j].id]
                if d < closest:
                    closest = d
                    i = l
                    j = m
                m += 1
            l += 1

        # find the average of the two clusters
        o = 0
        mergevec = array(numEvents)
        while o < numEvents:
            mergevec[o] = (self.cluster_node[i].vec[o] + self.cluster_node[j].vec[o]) / 2
            o += 1

        self.cluster_node[self.lenCluster].id = currentclustid
        self.cluster_node[self.lenCluster].distance = closest
        save(self.cluster_node[self.lenCluster].vec[0], mergevec, chars=32*numEvents)
        self.cluster_node[self.lenCluster].left = i
        self.cluster_node[self.lenCluster].right = j
        lenCluster -= 1
        # del i and j
        # del clust[lowestpair[1]]
        # del clust[lowestpair[0]]
        self.lenCluster += 1
        currentclustid -= 1
    return(1)

def extract_clusters(nodeIndex, dist):
    if self.cluster_node[nodeIndex].distance < dist:
        self.extracted_clusters[self.extractionLen] = nodeIndex
        extractionLen += 1
    else:
        if(self.cluster_node[nodeIndex].left!=0):
            self.extract_clusters(self.cluster_node[nodeIndex].left, dist)
        if(self.cluster_node[nodeIndex].right!=0):
            self.extract_clusters(self.cluster_node[nodeIndex].right, dist)
    return(1)


def get_cluster_elements(nodeIndex):
    id = self.cluster_node[nodeIndex].id 
    if id >= 0:
        self.cluster_elements[self.elementsLen] = id
        elementsLen += 1
    else:
        if(self.cluster_node[nodeIndex].left!=0):
            self.get_cluster_elements(self.cluster_node[nodeIndex].left)
        if(self.cluster_node[nodeIndex].right!=0):
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

def get_cluster_node_vec(nodeIndex):
    return(self.cluster_node[nodeIndex].vec[nodeIndex])

def set_numEvents(num):
    self.numEvents = num

# loop through every pair looking for the smallest distance
    # bug if dist is 0
    # if cluster.left or right is 0 there's a bug, b/c check is if none not if 0