from sentence_transformers import SentenceTransformer
if __name__ == '__main__':
    from _interface import EmbeddingModelInterface
else:
    from ._interface import EmbeddingModelInterface


class SentenceT5(EmbeddingModelInterface):
    """SentenceT5 class for comparing texts using the T5 model."""
    versions = ('base', 'large', 'xl', 'xxl')

    def __repr__(self) -> str:
        return 'SentenceT5'
    
    def __init__(self, version: str = 'xxl') -> None:
        """Initialise the SentenceT5 class."""

        if not isinstance(version, str): raise TypeError('version must be a string')
        if version not in self.versions: raise ValueError(f'version must be one of {self.versions}')

        print('Initialising SentenceT5 class...')
        self.model = SentenceTransformer(f'sentence-transformers/sentence-t5-{version}')
        print('Loaded model')


    def get_embeddings(self, string: str, *args: str) -> list:
        """Get the embeddings of texts."""

        if not isinstance(string, str): raise TypeError('string must be a string')
        if not all(isinstance(arg, str) for arg in args): raise TypeError('args must be a string')

        # print('Getting embeddings...')
        return self.model.encode([string] + [arg for arg in args]).tolist()

        

if __name__ == '__main__':
    from test import test
    test(SentenceT5)
