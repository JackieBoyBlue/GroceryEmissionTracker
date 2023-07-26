from InstructorEmbedding import INSTRUCTOR
from _interface import EmbeddingModelInterface


class Instructor(EmbeddingModelInterface):
    """Instructor class for comparing texts using the Instructor model."""
    versions = ('base', 'large', 'xl')

    def __init__(self, version: str = 'xl'):
        """Initialise the Instructor model."""

        if not isinstance(version, str): raise TypeError('version must be a string')
        if version not in Instructor.versions: raise ValueError(f'version must be one of {Instructor.versions}')

        print(f'Loading Instructor-{version} model...')
        self.model = INSTRUCTOR(f'hkunlp/instructor-{version}')
        print('Loaded model')
    

    def get_embeddings(self, item: str, *categories: str) -> list:
        """Get the embeddings of texts."""

        if not isinstance(item, str): raise TypeError('string must be a string')
        if not all(isinstance(category, str) for category in categories): raise TypeError('args must be a string')

        item_input = [f'Represent the Food item: {item}']
        category_inputs = [f'Represent the Food category: {category}' for category in categories]
        all_inputs = item_input + category_inputs

        print('Getting embeddings...')
        return self.model.encode(all_inputs)


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

    instructor = Instructor()
    # embeddings = instructor.get_embeddings(item_1, category_1, category_2, category_3, category_4, category_5, category_6, category_7, category_8, category_9, category_10, category_11, category_12)
    # print(embeddings)
    similarities = instructor.get_category_strings(item_1, category_1, category_2, category_3, category_4, category_5, category_6, category_7, category_8, category_9, category_10, category_11, category_12)
    print(similarities)
    