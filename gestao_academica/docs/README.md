# Documentação Técnica

Ponto de partida para quem vai manter ou estender o **Sistema de Gestão Acadêmica**.

## Por onde começar

| Seu objetivo | Leia, nesta ordem |
|--------------|-------------------|
| **Entender o sistema** (primeiro contato) | [README do projeto](../README.md) → [arc42 §1–5](arquitetura/arc42.md) → [glossário](glossario.md) |
| **Corrigir um bug** | [Guia de manutenção §2 e §4](manutencao/guia-de-manutencao.md) → [modelo de classes §4](projeto/modelo-de-classes.md#4-contrato-do-gerenciador-api-pública) → [referência da API](api/referencia.md) |
| **Adicionar uma funcionalidade** | [Guia de manutenção §3 (receitas)](manutencao/guia-de-manutencao.md#3-receitas) → [ADRs](adr/README.md) → [estratégia de testes](qualidade/estrategia-de-testes.md) |
| **Mudar a arquitetura** | [arc42 completo](arquitetura/arc42.md) → [ADRs](adr/README.md) → [riscos e débito técnico](qualidade/riscos-e-divida-tecnica.md) |
| **Avaliar o trabalho** | [Especificação e rastreabilidade](requisitos/especificacao.md) → [arc42 §10](arquitetura/arc42.md#10-requisitos-de-qualidade) |

## Mapa dos documentos

```
docs/
├── README.md                         ← você está aqui
├── arquitetura/
│   └── arc42.md                      visão completa: contexto, camadas, execução, qualidade (C4 + UML)
├── adr/
│   ├── README.md                     índice e modelo de ADR
│   └── ADR-001 … ADR-010             decisões de arquitetura e seus porquês
├── requisitos/
│   └── especificacao.md              casos de uso, RF/RN/RNF, critérios de aceitação, rastreabilidade
├── projeto/
│   ├── modelo-de-dados.md            ER, dicionário de dados, formato dos .txt, integridade
│   └── modelo-de-classes.md          diagrama de classes, CRC, padrões, contratos da API
├── manutencao/
│   └── guia-de-manutencao.md         ambiente, onde mexer, receitas passo a passo, solução de problemas
├── qualidade/
│   ├── estrategia-de-testes.md       pirâmide, convenções, fitness functions, roteiro manual da GUI
│   └── riscos-e-divida-tecnica.md    registro de riscos, débitos e evoluções
├── api/
│   └── referencia.md                 GERADO das docstrings (não editar à mão)
└── glossario.md                      termos do domínio, do projeto e de engenharia
```

Na raiz do projeto: [`CONTRIBUTING.md`](../CONTRIBUTING.md) (padrões de código e de
documentação) e [`CHANGELOG.md`](../CHANGELOG.md) (histórico de versões).

## Técnicas utilizadas

| Técnica | Referência | Documento |
|---------|-----------|-----------|
| arc42 | Starke & Hruschka, arc42.org | `arquitetura/arc42.md` |
| Modelo C4 | Simon Brown, c4model.com | arc42 §3, §5 e §7 |
| ADR | Michael Nygard (2011) | `adr/` |
| UML (classes, sequência, estados, casos de uso) | OMG UML 2.5 | arc42 §6, `projeto/`, `requisitos/` |
| Especificação de requisitos | IEEE 830 / ISO/IEC/IEEE 29148 (simplificada) | `requisitos/especificacao.md` |
| Cenários de qualidade | ISO/IEC 25010 + cenários de atributo de qualidade (SEI) | arc42 §10 |
| Cartões CRC | Beck & Cunningham (1989) | `projeto/modelo-de-classes.md` |
| Fitness functions | *Building Evolutionary Architectures* (Ford, Parsons, Kua) | `testes/test_arquitetura.py` |
| Docstrings Google Style | PEP 257 + Google Python Style Guide | todo o código |
| Keep a Changelog + SemVer | keepachangelog.com, semver.org | `CHANGELOG.md` |

## Como manter esta documentação viva

- **Os diagramas são texto (Mermaid):** edite o bloco no Markdown, e ele é versionado
  junto com o código. Visualize no GitHub ou no VS Code (extensão *Markdown Preview
  Mermaid Support*).
- **A referência da API é gerada:** `python ferramentas/gerar_referencia_api.py`.
- **Os testes cobram a documentação:** docstrings ausentes, regras de dependência
  violadas, documentos removidos e referência desatualizada fazem a suíte falhar.
- **Uma decisão nova pede um ADR novo.** ADRs aceitos não são reescritos.
