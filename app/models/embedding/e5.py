# Code for embedding strings into vectors
# This code is adapted from a Hugging Face model card [no date]
# Accessed 18/07/2023
# https://huggingface.co/intfloat/e5-large-v2


from torch import Tensor
from transformers import AutoTokenizer, AutoModel
if __name__ == '__main__':
    from _interface import EmbeddingModelInterface
else:
    from ._interface import EmbeddingModelInterface


class E5(EmbeddingModelInterface):
    """E5 class for comparing texts using the E5 model."""
    versions = ('large', 'base', 'small')

    def __repr__(self) -> str:
        return 'E5'

    def __init__(self, version: str = 'large') -> None:
        """Initialises the E5 class."""

        if not isinstance(version, str): raise TypeError('model must be a string')
        if version not in E5.versions: raise ValueError(f'version must be one of {E5.versions}')

        print(f'Loading E5-{version}-v2 model...')
        self.tokenizer = AutoTokenizer.from_pretrained(f'intfloat/e5-{version}-v2')
        self.model = AutoModel.from_pretrained(f'intfloat/e5-{version}-v2')
        print('Loaded model')
    

    def get_embeddings(self, string:str, *args: str) -> list:
        """Get the embeddings of texts."""

        if not isinstance(string, str): raise TypeError('string must be a string')
        if not all(isinstance(arg, str) for arg in args): raise TypeError('args must be a string')

        args = [string] + [arg for arg in args]
        input_texts = [f'query: {arg}' for arg in args]

        # print('Getting embeddings...')
        batch_dict = self.tokenizer(input_texts, max_length=512, padding=True, truncation=True, return_tensors='pt')
        outputs = self.model(**batch_dict)
        last_hidden_states = outputs.last_hidden_state
        attention_mask = batch_dict.attention_mask

        return E5.average_pool(last_hidden_states, attention_mask).tolist()


    @staticmethod
    def average_pool(last_hidden_states: Tensor, attention_mask: Tensor) -> Tensor:
        """Returns the average of the last hidden states."""

        last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
        return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]

    # end of referenced code



if __name__ == '__main__':
    from test import test
    test(E5)
