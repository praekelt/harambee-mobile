manage="${VENV}/bin/python ${INSTALLDIR}/${REPO}/manage.py"
pip install git+ssh://git@github.com/HarambeeYouth/HarambeeYouth.git

$manage migrate --noinput
cd ${INSTALLDIR}/${REPO}
$manage collectstatic --noinput
$manage update_index 
