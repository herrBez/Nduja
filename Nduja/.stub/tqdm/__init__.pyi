from typing import Optional, Iterable, Any, Dict, Union, Iterator


class tqdm(object):
    def __init__(self,
                 iterable: Optional[Union[Dict[Any, Any],Iterable[Any]]],
                 desc: Optional[str] = ...,
                 total: Optional[int] = ...,
                 leave: bool = ...,
                 file: Optional[Any] = ...,
                 ncols: Optional[int] = ...,
                 mininterval: float = ...,
                 maxinterval: float = ...,
                 miniters: Optional[int] = ...,
                 ascii: Optional[bool] = ...,
                 disable: bool = ...,
                 unit: str = ...,
                 unit_scale: bool = ...,
                 dynamic_ncols: bool = ...,
                 smoothing: float = ...,
                 bar_format: Optional[str] = ...,
                 initial: int = ...,
                 position: Optional[int] = ...,
                 postfix: Optional[Dict[Any, Any]] = ...,
                 unit_divisor: float = ...,
                 gui: bool = ...,
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