from InstructorEmbedding import INSTRUCTOR
import torch
if __name__ == '__main__':
    from _interface import EmbeddingModelInterface
else:
    from ._interface import EmbeddingModelInterface


class Instructor(EmbeddingModelInterface):
    """Instructor class for comparing texts using the Instructor model."""
    versions = ('base', 'large', 'xl')

    def __repr__(self) -> str:
        return 'Instructor'
    
    def __init__(self, version: str = 'xl'):
        """Initialise the Instructor model."""

        if not isinstance(version, str): raise TypeError('version must be a string')
        if version not in Instructor.versions: raise ValueError(f'version must be one of {Instructor.versions}')

        print(f'Loading Instructor-{version}...')
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
    from test import test
    test(Instructor)
    