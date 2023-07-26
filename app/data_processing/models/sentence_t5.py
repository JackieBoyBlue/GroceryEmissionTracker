from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine


class SentenceT5:
    """SentenceT5 class for comparing texts using the T5 model."""
    models = ('base', 'large', 'xl', 'xxl')

    def __init__(self, version: str = 'xxl') -> None:
        """Initialise the SentenceT5 class."""

        if not isinstance(version, str): raise TypeError('version must be a string')
        if version not in self.models: raise ValueError(f'version must be one of {self.models}')

        print('Initialising SentenceT5 class...')
        self.model = SentenceTransformer(f'sentence-transformers/sentence-t5-{version}')
        print('Loaded model')


    def get_embeddings(self, string: str, *args: str) -> list:
        """Get the embeddings of texts."""

        if not isinstance(string, str): raise TypeError('string must be a string')
        if not all(isinstance(arg, str) for arg in args): raise TypeError('args must be a string')

        print('Getting embeddings...')
        return self.model.encode([string] + [arg for arg in args])
    

    def get_category_strings(self, compare_this: str, to_this: str, *and_this: str, get_all_cosines: bool = False) -> tuple:
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
    
    
    def get_category_vectors(self, compare_this: list, to_this: list, *and_this: list, get_all_cosines: bool = False) -> tuple:
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

        

if __name__ == '__main__':

    item_1 = 'Tesco Lemons 4 Pack'
    category_1 = 'Meat and meat products (excl. poultry)'
    category_2 = 'Poultry meat and poultry meat products'
    category_3 = 'Fish and fish products from catch'
    category_4 = 'Fruit and vegetables'
    category_5 = 'Vegetable and animal oils and fats'
    category_6 = 'Dairy products'
    category_7 = 'Grain mill products; starches and starch products'
    category_8 = 'Bread; rusks and biscuits; pastry goods and cakes'
    category_9 = 'Cocoa; chocolate and sugar confectionery'
    category_10 = 'Other food products (incl. sugar)'
    category_11 = 'Non-alcoholic beverages'
    category_12 = 'Alcoholic beverages'
    
    SenT5 = SentenceT5()
    similarities = SenT5.get_category_strings(item_1, category_1, category_2, category_3, category_4, category_5, category_6, category_7, category_8, category_9, category_10, category_11, category_12)
    print(similarities)
