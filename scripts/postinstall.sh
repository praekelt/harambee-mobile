manage="${VENV}/bin/python ${INSTALLDIR}/${REPO}/manage.py"

$manage migrate
cd ${INSTALLDIR}/${REPO}
$manage collectstatic --noinput
