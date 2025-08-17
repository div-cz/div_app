from div_content.forms.testmovies import MyForm
from django.shortcuts import render, redirect
from django.http import HttpResponse
import subprocess
import os
import logging
import json


# Nastavení logging
logging.basicConfig(filename=r'/var/www/div_app/div_scripts/movies/logs/django_script_execution.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def run_script(startid, lastid=None):
    python_executable = r'/var/www/div_app/venv/bin/python'
    script_path = r'/var/www/div_app/div_scripts/movies/movies_async_v3.py'

    args = ['--startid', str(startid)]
    if lastid:
        args.extend(['--lastid', str(lastid)])

    try:
        result = subprocess.run(
            [python_executable, script_path] + args,
            capture_output=True, text=True, check=True
        )
        titles = json.loads(result.stdout)
        logging.debug(f"Script output: {titles}")
        return titles
    except subprocess.CalledProcessError as e:
        logging.error(f"CalledProcessError: {e.stderr}")
        return f"Error: {e.stderr}"
    except Exception as e:
        logging.error(f"Exception: {str(e)}")
        return str(e)

def my_view(request):
    if request.method == "POST":
        form = MyForm(request.POST)
        if form.is_valid():
            startid = form.cleaned_data['arg1']
            lastid = form.cleaned_data['arg2']
            titles = run_script(startid, lastid)
            if isinstance(titles, list):
                output = f"Úspěšně přidáno ID od {startid} - {lastid if lastid else startid}.Aktualizované tituly: \n{'\n'.join(titles)}"
            else:
                output = titles  # If there's an error, it will be a string
            request.session['output'] = output
            return redirect('add_movies')
    else:
        form = MyForm()

    output = request.session.pop('output', '')

    return render(request, 'test_movies.html', {"form": form, "output": output})


# -------------------------------------------------------------------
#                    KONEC
#           Catalog DIV.cz by eKultura
# -------------------------------------------------------------------