# Example API

*This guide will lead you through the technical aspects as well as the usage of our FastAPI, SQLAlchemy, PyTest Implementation*


## Important Files

* [example_com/app.py](./project/example_com/app.py) - Starts the application, in our case with the use of [uvicorn](https://www.uvicorn.org/)
* [example_com/config.py](./project/example_com/config.py) - Application configurations, environment variables, etc.
* [example_com/api/admin/admin_api.py](./project/example_com/api/admin/admin_api.py) - Admin API Logic
* [example_com/api/account/accounts_api.py](./project/example_com/api/account/accounts_api.py) - Accounts API Logic
* [example_com/api/workspaces/projects_api.py](./project/example_com/api/workspaces/projects_api.py) - Projects API Logic
* [example_com/data/db_session.py](./project/example_com/data/db_session.py) - Sets up database connection, creates tables, returns database sessions object
* [example_com/data/account/users.py](./project/example_com/data/account/users.py) - SQLAlchemy Object Mapping Class for User Accounts
* [example_com/data/workspaces/projects.py](./project/example_com/data/workspaces/projects.py) - SQLAlchemy Object Mapping Class for User Projects
* [example_com/infrastructure/jwt_token_auth.py](./project/example_com/infrastructure/jwt_token_auth.py) - Handles the distribution of unique tokens per user to access secure endpoints
* [example_com/infrastructure/redis.py](./project/example_com/infrastructure/redis.py) - Manages redis keys per user, removing old keys when the jwt token changes to keep redis memory db lean
* [example_com/models/project_schema.py](./project/example_com/models/project_schema.py) - Manages schema web responses for Projects API such as creating and updating projects
* [example_com/models/user_schema.py](./project/example_com/models/user_schema.py) - Manages schema web responses for Accounts API
* [example_com/services/project_service.py](./project/example_com/services/project_service.py) - Database querying service for projects, the backbone of our Projects API
* [example_com/services/user_service.py](./project/example_com/services/user_service.py) - Database querying service for users, the backbone of our Accounts API
* [tests/conftest.py](./project/tests/conftest.py) - Configuration for our pytesting that yields a web client for testing the various endpoints
* [tests/test_accounts.py](./project/tests/test_accounts.py) - Tests our Accounts API module by sending requests to each endpoint. Tests for failures and successes


## Pre-setup Notes

**User setup is required!**

1. Before proceeding with deploying this template API, you must create a `settings.json` file. The [settings_template.json](./project/example_com/settings_template.json) is the template you want to use. If this step is not complete, the app *will NOT work*. This file sets up the JWT secret when encoding tokens.

2. I strongly recommend building your own Docker containers, so that you can pull from your own private registry. It's also good practice.

**Build and push your app container**

```bash
docker build -f ./project/Dockerfile -t docker.pkg.github.com/{account}/{repo}/example-api:app ./project
docker push docker.pkg.github.com/{account}/{repo}/example-api:app
```

**Build and push your database container**

```bash
docker build -f ./project/example_com/data/Dockerfile -t docker.pkg.github.com/{account}/{repo}/example-api:db ./project/example_com/data
docker push docker.pkg.github.com/{account}/{repo}/example-api:db
```

When deploying to Kubernetes, the deployment scripts will need to point to your registry in the instructions below.


## Using Docker

Docker is the recommended method to run this application. To run it, install [docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/)

### Setup Instructions

1. Build the Docker Image

```bash
docker-compose build
```

2. Once build is complete, kick off the app and db containers in detached mode (runs in the background):

```bash
docker-compose up -d
```

3. Explore the URL of the SWAGGER-like API Docs: http://localhost:5000/docs

4. When you are done testing, bring down the containers

```bash
docker-compose down
```


### Testing Endpoints using Pytest

**NOTE**: In order to perform Pytests, the web app must be running in a docker container.

To run the pytests, run the following command:

```bash
docker-compose exec example-api python -m pytest
```

### Useful Commands

To rebuild any new changes to the application and push to the containers:

```bash
docker-compose up -d --build
```

---

Check logs on docker containers (call by name):

```bash
docker-compose logs example-api
docker-compose logs example-postgres
```

---

Access PostgreSQL Database:

```bash
docker-compose exec example-postgres psql -U postgres
```

## Using Kubernetes

To run this stack on Kubernetes, you'll need a couple of things. The benefits are container orchestration, granular control over them. Orchestration helps with cross-server communication, horizontal scaling, service discovery, load balancing, security/TLS, **zero-downtime deployments**, rollbacks, logging, and monitoring.

To run this deployment, you'll need the following: 

- [Minikube](https://minikube.sigs.k8s.io/docs/), which will allow you to run a Kubernetes cluster locally. 
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads) to run Minikube in
- [Kubectl](https://kubernetes.io/docs/reference/kubectl/kubectl/) to deploy and manage apps on Kubernetes


### Getting started with Kubernetes

1. Starting the Minikube Dashboard

```bash
minikube config set driver virtualbox
minikube start
minikube dashboard
```

**NOTE**: When launching the dashboard, it will run in the foreground. To break out of the dashboard, hit CTRL+c.

You can also run it in the background: `minikube dashboard &`

2. Create your `secrets.yml` file in the [kubernetes](./kubernetes) directory. There is a template that you can copy to get the right formatting: `secrets-template.yml`. Each field that has a "secret", needs to be hashed against the base64 encoder. When hashed, it just needs to be entered in the appropriate field. Example below.

```
echo -n "username" | base64
echo -n "password" | base64
```

**NOTE**: Do not forget the `-n` argument for echo to remove newline characters. Failure to do so will cause frustrations.

For the dockerconfigjson, you will need to hash the following, with the appropriate hash provided by GitHub. [Instructions](https://lionelmace.github.io/iks-lab/gitlab-registry.html) on to deploy a token for access to your GitHub. 

**NOTE**: The instructions above are for GitLab, but work the same as GitHub. The only thing you need to change is the registry location which is docker.pkg.github.com.

```
{
    "auths": {
        "docker.pkg.github.com": {
            "auth": "hashprovidedbygithub"
        }
    }
}
```

What you can do is copy the above into a file `.dockerconfigjson` in the Kubernetes directory and then run the following command to hash it with the base64 encoder:


```bash
cat .dockerconfigjson | base64
```

This encode string can then be pasted into the dockerconfigjson in your `secrets.yml`.

**NOTE**: Kubernetes automatically decodes your hashes and reads them. You should NEVER push your secrets YAML into your code base, nor your .dockerconfigjson. Anyone who has access to the dashboard will be able to read all of this plaintext however. Which is where Hashicorp Vault could assist in secure exchanging of secrets.


3. Push the Secrets object to your Kubernetes Cluster.

```bash
kubectl create -f ./kubernetes/secrets.yml
```

4. Push the ServiceAccount, Services, Deployments objects into your Kubernetes Cluster.

```bash
kubectl create -f ./kubernetes/service-account.yml
kubectl create -f ./kubernetes/postgres-service.yml
kubectl create -f ./kubernetes/postgres-deployment.yml
kubectl create -f ./kubernetes/fastapi-service.yml
kubectl create -f ./kubernetes/fastapi-deployment.yml
```

5. Push the Ingress object into your Kubernetes Cluster to access it, without this step, your cluster is not accessible from the outside (including your host machine).

```bash
minikube addons enable ingress
kubectl delete -A ValidatingWebhookConfiguration ingress-nginx-admission
kubectl create -f ./kubernetes/minikube-ingress.yml
```

6. Update */etc/hosts* file to create a quick DNS entry.

```bash
echo "$(minikube ip) example.api" | sudo tee -a /etc/hosts
```

7. Now, explore to the API!

Go to http://example.api/docs


8. Once done, stop and delete Minikube!

```bash
minikube stop; minikube delete
```

### Useful Commands

Get Kubernetes Deployments and Pods

```bash
kubectl get deployments
kubectl get pods
```

---

Check Logs of Pod

```bash
kubectl logs pod-name-here
```

---

Access the PostgreSQL Database

```bash
kubectl exec pod-name-here --stdin --tty psql -U postgres
```


## Local Usage 

*If Docker or Kubernetes is not an option, running on your local machine should work. This is not the recommended approach*

### Install requirements

To install requirements, create a python environment and install packages (this should be done on the root of the project):

```bash
python3 -m venv venv
source ./venv/bin/active
pip install -r ./project/requirements.txt
```

### Starting the API

To run the app locally, from the project root in terminal, run the following command:

```bash
uvicorn example_com.app:app --reload --workers 1 --host 127.0.0.1 --port 5000 
```

**NOTE**: The database will be created, as well as the tables. However, in order to populate them with some data, scripts will be provided to work with dummy data for testing purposes. Otherwise, manually creation will be needed.

### Testing Endpoints using Pytest (Locally)

Tests are stored in [tests](./project/tests) directory. There is a [conftest](./project/tests/conftest.py) file that should **never** be renamed otherwise pytest will not recognize it as a configuration file.

Anything python file that starts with the prefix "test", will be tested by pytest. As well as any function that starts with the same prefix.

Pytest is configured to test for bad input as well as good input to test the responses for accuracy.

To run pytest, run the following command from project root on your terminal:

```bash
pytest
pytest --no-header -v
```


### Helpful References

- https://minikube.sigs.k8s.io/docs/handbook/controls/
- https://testdriven.io/blog/running-flask-on-kubernetes/


## Testing the API

To interact with the API, use [Postman](https://www.postman.com/) or the [API docs](http://localhost:5000/docs) (after the application has been already started). Also, [httpie](https://httpie.io/) is rather useful.

### API Endpoints

**NOTE**: *Secure endpoints require a JWT Token*

| Endpoint                         | HTTP Method | Category  | Secure | Result                           |
|:---------------------------------|:-----------:|:---------:|:------:|:---------------------------------|
| /api/account                     | GET         | Account   | Yes    | Get account information          |
| /api/account/register            | POST        | Account   | No     | Register a user account          |
| /api/token                       | POST        | Account   | No     | Login and get a unique JWT Token |
| /api/account/{username}          | PUT         | Account   | Yes    | Update user account information  |
| /api/account/{username}/security | PUT         | Account   | Yes    | Update user account password     |
| /api/account/{username}          | DELETE      | Account   | Yes    | Delete user account              |
| /api/admin/settings              | GET         | Admin     | Yes    | See configuration settings       |
| /api/workspaces/projects         | GET         | Projects  | Yes    | Get all projects data            |
| /api/workspaces/projects/{id}    | GET         | Projects  | Yes    | Get a specific project data      |
| /api/workspaces/projects/new     | POST        | Projects  | Yes    | Create a new project             |
| /api/workspaces/projects/{id}    | PUT         | Projects  | Yes    | Update project information       |
| /api/workspaces/projects/{id}    | DELETE      | Projects  | Yes    | Delete a project                 |

