contract Consensus {
	struct cluster_node {
		// left leaf is 0, right leaf is 1
		mapping (uint => cluster_node) leafs;
		int id;
		int distance;
		uint vecLen;
		mapping (uint => uint) vec;
	}

	mapping (uint => cluster_node) clust;

	uint lenClust;

	uint numEvents;

	cluster_node temp;

	mapping (uint => cluster_node) extractedClust;

	uint extractedClustLen;

	mapping (uint => int) cluster_element;

	uint numElements;

	uint j;
	uint l;
	uint m;
	int closest;
	int dist;
	int d;
	uint o;
	uint length;
	mapping (int => mapping(int => int)) distances;
	uint[] mergevec;

	function setNumEvents(uint num) returns(uint success) {
		numEvents = num;
		return(1);
	}

	function sqrt(int n) returns(int answer) {
		int approx = n/2;
		int better = (approx + n/approx)/2;
		int i = 0;
		while(i < 11) {
			approx = better;
			better = (approx = n/approx)/2;
			i += 1;
		}
		return approx;
	}

	function L2dist(uint v1, uint v2) returns(int squareDist) {
		uint i = 0;
		int distSquare = 0;
		while(i < numEvents) {
        	distSquare += (int(clust[v1].vec[i]) - int(clust[v2].vec[i]))^2;
        	i += 1;
        }
    	return(sqrt(distSquare));
	}

	function hcluster(uint[] features) external returns(int clusterstruct){
		int currentclustid = -1;

    	uint i = 0;
    	while(i < (features.length/numEvents)) {
    		clust[i].id = int(i);
    		uint n = 0;
    		uint z = i*numEvents;
    		while(n < numEvents) {
    			clust[i].vec[n] = features[z];
    			n += 1;
    			z += 1;
    		}
    		clust[i].vecLen = numEvents;
    		cluster_node leaf;
    		leaf.id = -1;
    		clust[i].leafs[0] = leaf;
    		clust[i].leafs[1] = leaf;
    		i += 1;
    	}

    	while(lenClust > 1) {
    		i = 0;
    		j = 1;
    		closest = L2dist(0,1);

    		l = 0;
    		while(l < lenClust) {
    			m = l + 1;
    			while(m < lenClust) {
    				if(distances[clust[l].id][clust[m].id] == 0) {
    					dist = L2dist(l,m);
    					if(dist!=0) {
    						distances[clust[l].id][clust[m].id] = L2dist(l,m);
    					}
    				}

    				d = distances[clust[l].id][clust[m].id];

    				if(d < closest) {
    					closest = d;
    					i = l;
    					j = m;
    				}
    				m += 1;
    			}
    			l += 1;
    		}

	        o = 0;
	        cluster_node zero = clust[0];
    	    length = zero.vecLen;
        	while(o < length) {
        		mergevec[o] = (clust[i].vec[o] + clust[j].vec[o])/2;
        		o += 1;
        	}
        	cluster_node cluster;
        	cluster.leafs[0] = clust[i];
        	cluster.leafs[1] = clust[j];
        	cluster.distance = closest;
        	cluster.id = currentclustid;
        	o = 0;
        	while(o < length) {
        		cluster.vec[o] = mergevec[o];
        		o += 1;
        	}

        	currentclustid-=1;
        	del(j);
        	del(i);
        	clust[lenClust] = cluster;

    	}
    	return clust[0].id;
    }


    function del(uint index) returns(uint success){
    	uint i = index;
    	while(i < lenClust) {
    		clust[i] = clust[i+1];
        	i += 1;
        }
        lenClust -= 1;
    	return 1;
	}

	function extract_clusters(uint startCluster, int dist) internal returns(uint success){
		cluster_node cluster = clust[startCluster];
		if(cluster.distance < dist) {
			extractedClust[extractedClustLen] = cluster;
			extractedClustLen += 1;
		}
		while(cluster.leafs[0].id!=-1) {
			if(cluster.leafs[0].distance < dist) {
				extractedClust[extractedClustLen] = cluster.leafs[0];
				extractedClustLen += 1;
			}
			cluster = cluster.leafs[0];
		}
		while(cluster.leafs[1].id!=-1) {
			if(cluster.leafs[1].distance < dist) {
				extractedClust[extractedClustLen] = cluster.leafs[1];
				extractedClustLen += 1;
			}
			cluster = cluster.leafs[1];
		}
		if(cluster.leafs[0].distance < dist) {
			extractedClust[extractedClustLen] = cluster.leafs[0];
			extractedClustLen += 1;
		}
		if(cluster.leafs[1].distance < dist) {
			extractedClust[extractedClustLen] = cluster.leafs[1];
			extractedClustLen += 1;
		}
		return 1;
	}

	function get_cluster_elements(uint startCluster) internal returns(uint success) {
		cluster_node cluster = clust[startCluster];
		if(cluster.id >= 0) {
			cluster_element[numElements] = cluster.id;
			numElements += 1;
		}
		while(cluster.leafs[0].id!=-1) {
			if(cluster.leafs[0].id >= 0) {
				cluster_element[numElements] = cluster.leafs[0].id;
				numElements += 1;
			}
			cluster = cluster.leafs[0];
		}
		while(cluster.leafs[1].id!=-1) {
			if(cluster.leafs[1].id >= 0) {
				cluster_element[numElements] = cluster.leafs[1].id;
				numElements += 1;
			}
			cluster = cluster.leafs[1];
		}
		if(cluster.leafs[0].id >= 0) {
			cluster_element[numElements] = cluster.leafs[0].id;
			numElements += 1;
		}
		if(cluster.leafs[1].id >= 0) {
			cluster_element[numElements] = cluster.leafs[1].id;
			numElements += 1;
		}
		return 1;
	}
}