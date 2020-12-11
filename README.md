# updatehub agent SDK for Python

[![CI](https://github.com/UpdateHub/agent-sdk-python/workflows/CI/badge.svg?branch=master)](https://github.com/UpdateHub/agent-sdk-python/actions?query=branch%3Amaster)

The updatehub agent SDK for Python provides a set of classes to enable programs
written in Python to interact with the updatehub agent.

## Documentation

You can read the up-to-date reference using `pydoc`.

## Examples

[examples/state_change_listener.py](examples/state_change_listener.py): A simple
state change listener that blocks updates from being downloaded.

## Building

The project uses setuptools, so it should be straightforward to install it on
your environment:
```
python setup.py install
```

## Testing

For now only code lint is being checked. Install tox (`pip install tox`) and run
it to check for any errors.

## Compatibility

* Python 3.5
* Python 3.6
* Python 3.7
* Python 3.8
