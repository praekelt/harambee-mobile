manage="${VENV}/bin/python ${INSTALLDIR}/${REPO}/manage.py"

$manage migrate --noinput
cd ${INSTALLDIR}/${REPO}
$manage collectstatic --noinput
pip install git+ssh://git@github.com/HarambeeYouth/HarambeeYouth.git
