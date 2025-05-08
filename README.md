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
python src/vectorstore.py
```

Test the webapp with

```shell
streamlit run src/app.py
```

Create the image for the app:
```shell
docker build -t streamlit-app -f Dockerfile .

  --network:host \
  --add-host=host.docker.internal:172.17.0.1 \
  --add-host host.docker.internal=host-gateway \
  --network=host \


docker run -it --rm --name streamlitapp -p 8501:8501 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  --network=bridge \
  streamlit-app /bin/bash

curl -X 'GET' http://127.0.0.1:9091/webui/
curl -X 'GET' host.docker.internal:9091/webui/
```


### Resources:

- [Milvus instalation](https://milvus.io/docs/install_cluster-helm.md)
