"""Instrumentos. Importar este pacote registra todos (huayin.listar_instrumentos())."""
from .base import REGISTRO, VARIANTES, Golpe, Instrumento, criar, listar, registrar, tecnica, variante  # noqa: F401
from . import pipa, guqin, guzheng, alaudes, yangqin, arcos, sopros, percussao  # noqa: F401,E401
