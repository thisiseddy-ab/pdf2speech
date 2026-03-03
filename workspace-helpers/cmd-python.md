#### ====== Python ENV Commands ===== ####

# === create env === #
python -m venv venv

# === activate env (Windows) === #
.\venv\Scripts\activate

# === activate env (Unix/macOS) === #
source venv/bin/activate

# === deactivate env === #
deactivate

# === remove env === #
rmdir /s /q venv         # Windows
rm -rf venv              # Unix/macOS

# === show Python version === #
python --version

# === show venv Python path === #
where python             # Windows
which python             # Unix/macOS

# === install virtualenv globally === #
pip install virtualenv

# === create env with virtualenv === #
virtualenv venv

# === recreate env from scratch === #
rmdir /s /q venv && python -m venv venv && .\venv\Scripts\activate && pip install -r requirements.txt


#### ====== Python PIP Commands ===== ####

# === upgrade pip === #
pip install --upgrade pip

# === install requirements === #
pip install -r requirements.txt

# === freeze current packages === #
pip freeze > requirements.txt

# === install a package === #
pip install package_name

# === uninstall a package === #
pip uninstall package_name

# === show installed packages === #
pip list

# === check outdated packages === #
pip list --outdated

# === upgrade all packages (one-liner) === #
pip list --outdated --format=freeze | % { pip install --upgrade ($_ -split '==')[0] }     # PowerShell
pip list --outdated | awk 'NR>2 {print $1}' | xargs -n1 pip install -U                    # Unix/macOS

# === show package info === #
pip show package_name

# === search for packages === #
pip search keyword    # (deprecated, may not work in latest versions)