from typing import Dict, List, MutableMapping, MutableSequence, Union
from typing_extensions import TypeAlias

Number = Union[float, int]
JsonLike: TypeAlias = "JSON"
JSON = MutableMapping[
    str,
    Union[
        # even if MutableMapping/Dict and MutableSequence/List are essentially the same for this,
        # provide them explicitly to avoid annoying typing mismatch warnings not perfectly equal
        MutableMapping[str, JsonLike],
        MutableSequence[JsonLike],
        Dict[str, JsonLike],
        List[JsonLike],
        Number, bool, str, None,
    ]
]
