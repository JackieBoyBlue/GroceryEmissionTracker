# Code for embedding strings into vectors
# This code is adapted from a Hugging Face model card [no date]
# Accessed 18/07/2023
# https://huggingface.co/intfloat/e5-large-v2


from torch import Tensor
from transformers import AutoTokenizer, AutoModel

from scipy.spatial.distance import cosine


class E5:
    """E5 class for comparing texts using the E5 model."""
    models = ('large', 'base', 'small')

    def __init__(self, version: str = 'large') -> None:
        """Initialises the E5 class."""

        if not isinstance(version, str): raise TypeError('model must be a string')
        if version not in E5.models: raise ValueError(f'version must be one of {E5.models}')

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

        print('Getting embeddings...')
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
    
    E5 = E5()
    # embeddings = E5.get_embeddings(item_1, category_1, category_2, category_3, category_4, category_5, category_6, category_7, category_8, category_9, category_10, category_11, category_12)
    # print(embeddings)
    similarities = E5.get_category_strings(item_1, category_1, category_2, category_3, category_4, category_5, category_6, category_7, category_8, category_9, category_10, category_11, category_12)
    print(similarities)
