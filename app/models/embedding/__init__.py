import os
from .e5 import E5
from .gtr_t5 import GTR_T5
from .instructor import Instructor
from .sentence_t5 import SentenceT5

match os.getenv('MODEL'):
    case 'e5':
        model = E5()
    case 'gtr_t5':
        model = GTR_T5()
    case 'sentence_t5':
        model = SentenceT5()
    case 'instructor':
        model = Instructor()
    case _:
        raise ValueError('MODEL environment variable must be one of e5, gtr_t5, sentence_t5, or instructor')
