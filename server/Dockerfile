FROM python:3.6
COPY . /app
WORKDIR /app

# This is a weird fix for the dependencies. Be careful when modifying.
RUN pip install -r requirements.txt
RUN pip uninstall tensorflow tensorflow-estimator tensorflow-hub tensorflowjs numpy Keras Keras-Applications Keras-Preprocessing -y
RUN pip install tensorflow keras
RUN pip install tensorflowjs
RUN pip uninstall numpy -y
RUN pip install numpy

EXPOSE 8999
CMD ["python", "server.py"]
