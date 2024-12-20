## 1. Build Docker image 
```commandline
docker build -t flask-app .
```

## 2. Run Docker image
```commandline
docker run -p 9001:9001 flask-app
```