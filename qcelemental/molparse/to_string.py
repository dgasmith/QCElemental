import collections

import numpy as np

from ..physical_constants import constants


def to_string(molrec, dtype, units='Angstrom', atom_format=None, ghost_format=None, width=17, prec=12):
    """Format a string representation of QM molecule.

    Parameters
    ----------
    molrec : dict
        Psi4 json Molecule spec.
    dtype : {'xyz', 'cfour', 'nwchem'}
        Overall string format. Note that it's possible to request variations
        that don't fit the dtype spec so may not be re-readable (e.g., ghost
        and mass in nucleus label with ``'xyz'``).
        'cfour' forces nucleus label, ignoring atom_format, ghost_format
    units : str, optional
        Units in which to write string. Usually ``Angstrom`` or ``Bohr``
        but may be any length unit.  There is not an option to write in
        intrinsic/input units. For ``dtype='xyz', units='Bohr'`` where the
        format doesn't have a slot to specify units, "au" is added so that
        readable as ``dtype='xyz+'``.
    atom_format : str, optional
        General format is ``'{elem}'``. A format string that may contain fields
        'elea' (-1 will be ''), 'elez', 'elem', 'mass', 'elbl' in any
        arrangement. For example, if a format naturally uses element symbol
        and you want atomic number instead with mass info, too, pass
        ``'{elez}@{mass}'``. See `ghost_format` for handling field 'real'.
    ghost_format : str, optional
        General format is ``'@{elem}'``. Like `atom_format`, but this formatter
        is used when `real=False`. To suppress ghost atoms, use `ghost_format=''`.
    width : int, optional
        Field width for formatting coordinate float.
    prec : int, optional
        Number of decimal places for formatting coordinate float.

    Returns
    -------
    str
        String representation of the molecule.

    """

    #funits, fiutau = process_units(molrec)
    #molrec = self.to_dict(force_units=units, np_out=True)

    #if molrec['units'] == 'Angstrom' and units == 'Bohr' and 'input_units_to_au' in molrec:
    #    factor = molrec['input_units_to_au']
    if molrec['units'] == 'Angstrom' and units.capitalize() == 'Angstrom':
        factor = 1.
    elif molrec['units'] == 'Angstrom' and units.capitalize() == 'Bohr':
        if 'input_units_to_au' in molrec:
            factor = molrec['input_units_to_au']
        else:
            factor = 1. / constants.bohr2angstroms
    elif molrec['units'] == 'Bohr' and units.capitalize() == 'Angstrom':
        factor = constants.bohr2angstroms
    elif molrec['units'] == 'Bohr' and units.capitalize() == 'Bohr':
        factor = 1.
    else:
        factor = constants.conversion_factor(molrec['units'], units)
    geom = np.array(molrec['geom']).reshape((-1, 3)) * factor

    name = molrec.get('name', formula_generator(molrec['elem']))
    tagline = """auto-generated by QCElemental from molecule {}""".format(name)

    if dtype == 'xyz':
        # Notes
        # * if units not in umap (e.g., nm), can't be read back in by from_string()

        atom_format = '{elem}' if atom_format is None else atom_format
        ghost_format = '@{elem}' if ghost_format is None else ghost_format
        umap = {'bohr': 'au', 'angstrom': ''}

        atoms = _atoms_formatter(molrec, geom, atom_format, ghost_format, width, prec, 2)
        nat = len(atoms)

        first_line = """{} {}""".format(str(nat), umap.get(units.lower(), units.lower()))
        smol = [first_line.rstrip(), name]
        smol.extend(atoms)

    elif dtype == 'cfour':
        # Notes
        # * losing identity of ghost atoms. picked up again in basis formatting
        # * casting 'molecular_charge' to int
        # * no spaces at the beginning of 1st/comment line is important

        atom_format = '{elem}'
        ghost_format = 'GH'
        # TODO handle which units valid

        atoms = _atoms_formatter(molrec, geom, atom_format, ghost_format, width, prec, 2)

        smol = [tagline]
        smol.extend(atoms)

    elif dtype == 'nwchem':

        atom_format = '{elem}'
        ghost_format = 'GH'
        # TODO handle which units valid
        umap = {'bohr': 'bohr', 'angstrom': 'angstroms', 'nm': 'nanometers', 'pm': 'picometers'}

        atoms = _atoms_formatter(molrec, geom, atom_format, ghost_format, width, prec, 2)

        first_line = f"""geometry units {umap.get(units.lower())}"""
        # noautosym nocenter  # no reorienting input geometry
        fix_symm = molrec.get('fix_symmetry', None)
        symm_line = ''
        if fix_symm:
            symm_line = 'symmetry {}'.format(fix_symm)  # not quite what Jiyoung had
        last_line = """end"""
        smol = [first_line]
        smol.extend(atoms)
        smol.append(symm_line)
        smol.append(last_line)

    elif dtype == 'gamess':
        # Untested by gamess itself

        atom_format = ' {elem}{elbl} {elez}'
        ghost_format = ' {BQ} -{elez}'

        atoms = _atoms_formatter(molrec, geom, atom_format, ghost_format, width, prec, 2)

        first_line = """ $data"""
        second_line = f""" {tagline}"""
        third_line = """ C1"""
        last_line = """ $end"""

        smol = [first_line, second_line, third_line]
        smol.extend(atoms)
        smol.append(last_line)

    elif dtype == 'terachem':

        atom_format = '{elem}'
        ghost_format = 'X{elem}'
        umap = {'bohr': '', 'angstrom': ''}

        atoms = _atoms_formatter(molrec, geom, atom_format, ghost_format, width, prec, 2)

        first_line = f"""{len(atoms)} {umap[units.lower()]}"""  # units only validating, not printing
        smol = [first_line.rstrip(), name]
        smol.extend(atoms)

    else:
        raise ValueError(f'`to_string(dtype={dtype})` unrecognized')

    return '\n'.join(smol) + '\n'


def _atoms_formatter(molrec, geom, atom_format, ghost_format, width, prec, sp):
    """Format a list of strings, one per atom from `molrec`."""

    #geom = molrec['geom'].reshape((-1, 3))
    nat = geom.shape[0]
    fxyz = """{:>{width}.{prec}f}"""
    sp = """{:{sp}}""".format('', sp=sp)

    atoms = []
    for iat in range(nat):
        atom = []
        atominfo = {
            'elea': '' if molrec['elea'][iat] == -1 else molrec['elea'][iat],
            'elez': molrec['elez'][iat],
            'elem': molrec['elem'][iat],
            'mass': molrec['mass'][iat],
            'elbl': molrec['elbl'][iat]
        }

        if molrec['real'][iat]:
            nuc = """{:{width}}""".format(atom_format.format(**atominfo), width=width)
            atom.append(nuc)
        else:
            if ghost_format == '':
                continue
            else:
                nuc = """{:{width}}""".format(ghost_format.format(**atominfo), width=width)
                atom.append(nuc)

        atom.extend([fxyz.format(x, width=width, prec=prec) for x in geom[iat]])
        atoms.append(sp.join(atom))

    return atoms


def formula_generator(elem):
    """Return simple chemical formula from element list `elem`.

    >>> formula_generator(['C', 'Ca', 'O', 'O', 'Ag']
    AgCCaO2

    """
    counted = collections.Counter(elem)
    return ''.join((el if cnt == 1 else (el + str(cnt))) for el, cnt in sorted(counted.items()))
