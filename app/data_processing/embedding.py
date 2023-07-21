# @article{wang2022text,
#   title={Text Embeddings by Weakly-Supervised Contrastive Pre-training},
#   author={Wang, Liang and Yang, Nan and Huang, Xiaolong and Jiao, Binxing and Yang, Linjun and Jiang, Daxin and Majumder, Rangan and Wei, Furu},
#   journal={arXiv preprint arXiv:2212.03533},
#   year={2022}
# }

# Code for embedding strings into vectors
# This code is adapted from a Hugging Face model card [no date]
# Accessed 18/07/2023
# https://huggingface.co/intfloat/e5-large-v2


from torch import Tensor
from transformers import AutoTokenizer, AutoModel


class Embedding:
    """Embeds strings into vectors."""

    tokenizer = None
    model = None
    tensor = None

    def __init__(self, model: str = 'intfloat/e5-large-v2', tokenizer: str = None):
        """Initialises the Embedding class."""

        if not isinstance(model, str): raise TypeError('model must be a string')

        if not tokenizer: tokenizer = model
        if not isinstance(tokenizer, str): raise TypeError('tokenizer must be a string')

        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer or model)
        self.model = AutoModel.from_pretrained(model)


    def average_pool(last_hidden_states: Tensor, attention_mask: Tensor) -> Tensor:
        """Returns the average of the last hidden states."""

        last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
        return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]
    

    def __call__(self, text: str) -> Tensor:
        """Returns the embedding of the input string."""

        if not isinstance(text, str): raise TypeError('text must be a string')
        if not self.tokenizer: raise RuntimeError('tokenizer must be initialized')
        if not self.model: raise RuntimeError('model must be initialized')

        inputs = self.tokenizer(text, return_tensors="pt")
        outputs = self.model(**inputs)
        last_hidden_states = outputs.last_hidden_state
        attention_mask = inputs.attention_mask

        tensor = Embedding.average_pool(last_hidden_states, attention_mask)
        self.tensor = tensor
        return tensor
    
    # end of referenced code

    @staticmethod
    def get_score(compare_this: Tensor, to_this: Tensor) -> float:
        """Returns the cosine similarity between two tensors."""

        if not isinstance(compare_this, Tensor): raise TypeError('compare_this must be a Tensor')
        if not isinstance(to_this, Tensor): raise TypeError('to_this must be a Tensor')

        return compare_this[0].dot(to_this[0]).item()

    @staticmethod
    def get_vector(tensor: Tensor) -> list:
        """Returns the vector from a tensor."""

        if not isinstance(tensor, Tensor): raise TypeError('tensor must be a Tensor')

        return tensor[0].tolist()




# # Example usage
embedder = Embedding()

left = embedder('Increase investment in infrastructure and public services.')
right = embedder('Reduce the tax burdon on wealthy individuals.')

# print(Embedding.get_vector(left))

# print(Embedding.get_score(left, right))
