from typing import Optional, Iterable, Any, Dict, Union, Iterator


class tqdm(object):
    def __init__(self,
                 iterable: Optional[Union[Dict[Any, Any],Iterable[Any]]],
                 desc: Optional[str],
                 total: Optional[int],
                 leave: bool = True,
                 file: Optional[Any] = None,
                 ncols: Optional[int] = None,
                 mininterval: float = 0.1,
                 maxinterval: float = 10.0,
                 miniters: Optional[int] = None,
                 ascii: Optional[bool] = None,
                 disable: bool = False,
                 unit: str = 'it',
                 unit_scale: bool = False,
                 dynamic_ncols: bool = False,
                 smoothing: float = 0.3,
                 bar_format: Optional[str] = None,
                 initial: int = 0,
                 position: Optional[int] = None,
                 postfix: Optional[Dict[Any, Any]] = None,
                 unit_divisor: float = 1000,
                 gui: bool = False,
                 **kwargs: Any) -> None: ...

    def __iter__(self) -> Iterator[Any]: ...

    def update(self, n: int) -> None: ...

    def close(self) -> None: ...

    def unpause(self) -> None: ...

    def clear(self, nomove: bool) -> None: ...

    def refresh(self) -> None: ...

    @staticmethod
    def write(s: str, file: Any, end: str) -> None: ...

    def set_description(self, desc: Optional[str], refresh: bool) -> None: ...

    def set_postfix(self, ordered_dict: Optional[Dict[Any, Any]],
                    refresh: bool,
                    **kwargs: Any) -> None: ...

    def trange(*args: Any, **kwargs: Any) -> Any: ...