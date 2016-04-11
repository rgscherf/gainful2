source bin/activate
cd elm
elm-make src/Main.elm --output="../parsing/static/parsing/elm.js"
cd ..
sass parsing/style.scss parsing/static/parsing/style.css
python3 manage.py collectstatic --noinput

