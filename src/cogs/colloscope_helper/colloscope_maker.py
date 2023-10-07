import csv
import datetime
import os
from typing import Any, Callable, Literal

from fpdf import FPDF

ANNEE_SCOLAIRE = 2023  # année de la rentrée
COLLOSCOPE_PATH = "./data/colloscope.csv"  # path to the colloscope csv file


class ColleData:
    # This class contains the information of a single colle
    def __init__(self, groupe: str, matiere: str, prof: str, semaine: str, jourSemaine: str, heure: str, salle: str):
        self.groupe = groupe

        self.matiere = matiere
        self.prof = prof
        self.semaine = semaine
        self.jourSemaine = jourSemaine.lower()
        self.heure = heure
        self.salle = salle

        self.date = self.formatDate()
        self.dateLetters = self.formatDateLetters()

    def __str__(self):  # what this class return whene printed
        return f"Le {self.date}, passe le groupe {self.groupe} en {self.salle} avec {self.prof} à {self.heure}"

    def formatDate(self):
        jourSemaines = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"]

        jourInt, moisInt = map(
            int, self.semaine.split("-")[0].split("/")
        )  # get the day and month of the first day of the week

        if int(moisInt) > 8:
            annee = ANNEE_SCOLAIRE
        else:
            annee = ANNEE_SCOLAIRE + 1

        jour = datetime.date(annee, moisInt, jourInt)

        delta_jour = datetime.timedelta(days=0)

        for j in enumerate(jourSemaines):
            if j[1] == self.jourSemaine:
                delta_jour = datetime.timedelta(days=j[0])
                break

        return (jour + delta_jour).strftime("%d/%m/%Y")

    def formatDateLetters(self):
        monthName = [
            "janvier",
            "fevrier",
            "mars",
            "avril",
            "mai",
            "juin",
            "juillet",
            "aout",
            "septembre",
            "octobre",
            "novembre",
            "decembre",
        ]
        date = self.date.split("/")

        return f" {self.jourSemaine} {date[0]} {monthName[ int(date[1])-1 ]}"  # date en toute lettre


def sort_colles(
    colles_datas: list[ColleData], sort_type: Literal["temps", "prof", "groupe"] = "temps"
) -> list[ColleData]:
    def by_time(c: ColleData):
        return datetime.datetime.strptime(c.date, "%d/%m/%Y").timestamp()

    def by_prof(c: ColleData):
        return c.prof

    def by_groupe(c: ColleData):
        return c.groupe

    key: Callable[[ColleData], Any]
    match sort_type:
        case "temps":
            key = by_time
        case "prof":
            key = by_prof
        case "groupe":
            key = by_groupe
    return sorted(colles_datas, key=key)


def get_all_colles(filename: str):
    # returns a list of all the collesDatas by reading the csv file
    colles: list[ColleData] = []  # list of collesDatas

    with open(filename, encoding="utf-8", errors="ignore") as f:  # open file
        csv_reader = csv.reader(f, delimiter=",")  # CSV reader

        header = []  # header
        data_matrix: list[Any] = []  # array of all the csv data | dataMatrix[y][x] to get the data
        for i, row in enumerate(csv_reader):  # iterate over each row
            if i == 0:  # get the first row
                header = row
            data_matrix.append(row)

    for y in range(1, len(data_matrix)):  # iterate over each colles rows
        matiere = data_matrix[y][0]
        professeur = data_matrix[y][1]
        jour = data_matrix[y][2]
        heure = data_matrix[y][3]
        salle = data_matrix[y][4]

        for x in range(5, len(header)):  # iterate over each colles columns
            groupe = data_matrix[y][x]
            semaine = data_matrix[0][x]
            if groupe != "":
                colles.append(ColleData(groupe, matiere, professeur, semaine, jour, heure, salle))

    return colles


def get_vacances(filename: str) -> list[str]:
    """#### renvoie les dates de chaques vacances"""
    with open(filename, encoding="utf-8", errors="ignore") as Cfile:  # open file
        csv_reader = csv.reader(Cfile, delimiter=",")  # CSV reader

        vacances: list[str] = []  #
        for RowIndex, row in enumerate(csv_reader):  # iterate over each row
            if RowIndex == 0:  # get the first row
                for i, week in enumerate(row):  # iterate over each column
                    if week.lower() == "vacances":
                        if not row[i - 1]:
                            continue  # skip empty rows
                        semaine = ColleData("", "", "", row[i - 1], "lundi", "", "").formatDate()  # format date
                        vacances.append(add_one_week(semaine))  # add vacances to list

    return vacances


