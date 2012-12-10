current_dir="$(dirname $0)"

if test "$1" == "-reset"; then
    rm -f ${current_dir}/config/data.cfg
    rm -f ${current_dir}/*.pyc
    rm -f ${current_dir}/pywikipedia/*.pyc
elif test "$1" == "-gitrm"; then
    git rm $(git ls-files --deleted)
fi
