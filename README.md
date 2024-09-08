# KubernetesLab

This is WAY faster than the previous all ansible implementation

## Usage

Everything is configured in the config.yml

For now its manual, but I will create an ansible wrapper to automate.

```python
# Create yaml files
python creation.py

# Apply namespaces first
kubectl apply -f namespaces

# Then apply all deployments, service accounts, services, etc
kubectl apply -f deployments --recursive

# If you want to delete
kubectl delete -f deployments --recursive
kubectl delete -f namespaces
```

## Next steps

Add ansible wrapper
