from ast import Call
from ctypes import CFUNCTYPE, WINFUNCTYPE, POINTER, WinDLL, CDLL,OleDLL, c_bool, c_char, c_char_p, c_int, c_int32, c_void_p, c_wchar, c_wchar_p, byref, create_string_buffer, c_byte
import ctypes
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

CallbackFunction = Callable[[str], bool]
CallbackFunctionC = CFUNCTYPE(c_bool, c_void_p)

class TXmlConnectorWrapper:
    _path: Path
    _dll: WinDLL
    _callback_c_func: CallbackFunctionC | None

    def __init__(self, path: Path):
        self._path = path
        self._load()
        self._set_return_types()
        self._callback_c_func = None

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

    def _free_memory_callback_wrapper(self, f: CallbackFunction) -> CallbackFunction:
        def _wrapper(data_pointer: int):
            py_str = c_char_p(data_pointer).value.decode()
            self.free_memory(data_pointer)
            return f(py_str)
        return _wrapper

    def initialize(self, log_directory: Path, log_level: int) -> int:
        return int(self._dll.Initialize(str(log_directory).encode('ascii'), c_int32(log_level)))

    def uninitialize(self) -> int:
        return int(self._dll.UnInitialize())

    def set_callback(self, callback: Callable[[int], None], wrap: bool = True) -> bool:
        if wrap:
            callback = self._free_memory_callback_wrapper(callback)
        self._callback_c_func = CallbackFunctionC(callback)
        return bool(self._dll.SetCallback(self._callback_c_func))

    # don't need it I think
    # # CallingConvention StdCall
    # def set_callback_ex(self, pCallbackEx, userData: int) -> bool:
    #     self._callback_c_func = CallbackFunctionC(callback)
    #     raise NotImplementedError(self.set_callback_ex)

    # CallingConvention StdCall
    def send_command(self, command: str) -> str:
        return self._dll.SendCommand(command.encode('ascii')).decode()

    # CallingConvention StdCall
    def free_memory(self, data_pointer: int) -> bool:
        return self._dll.FreeMemory(c_void_p(data_pointer))

    def set_log_level(self, log_level: int) -> int:
        return self._dll.SetLogLevel(log_level)
