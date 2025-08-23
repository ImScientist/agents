# Agents

Deployment of conversational RAGs on a Kubernetes cluster (the exact goal is not clear yet).

We will use Langchain, externally hosted LLMs (OpenAI), local deployment of Milvus vector DB and of a 
Postgres DB (for conversation history).

<p align="center">
  <img width="500" alt="project_diagram" src="project_diagram.png" />
</p>


## Setup Milvus vector DB

- We will deploy Milvus with standalone mode:
  ```shell
  kubectl create namespace milvus

  helm upgrade -n milvus --install milvus-chart \
    --set cluster.enabled=false \
    --set etcd.replicaCount=1 \
    --set pulsarv3.enabled=false \
    --set minio.mode=standalone milvus/milvus
    
  # Access the webui on http://127.0.0.1:9091/webui/
  kubectl -n milvus port-forward service/milvus-chart 9091:9091
  
  # The default vectorstore URI and access token should be 
  # MINIO_URI=http://localhost:19530
  # MINIO_ACCESS_TOKEN=minioadmin:minioadmin
  ```

- Fill in the vectordb (you need a valid `OPENAI_API_KEY`):
  ```shell
  export OPENAI_API_KEY=...
  export MINIO_URI=...
  export MINIO_ACCESS_TOKEN=...
  
  kubectl -n milvus port-forward service/milvus-chart 19530:19530
  python src/vectorstore.py
  ```

## Setup Postgres as LangGraph Checkpoint saver

- Use the bitnami helm chart:
  ```shell
  helm repo add bitnami https://charts.bitnami.com/bitnami
  
  kubectl create ns postgres
  
  helm install --namespace postgres \
    psql-chart oci://registry-1.docker.io/bitnamicharts/postgresql \
    --set auth.postgresPassword=pwd
  ```

- Run once the python script `src/memory.py` to setup the DB:
  ```shell 
  kubectl port-forward --namespace postgres svc/psql-chart-postgresql 5432:5432
  
  # You have to change this connection string if you have used different parameters when creating the chart  
  export POSTGRES_CONN_STRING=postgres://postgres:pwd@localhost:5432/postgres
  
  # Execute script to setup the Postgres DB
  python src/memory.py
  
  # Check the changes (optional) ...
  psql "${POSTGRES_CONN_STRING}"
  ```

## Webapp

To test the webapp, you need a valid `OPENAI_API_KEY` env variable, the right access credentials for the
vectorstore: `MINIO_ACCESS_TOKEN`, `MINIO_URI`, and the connection string to the Postgres DB `POSTGRES_CONN_STRING`.

- To test the webapp locally, execute:
  ```shell
  export OPENAI_API_KEY=...
  kubectl -n milvus port-forward service/milvus-chart 19530:19530
  kubectl -n postgres port-forward svc/psql-chart-postgresql 5432:5432

  # Access the webui on http://127.0.0.1:8501/
  streamlit run src/app.py
  ```

- To deploy the Helm chart, follow the steps below:

    - Create the webapp image and, eventually, publish it:
      ```shell
      docker build -t imscientist/streamlit-app -f Dockerfile .
      
      # Optional; replace `imscientist` with your dockerhub username
      docker push imscientist/streamlit-app:latest
      ```
      If the image is not published then in `helm/values.yaml` you have to set `image.pullPolicy=Never`.

    - Create a new namespace and secrets:
      ```shell
      kubectl create namespace webapp
      
      # Create a secret that contains all relevant env variables
      # Note that service URIs are extended with ${namespace}.svc.cluster.local
      kubectl -n webapp create secret generic ext-services-credentials \
        --from-literal=OPENAI_API_KEY=$OPENAI_API_KEY \
        --from-literal=MINIO_ACCESS_TOKEN=minioadmin:minioadmin \
        --from-literal=MINIO_URI=http://milvus-chart.milvus.svc.cluster.local:19530 \
        --from-literal=POSTGRES_CONN_STRING=postgres://postgres:pwd@psql-chart-postgresql.postgres.svc.cluster.local:5432/postgres
 
      # Inspect the secret content
      kubectl -n webapp get secret ext-services-credentials -o yaml
    
      # Each value in `data` section is base64 encoded. To decode a single element execute:
      kubectl -n webapp get secret ext-services-credentials \
        -o jsonpath='{.data.MINIO_ACCESS_TOKEN}' | base64 -d; echo
      ```

    - Create a single webapp deployment and a service:
      ```shell
      helm install -n webapp -f helm/values.yaml webapp-chart helm
  
      # Access the webapp on http://127.0.0.1:8501/
      kubectl -n webapp port-forward service/webapp-chart 8501:8501
      ```

    - To delete the resources execute:
      ```shell
      helm -n webapp delete webapp-chart
      kubectl -n webapp delete secret ext-services-credentials
      kubectl delete ns webapp
      
      helm -n postgres delete psql-chart
      kubectl delete ns postgres
      
      helm -n milvus delete milvus-chart
      kubectl delete ns milvus
      ```

## Resources:

- [Milvus instalation](https://milvus.io/docs/install_cluster-helm.md)
- [Milvus helm chart](https://github.com/zilliztech/milvus-helm/tree/master/charts/milvus)
- [Postgres helm chart](https://github.com/bitnami/charts/tree/main/bitnami/postgresql)
