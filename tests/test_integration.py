import subprocess
import sys

import pytest

ad = pytest.importorskip("anndata")
np = pytest.importorskip("numpy")
pd = pytest.importorskip("pandas")


def _write(path, expression, genes, labels=None):
    obs = pd.DataFrame(index=[f"cell_{i}" for i in range(len(expression))])
    if labels is not None:
        obs["celltype"] = labels
    ad.AnnData(
        X=np.asarray(expression, dtype=np.float32),
        obs=obs,
        var=pd.DataFrame(index=genes),
    ).write_h5ad(path)


def test_cli_runs_real_veckit_paired_bootstrap(tmp_path):
    rng = np.random.default_rng(3)
    cells, genes_n = 90, 32
    genes = [f"g{i}" for i in range(genes_n)]
    labels = np.array(["A"] * 45 + ["B"] * 45)
    reference = np.log1p(
        rng.poisson(3, size=(cells, genes_n))
    ).astype(np.float32)
    target = reference.copy()
    target[:, :8] += 0.4
    target[:, 8:16] = np.maximum(target[:, 8:16] - 0.3, 0)
    model_a = np.maximum(target + rng.normal(0, 0.18, target.shape), 0)
    model_b = np.maximum(target + rng.normal(0, 0.08, target.shape), 0)

    ref = tmp_path / "ref.h5ad"
    truth = tmp_path / "target.h5ad"
    prediction_a = tmp_path / "a.h5ad"
    prediction_b = tmp_path / "b.h5ad"
    out = tmp_path / "out"
    _write(ref, reference, genes, labels)
    _write(truth, target, genes, labels)
    _write(prediction_a, model_a, genes)
    _write(prediction_b, model_b, genes)

    run = subprocess.run(
        [
            sys.executable,
            "-m",
            "vec_bootstrap.cli",
            str(prediction_a),
            "--prediction-b",
            str(prediction_b),
            "--task",
            "T1",
            "--target",
            str(truth),
            "--reference",
            str(ref),
            "--reps",
            "3",
            "--sample-cells",
            "60",
            "--out",
            str(out),
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=240,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    assert (out / "summary.csv").exists()
    assert "bootstrap B-better fraction" in (out / "report.md").read_text()
