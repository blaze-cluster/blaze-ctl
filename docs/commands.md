# `blazectl`

**Usage**:

```console
$ blazectl [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `cluster`
* `job`
* `namespace`
* `workers-group`

## `blazectl cluster`

**Usage**:

```console
$ blazectl cluster [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`
* `delete`
* `restart`
* `start`
* `stop`
* `terminate`

### `blazectl cluster create`

**Usage**:

```console
$ blazectl cluster create [OPTIONS]
```

**Options**:

* `--name TEXT`: [required]
* `-n, --namespace TEXT`: [required]
* `--head-node TEXT`: [required]
* `--default-workers-node TEXT`: [required]
* `--default-workers-count INTEGER`: [default: 0]
* `--default-workers-gpu / --no-default-workers-gpu`: [default: no-default-workers-gpu]
* `--help`: Show this message and exit.

### `blazectl cluster delete`

**Usage**:

```console
$ blazectl cluster delete [OPTIONS]
```

**Options**:

* `--name TEXT`: [required]
* `-n, --namespace TEXT`: [required]
* `--help`: Show this message and exit.

### `blazectl cluster restart`

**Usage**:

```console
$ blazectl cluster restart [OPTIONS]
```

**Options**:

* `--name TEXT`: [required]
* `-n, --namespace TEXT`: [required]
* `--restart-head / --no-restart-head`: [default: no-restart-head]
* `--help`: Show this message and exit.

### `blazectl cluster start`

**Usage**:

```console
$ blazectl cluster start [OPTIONS]
```

**Options**:

* `--name TEXT`: [required]
* `-n, --namespace TEXT`: [required]
* `--help`: Show this message and exit.

### `blazectl cluster stop`

**Usage**:

```console
$ blazectl cluster stop [OPTIONS]
```

**Options**:

* `--name TEXT`: [required]
* `-n, --namespace TEXT`: [required]
* `--help`: Show this message and exit.

### `blazectl cluster terminate`

**Usage**:

```console
$ blazectl cluster terminate [OPTIONS]
```

**Options**:

* `--name TEXT`: [required]
* `-n, --namespace TEXT`: [required]
* `--help`: Show this message and exit.

## `blazectl job`

**Usage**:

```console
$ blazectl job [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `download-logs`
* `run`
* `status`
* `stop`
* `tail-logs`
* `wait-until-job-end`

### `blazectl job download-logs`

**Usage**:

```console
$ blazectl job download-logs [OPTIONS]
```

**Options**:

* `-c, --cluster-name TEXT`: [required]
* `-n, --cluster-ns TEXT`: [required]
* `-j, --job-id TEXT`: [required]
* `--help`: Show this message and exit.

### `blazectl job run`

**Usage**:

```console
$ blazectl job run [OPTIONS]
```

**Options**:

* `-c, --cluster-name TEXT`: [required]
* `-n, --cluster-ns TEXT`: [required]
* `-e, --entrypoint TEXT`: [required]
* `--working-dir TEXT`: [default: ./]
* `--pip TEXT`
* `--on-job-run [stop-and-start|terminate-then-start|nothing]`: [default: ClusterStateOnJobRun.NOTHING]
* `--on-job-success [stop|terminate|nothing]`: [default: ClusterStateOnJobEnd.NOTHING]
* `--on-job-failure [stop|terminate|nothing]`: [default: ClusterStateOnJobEnd.NOTHING]
* `--help`: Show this message and exit.

### `blazectl job status`

**Usage**:

```console
$ blazectl job status [OPTIONS]
```

**Options**:

* `-c, --cluster-name TEXT`: [required]
* `-n, --cluster-ns TEXT`: [required]
* `-j, --job-id TEXT`: [required]
* `--help`: Show this message and exit.

### `blazectl job stop`

**Usage**:

```console
$ blazectl job stop [OPTIONS]
```

**Options**:

* `-c, --cluster-name TEXT`: [required]
* `-n, --cluster-ns TEXT`: [required]
* `-j, --job-id TEXT`: [required]
* `--on-job-stop [stop|terminate|nothing]`: [default: ClusterStateOnJobEnd.NOTHING]
* `--on-job-failure [stop|terminate|nothing]`: [default: ClusterStateOnJobEnd.NOTHING]
* `--help`: Show this message and exit.

### `blazectl job tail-logs`

**Usage**:

```console
$ blazectl job tail-logs [OPTIONS]
```

**Options**:

* `-c, --cluster-name TEXT`: [required]
* `-n, --cluster-ns TEXT`: [required]
* `-j, --job-id TEXT`: [required]
* `--help`: Show this message and exit.

### `blazectl job wait-until-job-end`

**Usage**:

```console
$ blazectl job wait-until-job-end [OPTIONS]
```

**Options**:

* `-c, --cluster-name TEXT`: [required]
* `-n, --cluster-ns TEXT`: [required]
* `-j, --job-id TEXT`: [required]
* `--timeout-seconds TEXT`: [default: 86400]
* `--on-job-success [stop|terminate|nothing]`: [default: ClusterStateOnJobEnd.NOTHING]
* `--on-job-failure [stop|terminate|nothing]`: [default: ClusterStateOnJobEnd.NOTHING]
* `--help`: Show this message and exit.

## `blazectl namespace`

**Usage**:

```console
$ blazectl namespace [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `add-fsx-volume`
* `create`
* `delete`
* `delete-fsx-volume`
* `set-gpu`
* `set-sa-policy`

### `blazectl namespace add-fsx-volume`

**Usage**:

```console
$ blazectl namespace add-fsx-volume [OPTIONS]
```

**Options**:

* `-n, --namespace TEXT`: [required]
* `--volume-name TEXT`: [required]
* `--volume-size-in-gb INTEGER`: [required]
* `--volume-handle TEXT`: [required]
* `--volume-dns TEXT`: [required]
* `--volume-mount-name TEXT`: [required]
* `--help`: Show this message and exit.

### `blazectl namespace create`

**Usage**:

```console
$ blazectl namespace create [OPTIONS]
```

**Options**:

* `-n, --namespace TEXT`: [required]
* `-eks, --eks-cluster TEXT`: [required]
* `--volume-size-in-gb INTEGER`: [default: 120]
* `--sa-policy-arn TEXT`
* `--gpu-enabled / --no-gpu-enabled`: [default: no-gpu-enabled]
* `--help`: Show this message and exit.

### `blazectl namespace delete`

**Usage**:

```console
$ blazectl namespace delete [OPTIONS]
```

**Options**:

* `-n, --namespace TEXT`: [required]
* `--help`: Show this message and exit.

### `blazectl namespace delete-fsx-volume`

**Usage**:

```console
$ blazectl namespace delete-fsx-volume [OPTIONS]
```

**Options**:

* `-n, --namespace TEXT`: [required]
* `--volume-name TEXT`: [required]
* `--help`: Show this message and exit.

### `blazectl namespace set-gpu`

**Usage**:

```console
$ blazectl namespace set-gpu [OPTIONS]
```

**Options**:

* `-n, --namespace TEXT`: [required]
* `--enabled / --no-enabled`: [required]
* `--help`: Show this message and exit.

### `blazectl namespace set-sa-policy`

**Usage**:

```console
$ blazectl namespace set-sa-policy [OPTIONS]
```

**Options**:

* `-n, --namespace TEXT`: [required]
* `--arn TEXT`: [required]
* `--help`: Show this message and exit.

## `blazectl workers-group`

**Usage**:

```console
$ blazectl workers-group [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `add`
* `delete`
* `set-replicas`
* `update`

### `blazectl workers-group add`

**Usage**:

```console
$ blazectl workers-group add [OPTIONS]
```

**Options**:

* `--name TEXT`: [required]
* `-c, --cluster TEXT`: [required]
* `-n, --namespace TEXT`: [required]
* `--instance-type TEXT`: [required]
* `--count INTEGER`: [default: 0]
* `--gpu / --no-gpu`: [default: no-gpu]
* `--help`: Show this message and exit.

### `blazectl workers-group delete`

**Usage**:

```console
$ blazectl workers-group delete [OPTIONS]
```

**Options**:

* `--name TEXT`: [required]
* `-c, --cluster TEXT`: [required]
* `-n, --namespace TEXT`: [required]
* `--help`: Show this message and exit.

### `blazectl workers-group set-replicas`

**Usage**:

```console
$ blazectl workers-group set-replicas [OPTIONS]
```

**Options**:

* `--name TEXT`: [required]
* `-c, --cluster TEXT`: [required]
* `-n, --namespace TEXT`: [required]
* `--count INTEGER`: [required]
* `--help`: Show this message and exit.

### `blazectl workers-group update`

**Usage**:

```console
$ blazectl workers-group update [OPTIONS]
```

**Options**:

* `--name TEXT`: [required]
* `-c, --cluster TEXT`: [required]
* `-n, --namespace TEXT`: [required]
* `--instance-type TEXT`
* `--count INTEGER`
* `--gpu / --no-gpu`
* `--help`: Show this message and exit.

