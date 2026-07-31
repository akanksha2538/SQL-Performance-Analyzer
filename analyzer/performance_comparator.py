import time


def measure_query_time(cursor, query):

    start = time.time()

    cursor.execute(query)

    if cursor.description:
        cursor.fetchall()

    end = time.time()

    execution_time = round(
        end - start,
        5
    )

    return execution_time



def calculate_improvement(before, after):

    if before == 0:
        return 0

    improvement = (
        (before - after)
        / before
    ) * 100


    return round(improvement, 2)