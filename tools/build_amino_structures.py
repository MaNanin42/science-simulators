"""Rebuild the atlas's offline vector drawings with Python and RDKit."""
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from rdkit import Chem
from rdkit.Chem import rdDepictor, rdMolDescriptors
from rdkit.Chem.Draw import rdMolDraw2D

GUIDE = Path(__file__).resolve().parents[1] / "docs/amino-acid-guide/index.html"
DATA = re.compile(r'(<script id="compounds" type="application/json">)(.*?)(</script>)', re.S)
RING = "CG CD1 CD2 CE1 CE2 CZ"
HYDROCARBON_ION = "pH 7에서 전하가 없습니다. 탄화수소 부분은 물속에서 H⁺를 주고받기 어렵습니다."
BRANCH_WATER = "소수성입니다. 가지 달린 탄화수소는 물과 수소 결합을 만들기 어렵습니다."
RING_WATER = "고리의 탄소 부분은 소수성입니다. 물과 수소 결합을 만들기 어렵습니다."
ALCOHOL = ("친수성입니다. –OH의 산소는 물과 수소 결합을 주고받습니다.", "pH 7에서는 거의 모두 –OH로 존재합니다. H⁺를 쉽게 잃지 않아 전하가 없습니다.")
AMIDE = ("친수성입니다. C=O의 산소는 물에서 수소 결합을 받고, N–H는 물에 수소 결합을 줍니다.", "pH 7에서는 전하가 없습니다. 질소의 비공유 전자쌍이 C=O 쪽으로 퍼져 있어 H⁺를 받기 어렵습니다.")
ACID = ("친수성이 큽니다. –COO⁻의 음전하가 물 분자의 부분 양전하를 띤 수소를 끌어당깁니다.", "pH 7에서는 대부분 H⁺를 잃은 –COO⁻(−1)입니다. 산성도가 높아지면 –COOH(0)의 비율이 커집니다.")
SIDE_GROUPS = {
    "G": [("곁사슬 H", "HA", "곁사슬이 작은 수소 하나여서 소수성 효과도 작습니다. 이 수소는 물과 일반적인 수소 결합을 만들지 않습니다.", "pH 7에서 전하가 없습니다. 탄소에 붙은 이 수소는 물속에서 H⁺로 쉽게 떨어지지 않습니다.")],
    "A": [("메틸기", "CB", "소수성입니다. –CH₃는 비극성이어서 물과 수소 결합을 만들기 어렵습니다.", HYDROCARBON_ION)],
    "V": [("분지형 곁사슬", "CB CG1 CG2", BRANCH_WATER, HYDROCARBON_ION)],
    "I": [("분지형 곁사슬", "CB CG1 CG2 CD1", BRANCH_WATER, HYDROCARBON_ION)],
    "L": [("분지형 곁사슬", "CB CG CD1 CD2", BRANCH_WATER, HYDROCARBON_ION)],
    "M": [("싸이오에터", "CG SD CE", "곁사슬 전체는 소수성이 우세합니다. 황은 물과 약하게 상호작용하지만 양쪽 탄화수소 부분은 비극성입니다.", "pH 7에서 전하가 없습니다. 황 양쪽에 탄소가 붙어 있어 –SH처럼 내놓을 수소가 없습니다.")],
    "F": [("페닐기", RING, RING_WATER, HYDROCARBON_ION)],
    "W": [("인돌 고리", "CG CD1 CD2 NE1 CE2 CE3 CZ2 CZ3 CH2", "큰 방향족 고리는 소수성이 우세하지만, 고리의 N–H는 물의 산소에 수소 결합을 줄 수 있습니다.", "pH 7에서는 거의 모두 중성입니다. 질소의 비공유 전자쌍이 방향족 고리에 참여해 H⁺를 받기 어렵습니다.")],
    "P": [("고리형 곁사슬", "N CA CB CG CD", "고리의 –CH₂– 부분은 소수성입니다. 같은 고리에 있는 α-아미노기의 질소는 양전하를 띠어 물과 잘 상호작용합니다.", "pH 7에서 곁사슬의 탄화수소 부분은 전하가 없습니다. 고리에 표시된 +1은 α-아미노기의 전하입니다.")],
    "S": [("하이드록실기", "CB OG", *ALCOHOL)],
    "T": [("하이드록실기", "CB OG1", *ALCOHOL)],
    "C": [("싸이올기", "CB SG", "–SH는 약한 극성을 띱니다. 중성 –SH는 세린의 –OH보다 물과 수소 결합하는 힘이 약하고, –S⁻가 되면 물과 더 강하게 상호작용합니다.", "pH 7에서는 주로 –SH(0)입니다. pH가 8을 넘으며 H⁺를 잃은 –S⁻(−1)의 비율이 커집니다.")],
    "Y": [("페놀성 OH", "CZ OH", "–OH는 친수성입니다. 방향족 고리 끝에서 물과 수소 결합을 주고받습니다.", "pH 7에서는 주로 –OH(0)입니다. pH가 약 10에 이르면 H⁺를 잃은 –O⁻(−1)와 –OH의 비율이 비슷해집니다."), ("방향족 고리", RING, RING_WATER, "pH 7에서 고리의 탄소 부분은 전하가 없습니다. 높은 pH에서 H⁺를 내놓는 자리는 고리에 붙은 페놀성 –OH입니다.")],
    "N": [("아마이드기", "CG OD1 ND2", *AMIDE)],
    "Q": [("아마이드기", "CD OE1 NE2", *AMIDE)],
    "D": [("곁사슬 카복실기", "CG OD1 OD2", *ACID)],
    "E": [("곁사슬 카복실기", "CD OE1 OE2", *ACID)],
    "K": [("곁사슬 아미노기", "CE NZ", "말단 –NH₃⁺는 친수성이 큽니다. 양전하가 물 분자의 부분 음전하를 띤 산소를 끌어당깁니다.", "H⁺를 잘 받아 pH 7에서는 대부분 –NH₃⁺(+1)입니다. pH가 약 10.5에 이르면 –NH₂(0)와 –NH₃⁺의 비율이 비슷해집니다.")],
    "R": [("구아니디늄기", "NE CZ NH1 NH2", "친수성이 큽니다. 세 질소에 분산된 양전하가 물 분자의 산소를 끌어당깁니다.", "pH 7에서는 거의 모두 +1입니다. H⁺가 붙은 형태가 안정해 리신의 곁사슬보다 더 높은 pH까지 양전하를 유지합니다.")],
    "H": [("이미다졸 고리", "CG ND1 CD2 CE1 NE2", "극성인 두 질소가 물과 수소 결합할 수 있습니다. 고리가 양전하를 띠면 물과 더 강하게 상호작용합니다.", "pH 7에서는 주로 중성입니다. pH가 약 6으로 내려가면 H⁺를 받은 형태(+1)와 중성형의 비율이 비슷해집니다.")],
}


