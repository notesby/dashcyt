from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, send_from_directory
)

from .auth import login_required
from .models import db, Report, SavedGraph
from .graph import load_geojson, run_query, generate_graph, display_graph
import pdfkit
import os

bp = Blueprint('reports', __name__)


@bp.route('/')
def index():
    reports = Report.query.all()
    return render_template('reports.html', reports=reports)


@bp.route('/report/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        user_id = session.get('user_id')
        report = Report(name=name, user_id=user_id)
        db.session.add(report)
        db.session.commit()
        return redirect(url_for("reports.index"))

    return render_template('addreport.html')


@bp.route('/report/<int:report_id>/download')
def download(report_id):
    graphs = SavedGraph.query.filter_by(report_id=report_id)
    graphs = list([x for x in graphs])
    for i, graph in enumerate(graphs):
        data = run_query(graph, graph.fields)
        geojson = None
        if graph.geojson:
            geojson = load_geojson(graph.geojson)
        fig = generate_graph(data, geojson, graph.graph_options, graph.type)
        graphs[i].image = display_graph(fig, "image")

    html = render_template('pdftemplate.html', graphs=graphs)
    root = os.path.realpath(os.path.dirname(__file__))
    pdf_path = os.path.join(root, "static", f"{report_id}.pdf")
    pdfkit.from_string(html, pdf_path)
    
    return send_from_directory(os.path.join(root, "static"), f"{report_id}.pdf")


