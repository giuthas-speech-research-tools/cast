# CAST Development guide

For lack of actual content here (apart from the installation
instructions below), look up the corresponding guide from PATKIT.

## Install CAST for development

Caveat lector! These are untested instructions written from memory.

Basically just use `uv`. Running test runs with 
```shell
uv run cast [command] [args]
```
is not really all that difficult. Or you could install the local repo as a tool
```shell
uv tool install .
```
and just run
```shell
uv tool uprgrade computer-assisted-segmentation-tools --reinstall 
```
when you need to update the installation. Weirdly enough you need to give the
package name when updating, trying to use `.` will not work.