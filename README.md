# k8 Tutorial using k3d

## Stage 1: Basic setup

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

## Stage 2: Setting up a Sealed secret

1. Install the sealed secret operator
```bash
helm repo add sealed-secrets https://bitnami-labs.github.io/sealed-secrets
helm repo update
helm install sealed-secrets sealed-secrets/sealed-secrets -n kube-system
```
2. Create your regular secret
```bash
kubectl create secret generic flask-secret \
  --from-literal=SUPER_SECRET_KEY=your-secret-value \
  --dry-run=client -o yaml > secret.yaml
```
3. Use kubeseal to encrypt it (noting the namespace)
```bash
kubeseal --format yaml \
  --controller-namespace kube-system \
  --controller-name sealed-secrets \
  < secret.yaml > sealed-secret.yaml
```
4. Apply the sealed secret
```bash
kubectl apply -f sealed-secret.yaml
```
5. Reference it in your deployment
```yaml
env:
  - name: SUPER_SECRET_KEY
    valueFrom:
      secretKeyRef:
        name: flask-secret
        key: SUPER_SECRET_KEY
```
6. The sealed secret is safe to commit while the secret.yml should be
excluded or deleted