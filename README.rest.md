
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


TODO:
- This is to setup the liveness and readiness probes more information can be found here: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
    ```
    livenessProbe:
      httpGet:
        path: /
        port: http
    readinessProbe:
      httpGet:
        path: /
        port: http
    ```

- What does `targetPort: http` mean?


```aiignore

docker-credential-pass-v0.9.3.linux-amd64

wget https://github.com/docker/docker-credential-helpers/releases/download/v0.9.3/docker-credential-pass-v0.9.3.linux-amd64.tar.gz \
    && tar -xf docker-credential-pass-v0.6.0-amd64.tar.gz \
    && chmod +x docker-credential-pass \
    && sudo mv docker-credential-pass /usr/local/bin/


```