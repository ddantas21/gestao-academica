"""Núcleo compartilhado pelas equipes ALFA e BETA.

* :mod:`nucleo.entidade` — base das entidades, fábrica de propriedades validadas e regras
  de validação genéricas.
* :mod:`nucleo.gerenciador` — gerenciador genérico com CRUD, persistência em .txt e
  integridade referencial.

Regra de dependência: o núcleo não importa nada de ``alfa``, ``beta`` nem das interfaces.
"""