def compare_dates(date1: str, date2: str) -> bool:
    """### takes in two dates of format dd/mm/yyyy
    #### True if date1 > date2 else False
    """
    ldate1 = list(map(int, date1.split("/")))
    ldate2 = list(map(int, date2.split("/")))
    convert1 = datetime.datetime(ldate1[2], ldate1[1], ldate1[0])
    convert2 = datetime.datetime(ldate2[2], ldate2[1], ldate2[0])
    return convert1 > convert2


def add_one_week(time: str) -> str:
    """### Add one week
    #### Args :
        time : string dd/mm/yyyy
    """
    date1 = list(map(int, time.split("/")))
    convert1 = datetime.datetime(date1[2], date1[1], date1[0])
    convert1 = convert1 + datetime.timedelta(days=7)
    return convert1.strftime("%d/%m/%Y")


def convert_hour(time: str) -> str:
    """Convertie l'heure francaises en heures anglaise
    Ex: 10h00 -> 10:00 AM
        18h00 -> 6:00 PM

    Args:
        heure (string): Ex: 18h00
    """

    temps = time.split("h")

    temps[1] = "00" if temps[1] == "" else temps[1]

    heure = int(temps[0])
    if heure >= 12:
        heure = heure - 12
        return str(heure) + f":{temps[1]} PM"
    else:
        return str(heure) + f":{temps[1]} AM"


def add_one_hour(time: str) -> str:
    """Ajoute une heure à l'heure donnée (pas de colle a minuit donc flemme)

    Args:
        time (string): Ex: 10:00 AM
    """

    temps = time.split(":")
    heure = int(temps[0])
    if heure == 12:
        return f"1:{temps[1].split(' ')[0]} PM"
    else:
        return str(heure + 1) + f":{temps[1]}"


