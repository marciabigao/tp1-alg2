# Como executar o projeto

## Ambiente

A execução deve ser feita em um ambiente Linux com Python 3 instalado.

## 1. Instalar dependências

No terminal, dentro da pasta do projeto:

```bash
pip3 install -r requirements.txt
```

## 2. Gerar arquivo com coordenadas

Se o arquivo data/butecos_geocoded.csv não existir, execute:

```bash
python3 geocode.py
```

## 3. Executar a aplicação

```bash
python3 app.py
```

## 4. Acessar no navegador

Abra o endereço que aparecer no terminal, por exemplo:

```
http://127.0.0.1:8050/
```


