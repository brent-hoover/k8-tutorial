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


## Stage 3: Adding SOPS secrets

This guide explains how to set up and use SOPS (Secrets OPerationS) for managing encrypted secrets in a Kubernetes cluster.

## Prerequisites

- A running Kubernetes cluster (k3d in this example)
- helm
- kubectl

## Installation Steps

### 1. Install Required Tools

```bash
# Install age encryption tool
brew install age

# Install sops
brew install sops
```

### 2. Generate Age Keys

```bash
# Generate a key pair
age-keygen -o key.txt
```

### 3. Create SOPS Configuration

Create a `.sops.yaml` file in your project root:

```bash
# Get your public key
PUBLIC_KEY=$(cat key.txt | grep "public key:" | cut -d " " -f 4)

# Create .sops.yaml configuration
cat > .sops.yaml << EOF
creation_rules:
  - path_regex: .*\.yaml
    age: ${PUBLIC_KEY}
EOF
```

### 4. Install SOPS Operator

```bash
# Add the helm repository
helm repo add sops https://isindir.github.io/sops-secrets-operator/
helm repo update

# Install the operator
helm install sops sops/sops-secrets-operator -n sops --create-namespace
```

### 5. Configure Operator with Age Key

```bash
# Create a secret with the age key
kubectl create secret generic sops-age \
  --namespace sops \
  --from-file=key.txt

# Edit the operator deployment to mount the key
kubectl edit deployment sops-sops-secrets-operator -n sops
```

Add these sections to the deployment:

Under `spec.template.spec.containers[0]`, add:
```yaml
        volumeMounts:
        - name: age-key
          mountPath: /etc/sops/keys
          readOnly: true
```

Under `spec.template.spec`, add:
```yaml
      volumes:
      - name: age-key
        secret:
          secretName: sops-age
```

### 6. Create an Encrypted Secret

Create a file named `test-sops-secret.yaml`:

```bash
cat > test-sops-secret.yaml << EOF
apiVersion: isindir.github.com/v1alpha3
kind: SopsSecret
metadata:
  name: test-sops-secret
spec:
  secretTemplates:
    - name: my-secret
      data:
        ANOTHER_SECRET_KEY: $(echo -n "testvalue" | base64)
EOF
```

Encrypt the secret:
```bash
sops --encrypt --in-place --encrypted-regex '^(data)$' test-sops-secret.yaml
```

Apply the encrypted secret:
```bash
kubectl apply -f test-sops-secret.yaml
```

### 7. Verify the Secret

```bash
# Check the SopsSecret status
kubectl get sopssecret test-sops-secret

# Check the created Kubernetes secret
kubectl get secret my-secret
```

## Using the Secret in Your Application

Reference the secret in your deployment:

```yaml
spec:
  template:
    spec:
      containers:
        - name: your-container
          env:
            - name: ANOTHER_SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: my-secret
                  key: ANOTHER_SECRET_KEY
```

## File Management and Security

### Files to Commit
- `.sops.yaml` - Contains only your public key configuration
- Encrypted secret files (after running `sops --encrypt`)
- Your Kubernetes manifests and other code

### Files to NOT Commit
- `key.txt` - Contains your age private key
- Any unencrypted secret files
- Any files containing raw secret values

### Managing key.txt
Do not delete `key.txt`! Instead:
1. Add it to your `.gitignore`:
   ```bash
   echo "key.txt" >> .gitignore
   ```
2. Store it securely (like in a password manager)
3. Keep a secure backup
4. You'll need this same key file to:
   - Decrypt secrets locally
   - Set up SOPS in other clusters
   - Rotate or modify secrets

## Notes
- SOPS secrets can be shared across clusters that share the same age key
- Always verify files are encrypted before committing
- Consider using git pre-commit hooks to prevent accidental secret commits