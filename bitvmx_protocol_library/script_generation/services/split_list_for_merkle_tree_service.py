import math
from typing import List


class SplitListForMerkleTreeService:

    def __call__(self, input_list: List[str]):
        if len(input_list) == 1:
            return input_list[0]
        else:
            middle_point = int(2 ** math.ceil(math.log2(len(input_list))) / 2)
            return [
                self(input_list[:middle_point]),
                self(input_list[middle_point:]),
            ]
