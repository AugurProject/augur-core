def sqrt(n):
    approx = n/2.0
    better = (approx + n/approx)/2.0
    i = 0
    while i < 11:
        approx = better
        better = (approx + n/approx)/2.0
        i += 1
    return approx

def euclidDist(x:arr, y:arr):
	i = 0
	distSquare = 0
	while i < len(x):
		distSquare += (x[i] - y[i])^2
		i += 1
	return(self.sqrt(distSquare))

