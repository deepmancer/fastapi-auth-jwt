import copy
import datetime
from typing import Any, Dict, Optional, Union

import jwt


class JWTHandler:
    """
    A handler class for encoding and decoding JWT tokens.

    This class provides methods to encode a payload into a JWT token and decode a JWT token back into a payload.
    It supports setting an expiration time and handles various exceptions during the encoding and decoding process.

    Attributes:
        secret (str): The secret key used for encoding and decoding the JWT.
        algorithm (str): The algorithm used for encoding and decoding the JWT. Defaults to 'HS256'.
    """

    def __init__(self, secret: str, algorithm: str = "HS256"):
        """
        Initialize the JWTHandler with a secret key and an optional algorithm.

        Args:
            secret (str): The secret key used for encoding and decoding the JWT.
            algorithm (str): The algorithm used for encoding and decoding the JWT. Defaults to 'HS256'.
        """
        self.secret = secret
        self.algorithm = algorithm

    def encode(
        self,
        payload: Dict[str, Any],
        expiration: Optional[Union[float, int]] = None,
        **kwargs,
    ) -> str:
        """
        Encode a payload into a JWT token.

        This method encodes a given payload into a JWT token, optionally setting an expiration time.
        Additional key-value pairs can be passed as kwargs to be included in the payload.

        Args:
            payload (Dict[str, Any]): The payload data to encode into the JWT.
            expiration (Optional[Union[float, int]]): Optional expiration time in seconds. Defaults to None.

        Returns:
            str: The encoded JWT token.

        Raises:
            TypeError: If the payload contains an invalid type.
            jwt.PyJWTError: If an error occurs during encoding.
            Exception: If any other unexpected error occurs.

        Examples:
            >>> handler = JWTHandler(secret="mysecret")
            >>> token = handler.encode({"user_id": 123}, expiration=3600)
            >>> print(token)
            'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'

            >>> # Encoding with additional fields in the payload
            >>> token = handler.encode({"user_id": 123}, role="admin", expiration=3600)
            >>> print(token)
            'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
        """
        try:
            _payload = copy.deepcopy(payload)
            if expiration:
                _payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(
                    seconds=int(expiration),
                )
            _payload.update(kwargs)
            token = jwt.encode(_payload, self.secret, algorithm=self.algorithm)
            return token
        except jwt.PyJWTError as e:
            raise e
        except TypeError as e:
            raise TypeError(f"Invalid type in payload: {e}")
        except Exception as e:
            raise Exception(
                f"An unexpected error occurred while encoding the token: {e}"
            )

    def decode(
        self,
        token: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Decode a JWT token into a payload.

        This method decodes a given JWT token back into its payload. The expiration field ('exp')
        is removed from the decoded payload if it exists.

        Args:
            token (str): The JWT token to decode.

        Returns:
            Dict[str, Any]: The decoded payload.

        Raises:
            jwt.PyJWTError: If an error occurs during decoding.
            Exception: If any other unexpected error occurs.

        Examples:
            >>> handler = JWTHandler(secret="mysecret")
            >>> token = handler.encode({"user_id": 123}, expiration=3600)
            >>> payload = handler.decode(token)
            >>> print(payload)
            {'user_id': 123}

            >>> # Decoding a token with additional fields
            >>> token = handler.encode({"user_id": 123, "role": "admin"}, expiration=3600)
            >>> payload = handler.decode(token)
            >>> print(payload)
            {'user_id': 123, 'role': 'admin'}
        """
        try:
            decoded = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                **kwargs,
            )
            decoded.pop("exp", None)
            return decoded
        except jwt.PyJWTError as e:
            raise e
        except Exception as e:
            raise Exception(
                f"An unexpected error occurred while decoding the token: {e}"
            )


__all__ = ["JWTHandler"]
