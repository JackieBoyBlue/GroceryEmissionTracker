import os
from .e5 import E5
from .gtr_t5 import GTR_T5
from .instructor import Instructor
from .sentence_t5 import SentenceT5

if os.getenv('MODEL') == 'e5':
    model = E5()
elif os.getenv('MODEL') == 'gtr_t5':
    model = GTR_T5()
elif os.getenv('MODEL') == 'sentence_t5':
    model = SentenceT5()
elif os.getenv('MODEL') == 'instructor':
    model = Instructor()
else:
    raise ValueError('MODEL environment variable must be one of e5, gtr_t5, sentence_t5, or instructor')