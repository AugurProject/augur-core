from scipy.misc import logsumexp
import numpy
import math

initialLiquidity = 50000000
cumulativeScale = 1
alpha = 0.007
numOutcomes = 2
prior_vector = numpy.array([.53, .47])

# z is a reasonable estimate to kickoff the shares vector with
z = initialLiquidity / (cumulativeScale + alpha*numOutcomes*cumulativeScale*math.log(numOutcomes))
shares_vector = numpy.array([z, z])

# So each price needs to be greater than prior odds set
# pi(q0) >=phii
def check_prices():
    i = 0
    while i < len(shares_vector):
        if(price(i) < prior_vector[i]):
            return(i)
        i+=1
    return(-1)

def lslmsr(share_vector):
    bq = sum(share_vector)*alpha
    return(bq*logsumexp(share_vector/bq))

def price(outcome):
    shares_vector[outcome] += 1
    x = lslmsr(shares_vector)
    shares_vector[outcome] -= 1
    y = lslmsr(shares_vector)
    return((x-y)/1)

# obj is minimize(v_subsidy - lslmsr(share_vector)) so it's as close to 0 as possible but not negative and maintain the check_prices -1 invariant

def optimize():
    optOutcome = check_prices()
    while(optOutcome!=-1):
        shares_vector[optOutcome]+=1
        while((initialLiquidity - lslmsr(shares_vector)) < 0):
            shares_vector[0] -= 1
            shares_vector[1] -= 1
        optOutcome = check_prices()
    print shares_vector
    print price(0)
    print price(1)
    
optimize()