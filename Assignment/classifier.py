import math
import operator
import random

from Assignment.text_data import Document


class TextClassifier:

    training_set = None
    test_set = None
    all_bags_of_words = {} # created to store the bags of words and avoid calculating the same one twice.

    def __init__(self, document):
        self.document = document
        self.similarity = {}

    @classmethod
    def define_training_set(cls, dataset):
        TextClassifier.training_set = dataset

    def classify(self, weighted=False):
        # TODO: redesign to remove recursion
        print("Enter the number of neighbours (an integer >= 1):")
        try:
            k = int(input())
        except ValueError:
            print("Please enter an integer >= 1")
        if k < 1:
            print("k must be >1")
            self.classify() # try avoiding to recurse here
        if weighted:
            return self.classify_weighted(k)
        else:
            return self.classify_no_weight(k)

    def create_similarity_dic(self):
        self.document.create_bag_of_words()
        for doc_id in TextClassifier.training_set:
            if doc_id == self.document.doc_id:
                continue  # ignore entry if it is the same document...
            if doc_id not in TextClassifier.all_bags_of_words:
                curr_doc = Document(doc_id)
                TextClassifier.all_bags_of_words[doc_id] = curr_doc.create_bag_of_words()
            curr_cos = self.calculate_cosine(doc_id)
            self.similarity[doc_id] = curr_cos
        return self.similarity

    def classify_no_weight(self, k):
        # takes the k nearest neighbours
        # sort dictionary of articles by their cosine
        # TODO: improve this - when you call a recursion with k-1 you don't need to execute it all again.
        count_per_classes = {'business': 0, 'politics': 0, 'sport': 0, 'technology': 0}
        sorted_similarities = sorted(self.similarity.items(), key=operator.itemgetter(1), reverse=True)
        for i in range(k):
            curr_doc_id = sorted_similarities[i][0]
            curr_doc_cat = Document(curr_doc_id).get_category()
            count_per_classes[curr_doc_cat] += 1
        highest = max(count_per_classes.values())  # get max value
        potential_classes = [k for k, v in count_per_classes.items() if v == highest]  # get all entries with max value
        if len(potential_classes) > 1:
            k -= 1  # classify text using 1 less neighbours until there are either no equality
            return self.classify_no_weight(k)
        return potential_classes[0]

    def classify_weighted(self, k):
        weight_per_classes = {'business': 0, 'politics': 0, 'sport': 0, 'technology': 0}
        sorted_similarities = sorted(self.similarity.items(), key=operator.itemgetter(1), reverse=True)
        for i in range(k):
            curr_doc_id = sorted_similarities[i][0]
            curr_doc_cat = Document(curr_doc_id).get_category()
            weight_per_classes[curr_doc_cat] += sorted_similarities[i][1] * (k-i)  # more votes to higher ranked results
        highest = max(weight_per_classes.values())
        potential_classes = [k for k, v in weight_per_classes.items() if v == highest]
        if len(potential_classes) > 1:
            k -= 1  # classify text using 1 less neighbours until there are either no equality
            return self.classify_weighted(k)  # it will eventually return because at k = 1 there can be no conflict
        return potential_classes[0]

    def calculate_cosine(self, other_doc_id):
        numerator = 0
        for term in self.document.bag_of_words:
            if term in TextClassifier.all_bags_of_words[other_doc_id]:
                other_occur = TextClassifier.all_bags_of_words[other_doc_id][term]
                numerator += self.document.bag_of_words[term] * other_occur
        denominator_1 = math.sqrt(sum(map(lambda x: x**2, TextClassifier.all_bags_of_words[other_doc_id].values())))
        denominator_2 = math.sqrt(sum(map(lambda x: x**2, self.document.bag_of_words.values())))

        return float(numerator / (denominator_1 * denominator_2))

    @staticmethod
    def get_accuracy(data_set):
        nb_accurate_results_unweighted = 0
        nb_accurate_results_weighted = 0
        i = 1
        for document in data_set:
            i += 1
            clf = TextClassifier(Document(document))
            clf.create_similarity_dic()
            k = random.randint(1,10)
            predicted_class_unweighted = clf.classify_no_weight(k)
            predicted_class_weighted = clf.classify_weighted(k)
            actual_class = Document(document).get_category()
            if predicted_class_unweighted == actual_class:
                nb_accurate_results_unweighted += 1
            if predicted_class_weighted == actual_class:
                nb_accurate_results_weighted += 1
        return nb_accurate_results_unweighted / data_set.shape[0], nb_accurate_results_weighted / data_set.shape[0]