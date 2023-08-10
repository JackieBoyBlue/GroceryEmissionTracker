from InstructorEmbedding import INSTRUCTOR
if __name__ == '__main__':
    from _interface import EmbeddingModelInterface
else:
    from ._interface import EmbeddingModelInterface


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

        # print('Getting embeddings...')
        return self.model.encode(all_inputs).tolist()


if __name__ == '__main__':
    import pathlib, csv, ast
    from colorama import Fore

    Embedder = Instructor()

    emission_factor_path = pathlib.Path(__file__).parent.parent.parent / 'datasets/category_emission_factors.py'

    with open(emission_factor_path, 'r') as f:
        emission_factors = ast.literal_eval(f.read()[28:])

    emission_factor_vectors = {emission_factor: Embedder.get_embeddings(emission_factor)[0] for emission_factor in emission_factors.keys()}
    # print(emission_factor_vectors['Meat and meat products (excl. poultry)'])

    csv_path = pathlib.Path(__file__).parent.parent.parent / 'datasets/foodItems-categories-pricesPerKg.csv'

    results = []
    total_correct = 0

    confusion_matrix = {}
    correct_items = []
    incorrect_items = []

    with open(csv_path, 'r') as f:
        from test import test
        test(Instructor)
    