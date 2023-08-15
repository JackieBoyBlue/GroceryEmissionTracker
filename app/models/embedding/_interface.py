from abc import ABC, abstractmethod
from scipy.spatial.distance import cosine

class EmbeddingModelInterface(ABC):
    """Embedding model for comparing texts."""

    versions = ()

    @abstractmethod
    def __init__(self, version: str = ''):
        pass

    @abstractmethod
    def get_embeddings(self, item: str, *categories: str) -> list:
        pass

    def get_category_from_strings(self, compare_this: str, to_this: str, *and_this: str, get_all_cosines: bool = False) -> tuple:
        """Takes a target string and n strings to compare it to, and returns the most similar string and its cosine similarity."""

        if not isinstance(compare_this, str): raise TypeError('compare_this must be a string')
        if not isinstance(to_this, str): raise TypeError('to_this must be a string')
        if not all(isinstance(arg, str) for arg in and_this): raise TypeError('and_this must be a string')

        cosines = {}

        embeddings = self.get_embeddings(compare_this, to_this, *and_this)
        print('Got embeddings')

        counter = 0
        compare_to = [to_this] + [arg for arg in and_this]
        for embedding in embeddings[1:]:
            cosines[compare_to[counter]] = 1 - cosine(embeddings[0], embedding)
            counter += 1

        if get_all_cosines: return cosines

        most_similar = max(cosines, key=cosines.get)
        return (most_similar, cosines[most_similar])
    
    
    def get_category_from_vectors(self, compare_this: list, to_this: tuple, *and_this: tuple, get_all_cosines: bool = False) -> tuple:
        """Takes a target vector and n vectors to compare it to, and returns the most similar vector and its cosine similarity."""

        if not isinstance(compare_this, list): raise TypeError('compare_this must be a list')
        if not isinstance(to_this, tuple): raise TypeError('to_this must be a tuple with (category_name, vector)')
        if not all(isinstance(arg, tuple) for arg in and_this): raise TypeError('and_this must be a tuple with (category_name, vector)')

        cosines = {}

        counter = 0
        compare_to = [to_this] + [arg for arg in and_this]

        for to_this in compare_to:
            cosines[to_this[0]] = 1 - cosine(compare_this, to_this[1])
            counter += 1

        if get_all_cosines: return cosines

        most_similar = max(cosines, key=cosines.get)
        return (most_similar, cosines[most_similar])
