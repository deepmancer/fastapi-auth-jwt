import copy
import datetime
from typing import Any, Dict, Optional

import jwt


class JWTHandler:
    def __init__(self, secret: str, algorithm: str = "HS256"):
        self.secret = secret
        self.algorithm = algorithm

    def encode(
        self,
        payload: Dict[str, Any],
        expiration: Optional[int] = None,
        **kwargs,
    ) -> str:
        try:
            _payload = copy.deepcopy(payload)
            if expiration:
                _payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(seconds=expiration)
            _payload.update(kwargs)
            token = jwt.encode(_payload, self.secret, algorithm=self.algorithm)
            return token
        except jwt.PyJWTError as e:
            raise e
        except TypeError as e:
            raise TypeError(f"Invalid type in payload: {e}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred while encoding the token: {e}")

    def decode(
        self,
        token: str,
        **kwargs,
    ) -> Dict[str, Any]:
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
            raise Exception(f"An unexpected error occurred while decoding the token: {e}")


__all__ = ["JWTHandler"]
