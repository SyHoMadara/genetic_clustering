from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import silhouette_score
from sklearn import datasets
import random

class GeneticClustering:
    def __init__(self, chromosome, points=None):
        self.chromosome = chromosome
        self.points = points
        self.list_class = list(set(datasets.load_iris().target))
        self.fitness_scores = self._get_fitness()

    def _get_fitness(self):
        labels = np.array(list((self.chromosome.values())))
        unique_labels = np.unique(labels)

        if len(unique_labels) < 2:
            return -1

        fitness_scores = silhouette_score(self.points, labels)
        return fitness_scores

    def mutation(self):
        self._change_labels_to_nearest_center()
        self._change_random_label()
        self._assign_nearest_cluster_label()
        return self.chromosome

    def generate(self, parent):
        new_generation = dict()
        for index in range(len(self.chromosome)):
            probability = random.random()

            if probability < 0.45:
                new_generation[index] = self.chromosome[index]
            elif probability < 0.90:
                new_generation[index] = parent.chromosome[index]
            else:
                new_generation[index] = random.choice(self.list_class)

        return GeneticClustering(new_generation, self.points)

    def _change_labels_to_nearest_center(self):
        sample_cluster_labels = random.choice(self.list_class)
        labels_nearest_cluster = self._find_labels_nearest_cluster(sample_cluster_labels)

        number_of_sample_cluster_labels = list(self.chromosome.values()).count(sample_cluster_labels)

        counter = 1
        for index in range(len(self.chromosome)):
            if self.chromosome[index] == sample_cluster_labels:
                self.chromosome[index] = labels_nearest_cluster
                counter += 1
            if counter == number_of_sample_cluster_labels // 3:
                break

    def _find_labels_nearest_cluster(self, sample_cluster_labels):
        sample_cluster = {}
        _sample_cluster = []
        for index in range(len(self.chromosome)):
            if self.chromosome[index] == sample_cluster_labels:
                _sample_cluster.append(self.points[index])
        sample_cluster[sample_cluster_labels] = _sample_cluster

        clusters = {}
        for _label in self.list_class:
            cluster = []
            if sample_cluster_labels != _label:
                for index, label in self.chromosome.items():
                    if label == _label:
                        cluster.append(self.points[index])
                clusters[_label] = cluster

        center_sample = self._find_center_cluster(sample_cluster[sample_cluster_labels])

        centers = []
        for cluster in clusters:
            temp = self._find_center_cluster(clusters[cluster])
            centers.append(temp)

        distance = []
        for center in centers:
            _distance = self._calculate_distance(center, center_sample)
            distance.append(_distance)

        distance = np.argsort(distance)
        index_nearest_center = distance[0]

        labels_nearest_cluster = list(clusters)[index_nearest_center]
        return labels_nearest_cluster

    def _find_center_cluster(self, cluster):
        data = list(map(np.array, cluster))
        data = np.array(data)
        center = np.mean(data, axis=0)
        return center

    def _assign_nearest_cluster_label(self):
        sample_index = random.choice(list(self.chromosome.keys()))

        _distance = []
        for index in range(len(self.chromosome)):
            _distance.append(self._calculate_distance(self.points[index], self.points[sample_index]))
        _distance = np.argsort(_distance)
        index_nearest_point = _distance[1]
        self.chromosome[sample_index] = self.chromosome[index_nearest_point]

    def _calculate_distance(self, point1, point2):
        point1 = np.array(point1)
        point2 = np.array(point2)
        distance = np.sqrt(np.sum((point1 - point2) ** 2))
        return distance

    def _change_random_label(self):
        sample_index = random.choice(list(self.chromosome.keys()))
        sample_labels = random.choice(self.list_class)

        while sample_labels == self.chromosome[sample_index]:
            sample_labels = random.choice(self.list_class)
        self.chromosome[sample_index] = sample_labels


class GeneticCluster:
    def __init__(self, x, y, size_population=50, goal=0.9, repeat=100):
        self.x = x
        self.genom = list(np.unique(y))
        self.size_population = size_population
        self.goal = goal
        self.repeat = repeat
        self.population = []
        self.fitness = []

    def fit(self):
        for _ in range(self.size_population):
            chromosome = self._create_random_chromosome()
            self.population.append(GeneticClustering(chromosome, self.x))
        self.counter = 1

        while True:
            if self.counter == self.repeat:
                break
            self.population = sorted(self.population, key=lambda chromosome: chromosome.fitness_scores, reverse=True)

            if self.goal <= self.population[0].fitness_scores <= 1:
                break

            new_generation = list()

            size_best_people = int((10 * self.size_population) / 100)
            new_generation.extend(self.population[:size_best_people])

            for _ in range(int((90 * self.size_population) / 100)):
                parent1 = random.choice(self.population[:50])
                parent2 = random.choice(self.population[:50])
                child = parent1.generate(parent2)
                new_generation.append(child)

            self.population = new_generation

            for index in range(self.size_population):
                self.population[index] = GeneticClustering(self.population[index].mutation(), self.x)

            self.fitness.append(self.population[0].fitness_scores)
            self.counter += 1
            self.show()

    def _create_random_chromosome(self):
        chromosome = dict()
        for index in range(self.x.shape[0]):
            chromosome[index] = random.choice(self.genom)
        return chromosome

    def show(self):
        print(f"loop is  : {self.counter}")
        print(f"generation: {self.population[0]} \tFitness: {self.population[0].fitness_scores}")

    def show_plot(self):
        plt.plot(self.fitness)


iris = pd.read_csv("iris.data")
x = iris.loc[:,iris.columns != 'class']
y = iris['class']

genetic_cluster = GeneticCluster(x, y)
genetic_cluster.fit()
genetic_cluster.show_plot()
plt.show()