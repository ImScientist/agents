# Agents

Deployment of conversational RAGs on a Kubernetes cluster (the exact goal is not clear yet).

We will use Langchain, externally hosted LLMs (OpenAI) and local deployment of Milvus vector DB.

### Setup Milvus

We will deploy Milvus with standalone mode:

```shell
kubectl create namespace milvus

helm upgrade -n milvus --install milvus-chart \
    --set cluster.enabled=false \
    --set etcd.replicaCount=1 \
    --set pulsarv3.enabled=false \
    --set minio.mode=standalone milvus/milvus
    
# Access the webui on http://127.0.0.1:9091/webui/
kubectl -n milvus port-forward service/milvus-chart 9091:9091

# Access the vectordb
kubectl -n milvus port-forward service/milvus-chart 19530:19530
```

Fill in the vectordb (you need a valid `OPENAI_API_KEY`):

```shell
python src/vectordb.py
```

### Resources:

- [Milvus instalation](https://milvus.io/docs/install_cluster-helm.md)
