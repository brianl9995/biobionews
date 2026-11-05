[![Tests](https://github.com/brianl9995/biobionews/workflows/Tests/badge.svg)](https://github.com/brianl9995/biobionews/actions?workflow=Tests)

BioBioNews
==========

Lector de noticias de biobiochile.cl en TUI

![BioBioNews TUI](screen.png)

## Instrucciones de instalación

### 1. Clonar Repositorio

```bash
git clone https://github.com/brianl9995/biobionews.git
cd biobionews
```

### 2. Configurar entorno virtual e instalar dependencias

Requiere Python 3.10 o superior.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 3. Ejecutar

```bash
PYTHONPATH=src .venv/bin/python -m biobionews --limit 10
```

Teclas: `↑`/`↓` navegar entre noticias, `enter` abrir en el navegador, `r` actualizar, `q` salir. Se actualiza solo cada 1 minuto. Por defecto usa todo el ancho de la pantalla (limitable con `--width`).

Opciones: `--plain` (imprime sin TUI), `--limit/-l` (cantidad de noticias), `--width/-w` (ancho del texto), `--lines/-n` (líneas por noticia).

### 4. Tests

```bash
.venv/bin/pip install pytest pytest-mock
.venv/bin/pytest
```
