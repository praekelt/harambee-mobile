manage="${VENV}/bin/python ${INSTALLDIR}/${REPO}/manage.py"

$manage migrate --noinput
cd ${INSTALLDIR}/${REPO}
$manage collectstatic --noinput
