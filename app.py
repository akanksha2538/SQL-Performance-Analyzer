from flask import (
    Flask,
    render_template,
    request,
    Response,
    send_file
)

import psycopg2
import time
import csv
import os

from io import StringIO

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph
)

from reportlab.lib.styles import getSampleStyleSheet

from config import *
from analyzer.graph_generator import (
    create_execution_graph,
    create_fastest_slowest_graph,
    create_statistics_pie
)
from analyzer.comparison_graph import create_comparison_graph
from analyzer.query_optimizer import analyze_query_plan


app = Flask(__name__)


# ================= HOME PAGE =================

@app.route("/", methods=["GET", "POST"])
def home():

    results = None
    columns = None
    execution_time = None
    error = None
    explain_output = None
    recommendations = []
    optimization_analysis = None


    if request.method == "POST":

        query = request.form["query"]


        try:

            connection = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                port=DB_PORT
            )


            cursor = connection.cursor()


            # Calculate execution time

            start = time.time()


            cursor.execute(query)


            if cursor.description:

                columns = [
                    desc[0]
                    for desc in cursor.description
                ]

                results = cursor.fetchall()

            else:

                connection.commit()



            end = time.time()

            execution_time = round(
                end - start,
                5
            )



            # Store Query History

            cursor.execute(
                """
                INSERT INTO query_history
                (sql_query, execution_time)
                VALUES (%s,%s)
                """,
                (query, execution_time)
            )


            connection.commit()



            # ================= QUERY OPTIMIZATION =================


            if query.strip().upper().startswith("SELECT"):


                cursor.execute(
                    "EXPLAIN ANALYZE " + query
                )


                explain_output = [
                    row[0]
                    for row in cursor.fetchall()
                ]



                optimization_analysis = analyze_query_plan(
                    explain_output
                )


                recommendations = (
                    optimization_analysis["recommendations"]
                )



            cursor.close()

            connection.close()



        except Exception as e:

            error = str(e)



    return render_template(
        "index.html",
        results=results,
        columns=columns,
        execution_time=execution_time,
        error=error,
        explain_output=explain_output,
        recommendations=recommendations,
        optimization_analysis=optimization_analysis
    )





# ================= HISTORY PAGE =================


@app.route("/history")
def history():

    connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )


    cursor = connection.cursor()



    cursor.execute(
        """
        SELECT id,
               sql_query,
               execution_time,
               execution_date
        FROM query_history
        ORDER BY id DESC
        """
    )


    history = cursor.fetchall()



    cursor.close()

    connection.close()



    return render_template(
        "history.html",
        history=history
    )
# ================= PERFORMANCE COMPARISON =================

@app.route("/comparison")
def comparison():

    connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

    cursor = connection.cursor()

    cursor.execute("""
        SELECT execution_time
        FROM query_history
        ORDER BY id DESC
        LIMIT 2
    """)

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    if len(rows) < 2:
        return "Please execute at least two queries before viewing the comparison."

    after_time = float(rows[0][0])
    before_time = float(rows[1][0])

    if before_time == 0:
        improvement = 0
    else:
        improvement = round(
            ((before_time - after_time) / before_time) * 100,
            2
        )

    create_comparison_graph(
        before_time,
        after_time
    )

    return render_template(
        "comparison.html",
        before_time=before_time,
        after_time=after_time,
        improvement=improvement
    )


# ================= DASHBOARD PAGE =================


@app.route("/dashboard")
def dashboard():


    connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )


    cursor = connection.cursor()



    # Total Queries

    cursor.execute(
        "SELECT COUNT(*) FROM query_history"
    )

    total_queries = cursor.fetchone()[0]




    # Average Execution Time

    cursor.execute(
        """
        SELECT ROUND(AVG(execution_time)::numeric,5)
        FROM query_history
        """
    )

    avg_time = cursor.fetchone()[0]




    # Fastest Query

    cursor.execute(
        "SELECT MIN(execution_time) FROM query_history"
    )

    fastest = cursor.fetchone()[0]




    # Slowest Query

    cursor.execute(
        "SELECT MAX(execution_time) FROM query_history"
    )

    slowest = cursor.fetchone()[0]




    # Slow Query Detection

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM query_history
        WHERE execution_time > 1
        """
    )


    slow_queries = cursor.fetchone()[0]




    # Performance Score

    performance_score = 100


    if slow_queries > 0:

        performance_score -= slow_queries * 5



    if performance_score < 0:

        performance_score = 0





    # Generate Graph


    cursor.execute(
        """
        SELECT id, execution_time
        FROM query_history
        ORDER BY id
        LIMIT 10
        """
    )


    query_data = cursor.fetchall()



    query_times = {}



    for row in query_data:

        query_times[
            f"Q{row[0]}"
        ] = row[1]



        graph_path = create_execution_graph(
        query_times
    )

    fast_graph = create_fastest_slowest_graph(
        fastest,
        slowest
    )

    pie_graph = create_statistics_pie(
        total_queries,
        slow_queries
    )

    cursor.close()
    connection.close()

    return render_template(
        "dashboard.html",
        total_queries=total_queries,
        avg_time=avg_time,
        fastest=fastest,
        slowest=slowest,
        slow_queries=slow_queries,
        performance_score=performance_score,
        graph_path=graph_path,
        fast_graph=fast_graph,
        pie_graph=pie_graph
    )





# ================= RUN APPLICATION =================
@app.route("/export_csv")
def export_csv():

    connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id,
               sql_query,
               execution_time,
               execution_date
        FROM query_history
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    output = StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "SQL Query",
        "Execution Time",
        "Execution Date"
    ])

    writer.writerows(rows)

    csv_data = output.getvalue()

    output.close()

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=query_history.csv"
        }
    )
@app.route("/export_pdf")
def export_pdf():

    connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id,
               sql_query,
               execution_time,
               execution_date
        FROM query_history
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    pdf_file = "query_history_report.pdf"

    doc = SimpleDocTemplate(pdf_file)
    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "SQL Query Performance Analyzer Report",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph("<br/>", styles["BodyText"])
    )

    for row in rows:

        text = f"""
        <b>ID:</b> {row[0]}<br/>
        <b>Query:</b> {row[1]}<br/>
        <b>Execution Time:</b> {row[2]} Seconds<br/>
        <b>Date:</b> {row[3]}<br/><br/>
        """

        elements.append(
            Paragraph(text, styles["BodyText"])
        )

    doc.build(elements)

    return send_file(
        pdf_file,
        as_attachment=True
    )
if __name__ == "__main__":

    app.run(debug=True)