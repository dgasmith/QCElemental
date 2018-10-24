# QCElemental

[![Build Status](https://travis-ci.org/MolSSI/QCElemental.svg?branch=master)](https://travis-ci.org/MolSSI/QCElemental)
[![codecov](https://codecov.io/gh/MolSSI/QCElemental/branch/master/graph/badge.svg)](https://codecov.io/gh/MolSSI/QCElemental)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/MolSSI/QCElemental.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/MolSSI/QCElemental/context:python)
[![Documentation Status](https://readthedocs.org/projects/qcelemental/badge/?version=latest)](https://qcelemental.readthedocs.io/en/latest/?badge=latest)
[![Chat on Slack](https://img.shields.io/badge/chat-on_slack-green.svg?longCache=true&style=flat&logo=slack)](https://join.slack.com/t/qcdb/shared_invite/enQtNDIzNTQ2OTExODk0LWM3OTgxN2ExYTlkMTlkZjA0OTExZDlmNGRlY2M4NWJlNDlkZGQyYWUxOTJmMzc3M2VlYzZjMjgxMDRkYzFmOTE)

QCElemental is a resource module for quantum chemistry containing physical
constants and periodic table data from NIST and molecule handlers.

Periodic Table and Physical Constants data are pulled from NIST srd144 and
srd121, respectively; [details](nist_data/README.md) in a renewable manner
(class around NIST-published JSON file).

This project also contains a generator, validator, and translator for [Molecule
QCSchema](https://molssi-qc-schema.readthedocs.io/en/latest/auto_topology.html).

### Periodic Table

A variety of periodic table quantities are available using virtually any alias:

```python
>>> import qcelemental as qcel
>>> qcel.periodictable.to_E('KRYPTON')
'Kr'
>>> qcel.periodictable.to_element(36)
'Krypton'
>>> qcel.periodictable.to_Z('kr84')
36
>>> qcel.periodictable.to_A('Kr')
84
>>> qcel.periodictable.to_A('D')
2
>>> qcel.periodictable.to_mass('kr', return_decimal=True)
Decimal('83.9114977282')
>>> qcel.periodictable.to_mass('kr84')
83.9114977282
>>> qcel.periodictable.to_mass('Kr86')
85.9106106269
```

### Physical Constants

Physical constants can be aquired directly from the [NIST CODATA](https://physics.nist.gov/cuu/Constants/Table/allascii.txt):

```python
>>> import qcelemental as qcel
>>> qcel.constants.Hartree_energy_in_eV
27.21138602
>>> qcel.constants.get('hartree ENERGY in ev')
27.21138602
>>> pc = qcel.constants.get('hartree ENERGY in ev', return_tuple=True)
>>> pc.lbl
'Hartree energy in eV'
>>> pc.data
Decimal('27.21138602')
>>> pc.units
'eV'
>>> pc.comment
'uncertainty=0.000 000 17'
```

Alternatively, with the use of the Pint unit conversion package arbitrary
conversion factors can be obtained:

```python
>>> qcel.constants.conversion_factor("bohr", "miles")
3.2881547429884475e-14
```

