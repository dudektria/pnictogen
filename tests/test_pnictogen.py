#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from glob import iglob
import pybel
from nose.tools import assert_equals
from contextlib import contextmanager

from pnictogen import argparser, main, pnictogen, update_data

# Only testing xyz files because I trust Open Babel to handle other file types
example_xyz_files = iglob("examples/*.xyz")
boilerplates = iglob("examples/boilerplates/*")


@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


# TODO: make prettier error messages when runnig tests


def test_argparser():
    for template in boilerplates:
        argv = [template] + list(example_xyz_files)

        parser = argparser()
        parser.parse_args(argv)


def test_main():
    for template in boilerplates:
        main(["-g", template])

        # One at a time
        for xyz_file in example_xyz_files:
            main([template, xyz_file])

        # All at once
        main([template] + list(example_xyz_files))

    # Allow use of template in the parent directory
    with cd("examples/boilerplates"):
        main(["../templates/EDA.ADF.in", "../water_dimer.xyz"])


def test_pnictogen():
    for template in boilerplates:
        template_prefix, extension = os.path.splitext(template)
        for xyz_file in example_xyz_files:
            input_prefix, xyz_file_extension = os.path.splitext(xyz_file)

            mol = pybel.readfile("xyz", xyz_file)
            written_files = pnictogen(mol, input_prefix, template,
                                      extension[1:])

            assert_equals(type(written_files), list)
            for written_file in written_files:
                assert_equals(type(written_file), str)

            written_files2 = pnictogen(mol, input_prefix, template)
            assert_equals(written_files, written_files2)

    # Allow use of template in the parent directory
    with cd("examples/boilerplates"):
        mol = pybel.readfile("xyz", "../water_dimer.xyz")
        written_files = pnictogen(mol, "../water_dimer",
                                  "../templates/EDA.ADF.in", "in")

        assert_equals(written_files, ["../water_dimer_eda.in",
                                      "../water_dimer_frag1.in",
                                      "../water_dimer_frag2.in"])

    mol = pybel.readfile("xyz", "examples/co.xyz")
    written_files = pnictogen(mol, "examples/co",
                              "examples/boilerplates/ORCA.inp", foo="bar")

    assert_equals(written_files, ["examples/co.inp"])


# TODO: create hello world template in a temporary file to test
# render_template() without any molecule.
# def test_render_templates():
#     pass


def test_render_boilerplates():
    water_mol = list(pybel.readfile("xyz", "examples/water.xyz"))[0]

    main(["-g", "examples/boilerplates/ADF.in"])
    main(["examples/boilerplates/ADF.in", "examples/water.xyz"])
    assert_equals(open("examples/water.in").read(), water_mol.write("adf"))

    main(["-g", "examples/boilerplates/GAMESS.inp"])
    main(["examples/boilerplates/GAMESS.inp", "examples/water.xyz"])
    assert_equals(open("examples/water.inp").read(),
                  """ $CONTRL COORD=CART UNITS=ANGS $END

 $DATA
PBE0-D3(BJ)/def2-TZVP @ ORCA 4.0.1.2
C1
O      8.0      0.0584027061    0.0584027059    0.0000000000
H      1.0      1.0096135406   -0.0680162466    0.0000000000
H      1.0     -0.0680162466    1.0096135407    0.0000000000
 $END


""")

    main(["-g", "examples/boilerplates/GAMESSUK.inp"])
    main(["examples/boilerplates/GAMESSUK.inp", "examples/water.xyz"])
    assert_equals(open("examples/water.inp").read(), water_mol.write("gukin"))

    main(["-g", "examples/boilerplates/Gaussian.gjf"])
    main(["examples/boilerplates/Gaussian.gjf", "examples/water.xyz"])
    assert_equals(open("examples/water.gjf").read(),
                  """#Put Keywords Here, check Charge and Multiplicity.

 PBE0-D3(BJ)/def2-TZVP @ ORCA 4.0.1.2

0  1
O          0.05840        0.05840        0.00000
H          1.00961       -0.06802        0.00000
H         -0.06802        1.00961        0.00000

""")

    main(["-g", "examples/boilerplates/Jaguar.in"])
    main(["examples/boilerplates/Jaguar.in", "examples/water.xyz"])
    assert_equals(open("examples/water.in").read(), water_mol.write("jin"))

    main(["-g", "examples/boilerplates/Molpro.inp"])
    main(["examples/boilerplates/Molpro.inp", "examples/water.xyz"])
    assert_equals(open("examples/water.inp").read(), water_mol.write("mp"))

    main(["-g", "examples/boilerplates/MOPAC.mop"])
    main(["examples/boilerplates/MOPAC.mop", "examples/water.xyz"])
    assert_equals(open("examples/water.mop").read(),
                  """CHARGE=0 MS=0.0
PBE0-D3(BJ)/def2-TZVP @ ORCA 4.0.1.2

O   0.05840 1  0.05840 1  0.00000 1
H   1.00961 1 -0.06802 1  0.00000 1
H  -0.06802 1  1.00961 1  0.00000 1
""")

    main(["-g", "examples/boilerplates/MPQC.in"])
    main(["examples/boilerplates/MPQC.in", "examples/water.xyz"])
    assert_equals(open("examples/water.in").read(), water_mol.write("mpqcin"))

    main(["-g", "examples/boilerplates/NWChem.nw"])
    main(["examples/boilerplates/NWChem.nw", "examples/water.xyz"])
    assert_equals(open("examples/water.nw").read(), """start molecule

title PBE0-D3(BJ)/def2-TZVP @ ORCA 4.0.1.2

geometry units angstroms print xyz autosym
O          0.05840        0.05840        0.00000
H          1.00961       -0.06802        0.00000
H         -0.06802        1.00961        0.00000
end
""")

    main(["-g", "examples/boilerplates/ORCA.inp"])
    main(["examples/boilerplates/ORCA.inp", "examples/water.xyz"])
    assert_equals(open("examples/water.inp").read(),
                  """# PBE0-D3(BJ)/def2-TZVP @ ORCA 4.0.1.2
! Opt

* xyz 0 1
O          0.05840        0.05840        0.00000
H          1.00961       -0.06802        0.00000
H         -0.06802        1.00961        0.00000
*
""")

    main(["-g", "examples/boilerplates/Psi.dat"])
    main(["examples/boilerplates/Psi.dat", "examples/water.xyz"])
    assert_equals(open("examples/water.dat").read(),
                  """# PBE0-D3(BJ)/def2-TZVP @ ORCA 4.0.1.2

molecule {
0 1
O          0.05840        0.05840        0.00000
H          1.00961       -0.06802        0.00000
H         -0.06802        1.00961        0.00000
units angstrom
}

optimize('scf')""")

    main(["-g", "examples/boilerplates/QChem.in"])
    main(["examples/boilerplates/QChem.in", "examples/water.xyz"])
    assert_equals(open("examples/water.in").read(), water_mol.write("qcin"))

    main(["-g", "examples/boilerplates/ZINDO.input"])
    main(["examples/boilerplates/ZINDO.input", "examples/water.xyz"])
    assert_equals(open("examples/water.input").read(), water_mol.write("zin"))


