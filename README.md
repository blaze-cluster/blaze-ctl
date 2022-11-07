# blaze-ctl

Controller to manage blaze cluster in cloud (aws) environment

## Concepts

### Namespace

Blaze clusters are created in a namespace, where a namespace defines and manges associated resources, such as -

* EKS Cluster
* Provisioner
* Block Device
* FSX Volumes
* Service Account

Before we can create a cluster, we need to have a namespace and permission to manage cluster in that namespace.

Each namespace has two group of users -

* `blaze-user`: they can create / delete cluster and see pod and svc status
* `blaze-admin`: they can additionally manage FSX Volumes, service accounts, gpu support

## Commands

### Namespace

#### Create Namespace

```
blazectl namespace create
```

#### Delete Namespace

```
blazectl namespace delete
```

#### Add blaze-user

```
blazectl user blaze-user add
```

#### Delete blaze-user

```
blazectl user blaze-user delete
```

#### Add blaze-admin

```
blazectl user blaze-admin add
```

#### Delete blaze-admin

```
blazectl user blaze-admin delete
```

### Cluster

#### Create

```
blazectl cluster create
```

#### Delete

```
blazectl cluster delete
```

#### Restart

```
blazectl cluster restart
```

## Prerequisites

### On MacOS

```
brew install pipx
pipx ensurepath
```

## Install