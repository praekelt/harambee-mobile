manage="${VENV}/bin/python ${INSTALLDIR}/${REPO}/manage.py"

$manage migrate
$manage collectstatic --noinput

supervisorctl restart all
