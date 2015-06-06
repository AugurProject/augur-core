data cluster_node[](left, right, vec[], id, distance)
data distances[]
data lenCluster
data i
data j
data numEvents
data distances[][]

def sqrt(n):
    approx = n/2.0
    better = (approx + n/approx)/2.0
    i = 0
    while i < 11:
        approx = better
        better = (approx + n/approx)/2.0
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

    # initial clusters are the rows (individually)
    i = 0
    while i < (len(features)/numEvents):
        cluster_node[i].id = i
        n = 0
        z = i*numEvents
        while n < numEvents:
            cluster_node[i].vec[n] = features[z]
            n += 1
            z += 1
        i += 1
    lenCluster = len(features)/numEvents

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

        self.cluster_node[lenCluster].id = currentclustid
        self.cluster_node[lenCluster].distance = closest
        save(self.cluster_node[lenCluster].vec[0], mergevec, chars=32*numEvents)
        self.cluster_node[lenCluster].left = i
        self.cluster_node[lenCluster].right = j
        lenCluster += 1

        currentclustid -= 1





# loop through every pair looking for the smallest distance
    # bug if dist is 0