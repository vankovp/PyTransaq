from ctypes import CFUNCTYPE, POINTER, WinDLL, c_bool, c_char, c_char_p, c_int, c_int32, c_void_p
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

CallbackFunction = CFUNCTYPE(c_void_p, POINTER(c_char))

class TXmlConnectorWrapper:
    _path: Path
    _dll: WinDLL

    def __init__(self, path: Path):
        self._path = path
        self._load()
        self._set_return_types()

    def _load(self) -> None:
        self._dll: WinDLL = WinDLL(self._path)

    def _set_return_types(self) -> None:
        self._dll.Initialize.restype = c_int
        self._dll.UnInitialize.restype = c_int
        self._dll.SetCallback.restype = c_bool
        self._dll.SetCallbackEx.restype = c_bool
        self._dll.SendCommand.restype = c_char_p
        self._dll.FreeMemory.restype = c_bool
        self._dll.SetLogLevel.restype = c_int

    # CallingConvention Winapi
    def initialize(self, log_directory: Path, log_level: int) -> int:
        return int(self._dll.Initialize(str(log_directory).encode('ascii'), c_int32(log_level)))

    # CallingConvention Winapi
    def uninitialize(self) -> int:
        return int(self._dll.UnInitialize())

    # CallingConvention StdCall
    def set_callback(self, callback: Callable[[int], None]) -> bool:
        return bool(self._dll.SetCallback(CallbackFunction(callback)))

    # CallingConvention StdCall
    def set_callback_ex(self, pCallbackEx, userData: int) -> bool:
        raise NotImplementedError(self.set_callback_ex)

    # CallingConvention StdCall
    def send_command(self, pData: str) -> str:
        return self._dll.SendCommand(pData.encode('ascii')).decode()

    # CallingConvention StdCall
    def free_memory(self, data_pointer: int) -> bool:
        return self._dll.FreeMemory(data_pointer)

    # CallingConvention Winapi
    def set_log_level(self, log_level: int) -> int:
        return self._dll.SetLogLevel(log_level)
