import re


def analyze_query_plan(explain_output):

    analysis = {

        "scan_type": "Unknown",

        "query_cost": None,

        "execution_time": None,

        "rows": None,

        "recommendations": []

    }


    # Convert list output into text

    plan_text = " ".join(explain_output)



    # Detect Scan Type

    if "Seq Scan" in plan_text:

        analysis["scan_type"] = "Sequential Scan"

        analysis["recommendations"].append(
            "⚠ Sequential Scan detected. Consider creating an index."
        )



    elif "Index Scan" in plan_text:

        analysis["scan_type"] = "Index Scan"

        analysis["recommendations"].append(
            "✅ Index Scan detected. Query is using indexes efficiently."
        )



    elif "Bitmap Index Scan" in plan_text:

        analysis["scan_type"] = "Bitmap Index Scan"

        analysis["recommendations"].append(
            "✅ Bitmap Index Scan detected."
        )



    # Extract Query Cost

    cost_match = re.search(
        r"cost=\d+\.\d+\.\.(\d+\.\d+)",
        plan_text
    )


    if cost_match:

        analysis["query_cost"] = float(
            cost_match.group(1)
        )



    # Extract Execution Time

    time_match = re.search(
        r"Execution Time:\s+([\d.]+)\s+ms",
        plan_text
    )


    if time_match:

        analysis["execution_time"] = float(
            time_match.group(1)
        )



    # Extract Rows

    rows_match = re.search(
        r"rows=(\d+)",
        plan_text
    )


    if rows_match:

        analysis["rows"] = int(
            rows_match.group(1)
        )



    # Additional Recommendations

    if analysis["query_cost"]:

        if analysis["query_cost"] > 100:

            analysis["recommendations"].append(
                "⚠ High query cost detected. Query optimization is recommended."
            )



    if "SELECT *" in plan_text.upper():

        analysis["recommendations"].append(
            "💡 Avoid SELECT *. Fetch only required columns."
        )



    if not analysis["recommendations"]:

        analysis["recommendations"].append(
            "✅ Query performance looks good."
        )



    return analysis