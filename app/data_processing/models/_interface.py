from scipy.spatial.distance import cosine

class EmbeddingModelInterface:
    """Embedding model for comparing texts."""

    versions = ()

    def __init__(self, version: str = ''):
        pass

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
    
    
    def get_category_from_vectors(self, compare_this: list, to_this: list, *and_this: list, get_all_cosines: bool = False) -> tuple:
        """Takes a target vector and n vectors to compare it to, and returns the most similar vector and its cosine similarity."""

        if not isinstance(compare_this, list): raise TypeError('compare_this must be a list')
        if not isinstance(to_this, list): raise TypeError('to_this must be a list')
        if not all(isinstance(arg, list) for arg in and_this): raise TypeError('and_this must be a list')

        cosines = {}

        counter = 0
        compare_to = [to_this] + [arg for arg in and_this]
        for to_this in compare_to:
            cosines[compare_to[counter]] = 1 - cosine(compare_this, to_this)
            counter += 1

        if get_all_cosines: return cosines

        most_similar = max(cosines, key=cosines.get)
        return (most_similar, cosines[most_similar])
