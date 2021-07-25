from parameters import *
import numpy as np

def euclidean(c1, c2):
    return pow(pow(c1[0] - c2[0], 2) + pow(c1[1] - c2[1], 2), 0.5)

def parse(filename):
    with open(filename) as f:
        content = f.readlines()

    for line in content:
        l = line.strip().split()
        content[int(l[0]) - 1] = (int(l[1]), int(l[2]))
    return content

def distance(list):
    distance = [[0 for i in range(len(list))] for j in range(len(list))]
    for i in range(len(list)):
        for j in range(len(list)):
            if (i == j):
                distance[i][j] = 0
            elif (i < j):
                distance[i][j] = euclidean(list[i], list[j])
            else:
                distance[i][j] = distance[j][i]
    return distance

def placeInitPheromone():
    pheromone = [[0 for i in range(numCities)] for j in range(numCities)]
    for i in range(len(pheromone)):
        for j in range(len(pheromone)):
            if (i == j):
                pheromone[i][j] = 0
            elif (i < j):
                pheromone[i][j] = initPheromoneAmt
            else:
                pheromone[i][j] = pheromone[j][i]
    return pheromone

def assignCities():
    antLocations = [-1 for i in range(numAnts)]
    cityPerGroup = np.random.permutation(numCities)
    for i in range(numAnts):
        antLocations[i] = cityPerGroup[i%numCities]
    return antLocations

def pseudorandomProportionalRule(path):
    probOfSelection = [0 for i in range(numCities)]
    src = path[0]
    for j in range(numCities):
        if (j in path):
            probOfSelection[j] = 0
        else:
            probOfSelection[j] = pheromoneAmounts[src][j]/pow(distances[src][j], beta)
    return probOfSelection

def antSystemTransitionRule(path):
    probOfSelection = [0 for i in range(numCities)]
    # find denominator
    src = path[-1]
    den = 0
    for dest in range(numCities):
        if (src == dest):
            continue
        den += pow(pheromoneAmounts[src][dest], alpha)/pow(distances[src][dest], beta)

    for j in range(numCities):
        if (j in path):
            probOfSelection[j] = 0
        else:
            probOfSelection[j] = pow(pheromoneAmounts[src][j], alpha)/pow(distances[src][j], beta)
            if (den == 0):
                probOfSelection[j] = pow(10, 100)
            else:
                probOfSelection[j] /= den
    return probOfSelection

def evaporate():
    for i in range(numCities):
        for j in range(numCities):
            pheromoneAmounts[i][j] = (1 - evapRate)*pheromoneAmounts[i][j]

def offlinePheromoneUpdate(length, path):
    for i in range(numCities):
        for j in range(numCities):
            if (i < j):
                for k in range(len(path) - 1):
                    if (path[k] == i and path[k + 1] == j) or (path[k] == j and path[k + 1] == i):
                        pheromoneAmounts[i][j] = ((1 - evapRate)*pheromoneAmounts[i][j]) + (evapRate/length)
                    else:
                        pheromoneAmounts[i][j] = ((1 - evapRate)*pheromoneAmounts[i][j])
            elif (i > j):
                pheromoneAmounts[i][j] = pheromoneAmounts[j][i]

def forage():
    paths = [[antLocations[i]] for i in range(numAnts)]
    pathLengths = [0 for i in range(numAnts)]
    for i in range(maxIter):
        q = np.random.rand()
        for j in range(numAnts):
            probOfSelection = []
            if (q <= q0):
                probOfSelection = pseudorandomProportionalRule(paths[j])
            else:
                probOfSelection = antSystemTransitionRule(paths[j])
            evaporate()
            maximum = max(probOfSelection)
            if (maximum != 0):
                paths[j].append(probOfSelection.index(max(probOfSelection)))
                pathLengths[j] += distances[paths[j][-2]][paths[j][-1]]
                pheromoneAmounts[paths[j][0]][paths[j][-1]] = ((1 - decayCoeff)*pheromoneAmounts[paths[j][0]][paths[j][-1]]) + (decayCoeff*initPheromoneAmt)
                pheromoneAmounts[paths[j][-1]][paths[j][0]] = pheromoneAmounts[paths[j][0]][paths[j][-1]]
        bestAnt = pathLengths.index(min(pathLengths))
        offlinePheromoneUpdate(pathLengths[bestAnt], paths[bestAnt])
    return min(pathLengths), paths[pathLengths.index(min(pathLengths))]

coordinates = parse(filename)
distances = distance(coordinates)

for i in range(3):
    numAnts = numAntsList[0]
    alpha = alphaList[i]
    beta = betaList[i]
    decayCoeff = decayCoeffList[0]

    pheromoneAmounts = placeInitPheromone()
    antLocations = assignCities()
    bestPathLength, bestPath = forage()

    print(round(bestPathLength), bestPath, len(bestPath))