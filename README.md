# k8 Tutorial using k3d

1. [Install k3d](https://k3d.io/stable/#installation)
2. Create the cluster for this tutorial using 
```bash
k3d cluster create python-flask --port "8080:5000@loadbalancer"
```
4. Build the docker image:
```bash
docker build -t flask-app:latest .
```
5. Import the image into k3d
```bash
 k3d image import flask-app:latest -c python-flask 
```
6. Install the helm chart
```bash
helm install flask-app ./flask-app
```
7. Test the app is serving
```bash
curl http://localhost:8080/hello
```
