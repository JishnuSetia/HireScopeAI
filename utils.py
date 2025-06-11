import csv
import datetime

def export_interview_report(transcript, questions):
    filename = f"interview_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, mode="w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Candidate Response", "Suggested Questions"])
        writer.writerow([transcript, questions])
