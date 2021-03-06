# rlp-cython

A Python implementation of Recursive Length Prefix encoding (RLP) with a very fast
cython back-end. You can find the original python based RLP [here](https://github.com/ethereum/pyrlp),
the specification of the standard in the
[Ethereum wiki](https://github.com/ethereum/wiki/wiki/RLP) and the
documentation of this package on
[readthedocs](http://pyrlp.readthedocs.org/en/latest/).


### Release setup

For Debian-like systems:
```
apt install pandoc
```

To release a new version:

```sh
make release bump=$$VERSION_PART_TO_BUMP$$
```

#### How to bumpversion

The version format for this repo is `{major}.{minor}.{patch}` for stable, and
`{major}.{minor}.{patch}-{stage}.{devnum}` for unstable (`stage` can be alpha or beta).

To issue the next version in line, specify which part to bump,
like `make release bump=minor` or `make release bump=devnum`.

If you are in a beta version, `make release bump=stage` will switch to a stable.

To issue an unstable version when the current version is stable, specify the
new version explicitly, like `make release bump="--new-version 4.0.0-alpha.1 devnum"`
