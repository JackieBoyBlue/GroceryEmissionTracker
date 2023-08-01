from sentence_transformers import SentenceTransformer
if __name__ == '__main__':
    from _interface import EmbeddingModelInterface
else:
    from ._interface import EmbeddingModelInterface


class GTR_T5(EmbeddingModelInterface):
    """GTR_T5 class for comparing texts using the T5 model."""
    versions = ('base', 'large', 'xl', 'xxl')

    def __init__(self, version: str = 'xxl') -> None:
        """Initialise the SentenceT5 class."""

        if not isinstance(version, str): raise TypeError('version must be a string')
        if version not in self.versions: raise ValueError(f'version must be one of {self.versions}')

        print('Initialising SentenceT5 class...')
        self.model = SentenceTransformer(f'sentence-transformers/gtr-t5-{version}')
        print('Loaded model')


    def get_embeddings(self, string: str, *args: str) -> list:
        """Get the embeddings of texts."""

        if not isinstance(string, str): raise TypeError('string must be a string')
        if not all(isinstance(arg, str) for arg in args): raise TypeError('args must be a string')

        print('Getting embeddings...')
        return self.model.encode([string] + [arg for arg in args])

        

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
    
    gtr_t5 = GTR_T5()
    # embeddings = gtr_t5.get_embeddings(item_1, category_1, category_2, category_3, category_4, category_5, category_6, category_7, category_8, category_9, category_10, category_11, category_12)
    # print(embeddings)
    similarities = gtr_t5.get_category_strings(item_1, category_1, category_2, category_3, category_4, category_5, category_6, category_7, category_8, category_9, category_10, category_11, category_12)
    print(similarities)
