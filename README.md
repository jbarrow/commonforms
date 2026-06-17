# CommonForms

🪄 Automatically convert a PDF into a fillable form.

[💻 Hosted Models (detect.semanticdocs.org)](https://detect.semanticdocs.org) | [📄 CommonForms Paper](https://arxiv.org/abs/2509.16506) | [🤗 Dataset](https://huggingface.co/datasets/jbarrow/CommonForms) | [🤗 FFDNet-L](https://huggingface.co/jbarrow/FFDNet-L) | [🤗 FFDNet-S](https://huggingface.co/jbarrow/FFDNet-S)

![Pipeline](https://raw.githubusercontent.com/jbarrow/commonforms/main/assets/pipeline.png)

This repo contains three things:
1. the pip-installable `commonforms` package, which has a CLI and API for converting PDFs into fillable forms
2. the FFDNet-S and FFDNet-L models from the paper [CommonForms: A Large, Diverse Dataset for Form Field Detection](https://arxiv.org/abs/2509.16506) 
3. the preprocessing code for the CommonForms dataset, which is hosted on HuggingFace: https://huggingface.co/datasets/jbarrow/CommonForms


## Installation

CommonForms is a CLI tool with a sizable dependency footprint (`transformers`,
`torch`, `rfdetr`, `ultralytics`, and friends), so the cleanest install is an
**isolated** one that creates a dedicated environment and exposes just the
`commonforms` command:

```sh
uv tool install commonforms
# or
pipx install commonforms
```

If you'd rather use it as a **library** inside an existing project, install it with
`uv` or `pip`, feel free to choose your package manager flavor:

```sh
uv pip install commonforms
# or
pip install commonforms
```

> ⚠️ A plain `pip install` (or `uv pip install`) installs into your **active**
> environment. Because the dependency set is large and pins recent versions, this can
> upgrade packages like `numpy`, `pillow`, and `transformers` in place — so install
> into a dedicated virtualenv/conda env, not a shared `base`.

Once it's installed, you should be able to run the CLI command on ~any PDF.

## CommonForms CLI

The simplest usage will run inference on your CPU using the default suggested settings:

```
commonforms <input.pdf> <output.pdf>
```

| Input | Output |
|-------|--------|
| ![Input PDF](https://raw.githubusercontent.com/jbarrow/commonforms/main/assets/input.png) | ![Output PDF](https://raw.githubusercontent.com/jbarrow/commonforms/main/assets/output.png) |

### Command Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `input` | Path | Required | Path to the input PDF file |
| `output` | Path | Required | Path to save the output PDF file |
| `--model` | str | `FFDNet-L` | Model name (FFDNet-L/FFDNet-S) or path to custom .pt file |
| `--keep-existing-fields` | flag | `False` | Keep existing form fields in the PDF |
| `--use-signature-fields` | flag | `False` | Use signature fields instead of text fields for detected signatures |
| `--device` | str | `cpu` | Device for inference (e.g., `cpu`, `cuda`, `0`) |
| `--image-size` | int | `1600` | Image size for inference |
| `--confidence` | float | `0.3` | Confidence threshold for detection |
| `--fast` | flag | `False` | If running on a CPU, you can trade off accuracy for speed and run in about half the time |
| `--multiline` | flag | `False` | If you want the detected textboxes to allow multiline inputs |


## CommonForms API

In addition to the CLI, you can use

```py
from commonforms import prepare_form

prepare_form(
    "path/to/input.pdf",
    "path/to/output.pdf"
)
```

All of the above arguments are keyword arguments to the `prepare_form` function.

## Dataset Prep

🚧 Code for dataset prep exists in the `dataset` folder.


# Citation

If you use the tool, models, or code in an academic paper, please cite the CommonForms paper:
```
@misc{barrow2025commonforms,
  title        = {CommonForms: A Large, Diverse Dataset for Form Field Detection},
  author       = {Barrow, Joe},
  year         = {2025},
  eprint       = {2509.16506},
  archivePrefix= {arXiv},
  primaryClass = {cs.CV},
  doi          = {10.48550/arXiv.2509.16506},
  url          = {https://arxiv.org/abs/2509.16506}
}
```

If you use it in a non-academic setting, please reach out to the author (joseph.d.barrow [at] gmail.com)!
I love to hear when people are using my work!
