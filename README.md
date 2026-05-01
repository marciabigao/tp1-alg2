# Como executar o projeto

## 1. Instalar dependências

No terminal, dentro da pasta do projeto:

```bash
pip install dash dash-leaflet
```

## 2. Gerar arquivo com coordenadas (se necessário)

Se o arquivo `data/butecos_geocoded.csv` não existir, execute:

```bash
python geocode.py
```

## 3. Executar a aplicação

```bash
python app.py
```


## 4. Acessar no navegador

Abra:

```
http://127.0.0.1:8050/
```