def test_update_data():
    mol = pybel.readstring("smi", "[Ag+]")
    assert_equals(mol.charge, 1)
    assert_equals(mol.spin, 1)

    update_data(mol, "spin=2 charge=0")
    assert_equals(mol.charge, 0)
    assert_equals(mol.spin, 2)

    # Keywords in title
    main(["-g", "examples/boilerplates/Gaussian.gjf"])
    main(["examples/boilerplates/Gaussian.gjf", "examples/hydroxide.xyz"])
    assert_equals(open("examples/hydroxide.gjf").read(),
                  """#Put Keywords Here, check Charge and Multiplicity.

 This guy has charge=-1 but its multiplicity spin=2 is incorrect

-1  2
O          0.05840        0.05840        0.00000
H          1.00961       -0.06802        0.00000

""")


def test_example_eda_adf():
    main(["examples/templates/EDA.ADF.in", "examples/water_dimer.xyz"])
    assert_equals(open("examples/water_dimer_eda.in").read(),
                  """TITLE examples/water_dimer.xyz

CHARGE 0  0

Number of atoms
 6

ATOMS Cartesian
O          0.12908       -0.26336        0.64798       f=frag1
H          0.89795        0.28805        0.85518       f=frag1
H          0.10833       -0.20468       -0.33302       f=frag1
O          0.31020        0.07569       -2.07524       f=frag2
H         -0.26065        0.64232       -2.62218       f=frag2
H          0.64083       -0.57862       -2.71449       f=frag2
End

Fragments
 frag1 examples/water_dimer_frag1.t21
 frag2 examples/water_dimer_frag2.t21
End

Basis
End

Geometry
End

""")
    assert_equals(open("examples/water_dimer_frag1.in").read(),
                  """TITLE frag1

CHARGE 0  0

Number of atoms
 3

ATOMS Cartesian
O          0.12908       -0.26336        0.64798
H          0.89795        0.28805        0.85518
H          0.10833       -0.20468       -0.33302
End

Basis
End

Geometry
End

""")
    assert_equals(open("examples/water_dimer_frag2.in").read(),
                  """TITLE frag2

CHARGE 0  0

Number of atoms
 3

ATOMS Cartesian
O          0.31020        0.07569       -2.07524
H         -0.26065        0.64232       -2.62218
H          0.64083       -0.57862       -2.71449
End

Basis
End

Geometry
End

""")


def test_example_fragments_orca():
    main(["examples/templates/fragments.ORCA.inp", "examples/water_dimer.xyz"])
    assert_equals(open("examples/water_dimer.inp").read(),
                  """# examples/water_dimer.xyz
! Opt

* xyz 0 1
O(1)       0.12908       -0.26336        0.64798
H(1)       0.89795        0.28805        0.85518
H(1)       0.10833       -0.20468       -0.33302
O(2)       0.31020        0.07569       -2.07524
H(2)      -0.26065        0.64232       -2.62218
H(2)       0.64083       -0.57862       -2.71449
*
""")
