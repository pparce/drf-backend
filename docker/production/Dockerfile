# Usar una imagen base de Python
FROM python:3.9

# Establecer variables de entorno
ENV PYTHONUNBUFFERED=1

# Crear y establecer el directorio de trabajo
WORKDIR /app

# Copiar el archivo requirements.txt
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . /app

# Copia el script de shell desde la raíz del proyecto
COPY ../../manage_migrations.sh /app


# Ejecuta collectstatic cuando se inicie el contenedor
CMD ["python", "manage.py", "collectstatic", "--noinput"]

