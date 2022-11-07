# `blazectl cluster`

**Usage**:

```console
$ blazectl cluster [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `create`
* `delete`
* `restart`

## `blazectl cluster create`

**Usage**:

```console
$ blazectl cluster create [OPTIONS]
```

**Options**:

* `--name TEXT`: [required]
* `-n, --namespace TEXT`: [required]
* `--head-instance-type TEXT`
* `--default-workers-instance-type TEXT`
* `--default-workers-count INTEGER`: [default: 0]
* `--help`: Show this message and exit.

## `blazectl cluster delete`

**Usage**:

```console
$ blazectl cluster delete [OPTIONS]
```

**Options**:

* `--name TEXT`: [required]
* `-n, --namespace TEXT`: [required]
* `--help`: Show this message and exit.

## `blazectl cluster restart`

**Usage**:

```console
$ blazectl cluster restart [OPTIONS]
```

**Options**:

* `--name TEXT`: [required]
* `-n, --namespace TEXT`: [required]
* `--help`: Show this message and exit.
