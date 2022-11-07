# `blazectl workers-group`

**Usage**:

```console
$ blazectl workers-group [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `add`
* `delete`
* `set-replicas`
* `update`

## `blazectl workers-group add`

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
* `--gpu / --no-gpu`: [default: False]
* `--help`: Show this message and exit.

## `blazectl workers-group delete`

**Usage**:

```console
$ blazectl workers-group delete [OPTIONS]
```

**Options**:

* `--name TEXT`: [required]
* `-c, --cluster TEXT`: [required]
* `-n, --namespace TEXT`: [required]
* `--help`: Show this message and exit.

## `blazectl workers-group set-replicas`

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

## `blazectl workers-group update`

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
