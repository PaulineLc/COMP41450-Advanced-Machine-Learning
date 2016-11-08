import math
import operator

from Assignment.text_data import Document
from Assignment.dataset import TextData


class TextClassifier:

    training_set = None

    def __init__(self, document):
        self.document = document
        self.similarity = {}
        self.count_classes = {'business': 0, 'politics': 0, 'sport': 0, 'technology': 0}

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
            self.classify()
        if weighted:
            # Todo: add weighted method
            pass
        else:
            return self.classify_no_weight(k)

    def create_similarity_dic(self):
        self.document.create_bag_of_words()
        for doc_id in TextClassifier.training_set:
            if doc_id == self.document.doc_id:
                continue  # ignore entry if it is the same document...
            curr_doc = Document(doc_id)
            curr_doc.create_bag_of_words()
            curr_cos = self.calculate_cosine(curr_doc)
            self.similarity[int(doc_id)] = curr_cos # TODO: try remove the cast to integer - is it useful?
        return self.similarity

    def classify_no_weight(self, k):
        # takes the k nearest neighbours
        # sort dictionary of articles by their cosine
        # TODO: improve this - when you call a recursion with k-1 you don't need to execute it all again.
        sorted_similarities = sorted(self.similarity.items(), key=operator.itemgetter(1), reverse=True)
        for i in range(k):
            curr_doc_id = sorted_similarities[i][0]
            curr_doc_cat = Document(curr_doc_id).get_category()
            self.count_classes[curr_doc_cat] += 1
        highest = max(self.count_classes.values()) # get max value
        potential_classes = [k for k,v in self.count_classes.items() if v == highest]  # get all entries with max value
        if len(potential_classes) > 1:
            k -= 1  # classify text using 1 less neighbours until there are either no equality
            return self.classify(k)
        return potential_classes[0]

    def calculate_cosine(self, other_doc):
        numerator = 0
        for term in self.document.bag_of_words:
            try:
                other_occur = other_doc.bag_of_words[term]
            except KeyError:
                continue # skip if term not in other document
            numerator += self.document.bag_of_words[term] * other_occur
        denominator_1 = math.sqrt(sum(map(lambda x:x**2, other_doc.bag_of_words.values())))
        denominator_2 = math.sqrt(sum(map(lambda x:x**2, self.document.bag_of_words.values())))

        return float(numerator / (denominator_1 * denominator_2))