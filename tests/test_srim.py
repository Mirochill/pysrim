import pytest

from srim.srim import TRIM, SR, TRIMSettings
from srim.core.target import Target
from srim.core.layer import Layer
from srim.core.ion import Ion

TESTDATA_DIRECTORY = 'test_files'

@pytest.mark.parametrize('ranges,sputtered', [(0, 0), (0, 1), (1, 0), (1, 1)])
def test_trim_sputtered_output_independent_of_ranges(tmp_path, monkeypatch, ranges, sputtered):
    ion = Ion('Ni', 1.0e6)
    target = Target([Layer.from_formula('Ni', 8.9, 1000.0)])
    trim = TRIM(target, ion, ranges=ranges, sputtered=sputtered)

    assert trim.settings.ranges == ranges
    assert trim.settings.sputtered == sputtered

    monkeypatch.chdir(tmp_path)
    trim._write_input_files()
    lines = (tmp_path / 'TRIM.IN').read_bytes().decode('utf-8').splitlines()
    header_index = next(i for i, line in enumerate(lines) if line.startswith('Diskfiles'))
    assert lines[header_index + 1].split() == [str(ranges), '0', '0', str(sputtered), '0', '0']


def test_trim_sputtered_default():
    assert TRIMSettings().sputtered == 0


@pytest.mark.parametrize('sputtered', [-1, 2])
def test_trim_sputtered_invalid(sputtered):
    with pytest.raises(ValueError):
        TRIMSettings(sputtered=sputtered)


def test_simple_trim_init():
    ion = Ion('Ni', 1.0e6)

    layer = Layer.from_formula('Ni', 8.9, 1000.0)
    target = Target([layer])

    trim = TRIM(target, ion)


def test_simple_srim_init():
    # Construct a Nickel ion
    ion = Ion('Xe', energy=1.2e9)

    # Construct a layer of nick 20um thick with a displacement energy of 30 eV
    layer = Layer({
        'Si': {
            'stoich': 0.5,
            'E_d': 35.0, # Displacement Energy
            'lattice': 0.0,
            'surface': 3.0
        },
        'C': {
            'stoich': 0.5,
            'E_d': 20.0, # Displacement Energy
            'lattice': 0.0,
            'surface': 3.0
        }
    }, density=3.21, width=10000.0)

    target = Target([layer])

    srim = SR(layer, ion, output_type=5)

    # resulting file should be equal to
    # test_files/SRIM/SR_OUTPUT.txt
