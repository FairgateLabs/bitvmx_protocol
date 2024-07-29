from abc import ABC, abstractmethod
from typing import Optional


class FaucetServiceInterface(ABC):

    @abstractmethod
    def __call__(
        self,
        amount: Optional[int] = 1000000,
        destination_address: Optional[str] = "tb1qd28npep0s8frcm3y7dxqajkcy2m40eysplyr9v",
    ):
        pass
