# Glossário

## Termos do domínio

| Termo | Definição |
|-------|-----------|
| **Aluno** | Discente matriculado em exatamente um curso. É identificado pela matrícula |
| **Curso** | Programa oferecido pela instituição, presencial ou EAD |
| **Disciplina** | Componente curricular de um curso, com carga horária, ministrado por um professor |
| **Professor** | Docente que leciona disciplinas |
| **Matrícula** | Identificador único do aluno. No relatório, "matriculado no curso" significa ter o `codigo_curso` daquele curso |
| **Modalidade** | Forma de oferta do curso: `Presencial` ou `EAD` |
| **Carga horária** | Total de horas da disciplina (inteiro > 0) |
| **Relatório integrado** | Listagem do RF15 que relaciona aluno, curso, disciplina e professor |
| **Equipe ALFA** | Responsável pelos módulos Aluno e Curso |
| **Equipe BETA** | Responsável pelos módulos Professor e Disciplina |
| **Integração Final** | Seção 5 do enunciado: o fluxo completo executado pelo `main.py` |

## Termos técnicos do projeto

| Termo | Definição | Onde |
|-------|-----------|------|
| **Entidade** | Classe que só guarda e valida dados (modelo de dados) | `nucleo/entidade.py`, `alfa/`, `beta/` |
| **Gerenciador** | Classe que mantém a lista de uma entidade e faz CRUD, persistência e integridade | `nucleo/gerenciador.py` |
| **Chave** | Primeiro campo de `CAMPOS`, o identificador único | `Gerenciador.chave` |
| **`CAMPOS`** | Tupla com a ordem dos atributos, que é também a ordem das colunas no `.txt` | cada entidade |
| **`CAMPOS_UNICOS`** | Campos, além da chave, que não podem repetir (ex.: CPF) | gerenciadores |
| **Dependentes** | Lista de quem referencia uma entidade; bloqueia a exclusão e propaga a troca de código | `Gerenciador.dependentes` |
| **Vínculo** | Campo que guarda o código de outra entidade (`codigo_curso`, `codigo_professor`) | Aluno, Disciplina |
| **Cascata** | Atualização automática dos dependentes quando um código muda | `Gerenciador.alterar` |
| **`ENTIDADES`** | Metadados que tornam as interfaces genéricas | `sistema.py` |
| **Fachada** | `SistemaIntegrado`, o único ponto de acesso das interfaces | `sistema.py` |
| **Linhas ignoradas** | Linhas do `.txt` que não puderam ser lidas na carga | `Gerenciador.linhas_ignoradas` |
| **Validador de curso** | Função injetada na BETA que diz se um curso existe | `SistemaBeta(validador_curso=...)` |
| **Normalizar** | Remover acentos e pôr em minúsculas para comparar textos | `nucleo.entidade.normalizar` |

## Termos de engenharia de software

| Termo | Definição |
|-------|-----------|
| **ADR** | *Architecture Decision Record*: registro curto de uma decisão de arquitetura e do seu porquê |
| **arc42** | Modelo de 12 seções para documentar arquitetura de software |
| **C4** | Modelo de diagramas em níveis: Contexto, Contêiner, Componente e Código |
| **CRC** | Cartão Classe-Responsabilidade-Colaboradores |
| **CRUD** | *Create, Read, Update, Delete*: cadastrar, listar/pesquisar, alterar e excluir |
| **Débito técnico** | Atalho ou limitação consciente que tem custo futuro de manutenção |
| **Doctest** | Exemplo dentro da docstring que é executado como teste |
| **Facade** | Padrão que oferece uma interface simples sobre um conjunto de classes |
| **Fitness function** | Teste automatizado que verifica uma característica da arquitetura (ex.: regras de importação) |
| **Injeção de dependência** | Passar a um objeto aquilo de que ele precisa, em vez de ele mesmo criar |
| **Gravação atômica** | Escrita que termina por inteiro ou não acontece |
| **Repository** | Padrão que isola o acesso aos dados das regras de negócio |
| **Rollback** | Desfazer uma operação parcialmente aplicada |
| **Template Method** | Padrão em que a classe base define o algoritmo e as subclasses preenchem passos |
| **Rastreabilidade** | Ligação documentada entre requisito, código e teste |
