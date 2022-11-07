# `blazectl namespace`

**Usage**:

```console
$ blazectl namespace [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `add-fsx-volume`
* `create`
* `delete`
* `delete-fsx-volume`
* `set-gpu`
* `set-sa-policy`

## `blazectl namespace add-fsx-volume`

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

## `blazectl namespace create`

**Usage**:

```console
$ blazectl namespace create [OPTIONS]
```

**Options**:

* `-n, --namespace TEXT`: [required]
* `-eks, --eks-cluster TEXT`: [required]
* `--volume-size-in-gb INTEGER`: [default: 120]
* `--sa-policy-arn TEXT`
* `--gpu-enabled / --no-gpu-enabled`: [default: False]
* `--help`: Show this message and exit.

## `blazectl namespace delete`

**Usage**:

```console
$ blazectl namespace delete [OPTIONS]
```

**Options**:

* `-n, --namespace TEXT`: [required]
* `--help`: Show this message and exit.

## `blazectl namespace delete-fsx-volume`

**Usage**:

```console
$ blazectl namespace delete-fsx-volume [OPTIONS]
```

**Options**:

* `-n, --namespace TEXT`: [required]
* `--volume-name TEXT`: [required]
* `--help`: Show this message and exit.

## `blazectl namespace set-gpu`

**Usage**:

```console
$ blazectl namespace set-gpu [OPTIONS]
```

**Options**:

* `-n, --namespace TEXT`: [required]
* `--enabled / --no-enabled`: [required]
* `--help`: Show this message and exit.

## `blazectl namespace set-sa-policy`

**Usage**:

```console
$ blazectl namespace set-sa-policy [OPTIONS]
```

**Options**:

* `-n, --namespace TEXT`: [required]
* `--arn TEXT`: [required]
* `--help`: Show this message and exit.
