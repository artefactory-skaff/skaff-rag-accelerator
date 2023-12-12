#!/bin/bash -e

read -p "Want to install conda env named 'skaff-rag-accelerator'? (y/n)" answer
if [ "$answer" = "y" ]; then
  echo "Installing conda env..."
  conda create -n skaff-rag-accelerator python=3.10 -y
  source $(conda info --base)/etc/profile.d/conda.sh
  conda activate skaff-rag-accelerator
  echo "Installing requirements..."
  pip install -r requirements-developer.txt
  python3 -m ipykernel install --user --name=skaff-rag-accelerator
  conda install -c conda-forge --name skaff-rag-accelerator notebook -y
  echo "Installing pre-commit..."
  make install_precommit
  echo "Installation complete!";
else
  echo "Installation of conda env aborted!";
fi
