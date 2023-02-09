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

## [Commands](docs/commands.md)

[Link](docs/commands.md)

## Install

`pip install blazectl`

## Build

`poetry build`

## Publish

`poetry publish`