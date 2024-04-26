import pytest
import subprocess

INSTANCES_FOLDER = "instances"
OUTPUT_FOLDER = "."
RESULTS = {
    "test_0": 150,
    "test_1": 150,
    "20_2_nonvalidly_0": 1694233,
    "20_2_nonvalidly_1": 1683245,
    "20_3_didactics_0": 0,
    "20_3_didactics_1": 0,
    "20_4_microliter_0": 2730773.5,
    "20_4_microliter_1": 2702051,
    "21_2_larcenist_0": 1625087.5,
    "21_2_larcenist_1": 0,
    "21_3_epicarp_0": 3585211,
    "21_3_epicarp_1": 3627289,
    "21_4_evasion_0": 2759511.5,
    "21_4_evasion_1": 2746929,
    "22_2_conglobate_0": 1508744,
    "22_2_conglobate_1": 1498367,
    "22_3_mycoses_0": 2587174,
    "22_3_mycoses_1": 2689896,
    "22_4_meropia_0": 3073210.5,
    "22_4_meropia_1": 3262368,
    "23_2_tagalize_0": 3869998.5,
    "23_2_tagalize_1": 3841293,
    "23_3_pallette_0": 1709210,
    "23_3_pallette_1": 1807628,
    "23_4_misframe_0": 1796182,
    "23_4_misframe_1": 1786548,
    "24_2_aspection_0": 2244922,
    "24_2_aspection_1": 2244525,
    "24_3_cybernion_0": 2249894,
    "24_3_cybernion_1": 2308844,
    "24_4_gabbais_0": 2881926.5,
    "24_4_gabbais_1": 2843280,
    "25_2_legalistic_0": 759897.5,
    "25_2_legalistic_1": 770033,
    "25_3_alidade_0": 4709596,
    "25_3_alidade_1": 0,
    "25_4_ducdame_0": 4052795.5,
    "25_4_ducdame_1": 0,
    "26_2_brutifying_0": 2294785,
    "26_2_brutifying_1": 2307654,
    "26_3_bepraiser_0": 2869977,
    "26_3_bepraiser_1": 2851762,
    "26_4_barbettes_0": 4743833.5,
    "26_4_barbettes_1": 4811434,
}


@pytest.mark.parametrize("instance,result", RESULTS.items())
def test(instance: str, result: float):
    t = instance.split("_")[-1]
    instance = "_".join(instance.split("_")[:-1])
    py_command = f"python3 generate_model.py {INSTANCES_FOLDER}/{instance}.txt {t}"
    subprocess.call(py_command, shell=True)
    glpk_command = (
        f"glpsol --lp {instance}_{t}.lp -o {OUTPUT_FOLDER}/{instance}_{t}.sol"
    )
    subprocess.call(glpk_command, shell=True)
    with open(f"{OUTPUT_FOLDER}/{instance}_{t}.sol") as f:
        assert (
            float(f.readlines()[5].split("=")[1].replace("(MINimum)", "").strip())
            == result
        )
