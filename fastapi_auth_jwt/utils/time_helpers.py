from datetime import timedelta
from typing import Optional, Union

from ..config.types import EXPIRATION_DTYPE


def cast_to_seconds(expiration: Union[EXPIRATION_DTYPE, None]) -> Optional[int]:
    """
    Casts the expiration value to seconds.

    Args:
        expiration (Union[EXPIRATION_DTYPE, None]): The expiration value to be casted.

    Returns:
        Optional[int]: The expiration value in seconds.

    Raises:
        TypeError: If the expiration type is invalid.
    """
    if expiration is None:
        return None
    if isinstance(expiration, int):
        return expiration
    if isinstance(expiration, float):
        return int(expiration)
    if isinstance(expiration, timedelta):
        return int(expiration.total_seconds())
    raise TypeError("Invalid expiration type")


__all__ = ["cast_to_seconds"]
