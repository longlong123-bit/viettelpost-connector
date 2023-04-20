from typing import Dict, Any, Sequence, Tuple
from abc import ABC


class InputDict(ABC):
    @staticmethod
    def parser_dict(data: Dict[str, Any]) -> Sequence[Tuple]:
        raise NotImplementedError('Subclass needs to be implemented this static method: parser_dict')


class OutputDict(ABC):
    @staticmethod
    def parser_class(cls, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError('Subclass needs to be implemented this static method: parser_class')
