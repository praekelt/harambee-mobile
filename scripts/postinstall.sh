manage="${VENV}/bin/python ${INSTALLDIR}/${REPO}/manage.py"

su - postgres -c "createdb harambee"

$manage migrate
cd ${INSTALLDIR}/${REPO}
$manage collectstatic --noinput
