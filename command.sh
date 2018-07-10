mkdir public/conf
mkdir public/csv
mkdir public/results
sudo -HE env PATH=$PATH PYTHONPATH=$PYTHONPATH FLASK_APP="~/server.py" python3 -m flask run --host=0.0.0.0 --port=80