def export_colles(
    export_type: Literal["pdf", "csv", "agenda", "todoist"],
    collesDatas: list[ColleData],
    groupe: int,
    vacances: list[str],
):
    pathExport = f"./exports/groupe{groupe}"

    if os.path.exists(pathExport) == False:
        os.mkdir(pathExport)

    def simpleCSV(colles_datas: list[ColleData]):
        # write the sorted data into a csv file
        with open(os.path.join(pathExport, f"ColloscopeGroupe{groupe}.csv"), "w", newline="") as Ofile:
            writer = csv.writer(Ofile, delimiter=",")
            writer.writerow(["date", "heure", "prof", "salle", "matière"])

            for colle in colles_datas:  # écris les données de colles dans un fichier
                data = [colle.date, colle.heure, colle.prof, colle.salle, colle.matiere]
                writer.writerow(data)

        return os.path.join(pathExport, f"ColloscopeGroupe{groupe}.csv")

    def agenda(colles_datas: list[ColleData]):
        AgendaColle: list[dict[str, Any]] = []
        for colle in colles_datas:
            AgendaColle.append(
                {
                    "Subject": f"{colle.matiere} {colle.prof} {colle.salle}",
                    "Start Date": colle.date,
                    "Start Time": convert_hour(colle.heure),
                    "End Date": colle.date,
                    "End Time": add_one_hour(convert_hour(colle.heure)),
                    "All Day Event": False,
                    "Description": f"Colle de {colle.matiere} avec {colle.prof} en {colle.salle} a {colle.heure}",
                    "Location": colle.salle,
                }
            )

        with open(os.path.join(pathExport, f"AgendaGroupe{groupe}.csv"), "w", newline="") as csvfile:
            fieldnames = [
                "Subject",
                "Start Date",
                "Start Time",
                "End Date",
                "End Time",
                "All Day Event",
                "Description",
                "Location",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for colle in AgendaColle:
                writer.writerow(colle)

    def todoist(colles_datas: list[ColleData]):
        type, priority = "task", 2
        todoistColle: list[dict[str, Any]] = []
        for colle in colles_datas:
            todoistColle.append(
                {
                    "TYPE": type,
                    "CONTENT": f"Colle de {colle.matiere} avec {colle.prof}",
                    "DESCRIPTION": f"Salle {colle.salle}",
                    "PRIORITY": priority,
                    "INDENT": "",
                    "AUTHOR": "",
                    "RESPONSIBLE": "",
                    "DATE": colle.date + " " + colle.heure,
                    "DATE_LANG": "fr",
                    "TIMEZONE": "Europe/Paris",
                }
            )

        with open(os.path.join(pathExport, f"todoistGroupe{groupe}.csv"), "w", newline="") as csvfile:
            fieldnames = [
                "TYPE",
                "CONTENT",
                "DESCRIPTION",
                "PRIORITY",
                "INDENT",
                "AUTHOR",
                "RESPONSIBLE",
                "DATE",
                "DATE_LANG",
                "TIMEZONE",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for colle in todoistColle:
                writer.writerow(colle)

        return os.path.join(pathExport, f"todoistGroupe{groupe}.csv")

    def pdfExport(colles_datas: list[ColleData], vacances: list[str]):
        vacanceIndex = 0
        pdf = FPDF()
        pdf.add_page()
        page_width = pdf.w - 2 * pdf.l_margin

        pdf.set_font("Arial", "U", 14)
        pdf.cell(page_width, 0.0, f"Colloscope groupe {groupe}", align="C")
        pdf.ln(10)

        pdf.set_font("Arial", "", 11)

        col_width = page_width / 4

        pdf.ln(1)

        th = pdf.font_size + 2

        pdf.set_font("Arial", "B", 11)
        pdf.cell(10, th, txt="Id", border=1, align="C")
        pdf.cell(40, th, "Date", border=1, align="C")
        pdf.cell(20, th, "Heure", border=1, align="C")
        pdf.cell(col_width * 0.75, th, "Prof", border=1, align="C")
        pdf.cell(30, th, "Salle", border=1, align="C")
        pdf.cell(col_width, th, "Matiere", border=1, align="C")
        pdf.set_font("Arial", "", 11)
        pdf.ln(th)

        for i, colle in enumerate(colles_datas, 1):
            if vacanceIndex < len(vacances):  # fait un saut de ligne à chaque vacances
                if compare_dates(colle.date, vacances[vacanceIndex]):
                    pdf.ln(th * 0.5)
                    pdf.set_font("Arial", "B", 14)
                    pdf.cell(90 + 2 * col_width, th, f"Vacances", align="C")
                    pdf.set_font("Arial", "", 11)
                    pdf.ln(th * 1.5)
                    vacanceIndex += 1
            pdf.cell(10, th, str(i), border=1, align="C")
            pdf.set_font("Arial", "", 9)
            pdf.cell(40, th, colle.dateLetters, border=1, align="C")
            pdf.set_font("Arial", "", 11)
            pdf.cell(20, th, colle.heure, border=1, align="C")
            pdf.cell(col_width * 0.75, th, colle.prof, border=1, align="C")
            pdf.cell(30, th, colle.salle, border=1, align="C")
            pdf.cell(col_width, th, colle.matiere, border=1, align="C")
            pdf.ln(th)

        pdf.ln(10)

        pdf.set_font("Times", "", 10)

        pdf.output(os.path.join(pathExport, f"ColloscopeGroupe{groupe}.pdf"), "F")

        return os.path.join(pathExport, f"ColloscopeGroupe{groupe}.pdf")

    match export_type:
        case "csv":
            return simpleCSV(collesDatas)

        case "agenda":
            return agenda(collesDatas)

        case "pdf":
            return pdfExport(collesDatas, vacances)

        case "todoist":
            return todoist(collesDatas)

    Exception("Invalid sort type")


def getGroupRecentColleData(groupe):
    if groupe == "":
        return []

    colles = get_all_colles(COLLOSCOPE_PATH)  # list of ColleData objects
    colles = sort_colles(colles, sort_type="temps")  # sort by time
    sortedColles = []
    currentDate = datetime.datetime.now() + datetime.timedelta(days=-1)  # date de la veille
    currentDate = currentDate.strftime("%d/%m/%Y")

    for data in colles:
        if data.groupe == groupe and compare_dates(data.date, currentDate):
            sortedColles.append(data)
    return sortedColles


def main(userGroupe, typeExport="pdf"):
    colles = get_all_colles(COLLOSCOPE_PATH)  # list of ColleData objects
    vacances = get_vacances(COLLOSCOPE_PATH)
    colles = sort_colles(colles, sort_type="temps")  # sort by time

    sortedColles = []

    for data in colles:
        if data.groupe == userGroupe:
            sortedColles.append(data)

    try:
        groupe = sortedColles[0].groupe
    except IndexError:
        return "Aucune colle n'a été trouvé pour ce groupe"

    return export_colles(typeExport, sortedColles, groupe, vacances)
