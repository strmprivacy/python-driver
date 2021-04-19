# Releasing to PyPi and Test PyPi

In the `Makefile`, there are two commands:
- `make release`: release to prod PyPi
- `make release-test`: release to test PyPi

When running either commands, you're prompted for a username and password. When using an API token, fill out the following:
- `username` = `__token__` (no, this is not a placeholder, the username literally is `__token__`)
- `password` = `<api_token>` (including `pypi-` part)