def draw_vector(mol, angle):
    draw = rdMolDraw2D.MolDraw2DSVG(-1, -1)
    options = draw.drawOptions()
    options.clearBackground = False
    options.rotate = angle
    options.scalingFactor = 32
    options.padding = 0.085
    options.bondLineWidth = 2.3
    options.updateAtomPalette({7: (0.10, 0.27, 0.58), 8: (0.64, 0.13, 0.10), 16: (0.49, 0.32, 0.04)})
    draw.DrawMolecule(mol)
    draw.FinishDrawing()
    root = ET.fromstring(draw.GetDrawingText())
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    paths = "".join(ET.tostring(el, encoding="unicode").replace(' xmlns="http://www.w3.org/2000/svg"', "") for el in root)
    points = [[round(draw.GetDrawCoords(i).x, 1), round(draw.GetDrawCoords(i).y, 1)] for i in range(mol.GetNumAtoms())]
    return dict(box=root.attrib["viewBox"], paths=paths, points=points)


def structure(code, formula):
    mol = Chem.RWMol(Chem.MolFromSequence(code))
    assert rdMolDescriptors.CalcMolFormula(mol) == formula, (code, formula)
    atoms = {a.GetPDBResidueInfo().GetName().strip(): a.GetIdx() for a in mol.GetAtoms()}

    def ion(name, charge, hydrogens):
        atom = mol.GetAtomWithIdx(atoms[name])
        atom.SetFormalCharge(charge)
        atom.SetNoImplicit(True)
        atom.SetNumExplicitHs(hydrogens)

    ion("N", 1, 2 if code == "P" else 3)
    ion("OXT", -1, 0)
    if code in "DE":
        ion("OD2" if code == "D" else "OE2", -1, 0)
    if code == "K":
        ion("NZ", 1, 3)
    if code == "R":
        imine = next(n for n in ("NH1", "NH2") if mol.GetBondBetweenAtoms(atoms["CZ"], atoms[n]).GetBondType() == Chem.BondType.DOUBLE)
        ion(imine, 1, 2)
    if code == "G":
        atoms["HA"] = mol.AddAtom(Chem.Atom("H"))
        mol.AddBond(atoms["CA"], atoms["HA"], Chem.BondType.SINGLE)
    Chem.SanitizeMol(mol)
    assert Chem.GetFormalCharge(mol) == (1 if code in "KR" else -1 if code in "DE" else 0)
    centers = dict(Chem.FindMolChiralCenters(mol, force=True, includeUnassigned=True, useLegacyImplementation=False))
    expected = {} if code == "G" else {atoms["CA"]: "R" if code == "C" else "S"}
    if code in "IT":
        expected[atoms["CB"]] = "R" if code == "T" else "S"
    assert centers == expected, (code, centers)

    rdDepictor.Compute2DCoords(mol)
    ammonium = "–NH₂⁺–" if code == "P" else "–NH₃⁺"
    backbone = [
        ("α-아미노기", "N", "친수성이 큽니다. 양전하를 띤 질소 주변으로 물 분자의 산소가 끌려옵니다.",
         f"pH 7에서는 대부분 H⁺를 받은 {ammonium}(+1)입니다. pH가 높아지면 H⁺를 잃은 중성 아민의 비율이 커집니다."),
        ("α-카복실기", "C O OXT", *ACID),
    ]
    groups = []
    for label, names, water, ionization in [*SIDE_GROUPS[code], *backbone]:
        indexes = [atoms[n] for n in names.split()]
        bonds = [[a, b] for b in indexes for a in indexes if a < b and mol.GetBondBetweenAtoms(a, b)]
        groups.append(dict(label=label, water=water, ionization=ionization, atoms=indexes, bonds=bonds))
    return dict(wide=draw_vector(mol, 0), tall=draw_vector(mol, 90), groups=groups)


def main():
    page = GUIDE.read_text(encoding="utf-8")
    match = DATA.search(page)
    records = json.loads(match[2])
    assert {r["oneLetter"] for r in records} == set(SIDE_GROUPS) and len(records) == 20
    for row in records:
        row["drawing"] = structure(row["oneLetter"], row["formula"])
        for key in ("image", "viewBox"):
            row.pop(key, None)
    payload = json.dumps(records, ensure_ascii=False, separators=(",", ":"))
    GUIDE.write_bytes((page[:match.start(2)] + payload + page[match.end(2):]).encode("utf-8"))


if __name__ == "__main__":
    main()
