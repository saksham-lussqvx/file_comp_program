import flet as ft
import time
from math import pi
import pandas as pd
from fuzzywuzzy import fuzz
from mysql.connector import connect
import traceback
import base64
import hashlib
import random
import os


def encryption(text: str):
    # generate a key as long as the text
    key = ""
    chars = (
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()_+-=."
    )
    "N)y0n"
    "hello"
    "hNe)y0ln"
    for i in range(len(text)):
        key += random.choice(chars)
    # now add this number to the text
    # to add this, first take 1 character from the text and then add the number do this until the text is finished
    final_text = ""
    for i in range(len(text)):
        final_text += text[i] + key[i]
    text = final_text
    # now encode the text
    text = base64.b64encode(text.encode())
    # now hash the text
    hash_object = hashlib.sha256()
    hash_object.update(text)
    hex_dig = hash_object.hexdigest()
    # now return the text
    return text.decode()


def decryption(text: str):
    # first decode the text
    text = base64.b64decode(text)
    # now hash the text
    hash_object = hashlib.sha256()
    hash_object.update(text)
    hex_dig = hash_object.hexdigest()
    # now remove the key from the text
    final_text = ""
    text = text.decode()
    for i in range(0, len(text), 2):
        final_text += text[i]
    text = final_text
    # now return the text
    return text


def create_db(user, password):
    try:
        # connect to the mysql server
        connection = connect(host="localhost", user=user, password=password)
        # delete the previous database if it exists
        delete_db_query = "DROP DATABASE IF EXISTS main_db"
        with connection.cursor() as cursor:
            cursor.execute(delete_db_query)
            connection.commit()
        # now here check if the db - "main_db" exists, if not then create it
        create_db_query = "CREATE DATABASE IF NOT EXISTS main_db"
        with connection.cursor() as cursor:
            cursor.execute(create_db_query)
            connection.commit()
            # here create a table in the main_db with columns - serial no, id_1, id_2, match_percent, date, address, city, state, zip code, country, telephone
            create_table_query = "CREATE TABLE IF NOT EXISTS main_db.main_table (serial_no INT AUTO_INCREMENT PRIMARY KEY, id_1 VARCHAR(255), id_2 VARCHAR(255), match_percent VARCHAR(255), date VARCHAR(255), address VARCHAR(255), city VARCHAR(255), state VARCHAR(255), zip_code VARCHAR(255), country VARCHAR(255), telephone VARCHAR(255))"
            cursor.execute(create_table_query)
            connection.commit()
    except:
        traceback.print_exc()


class AnimatedBox(ft.UserControl):
    def __init__(self, border_color, bg_color, rotate_angle):
        self.border_color = border_color
        self.bg_color = bg_color
        self.rotate_angle = rotate_angle
        super().__init__()

    def build(self):
        return ft.Container(
            width=48,
            height=48,
            border=ft.border.all(2.5, self.border_color),
            border_radius=2,
            rotate=ft.transform.Rotate(self.rotate_angle, ft.alignment.center),
            animate_rotation=ft.animation.Animation(700, "easeInOut"),
        )


global path_1, path_2
path_1 = ""
path_2 = ""


def change_value(e: ft.FilePickerResultEvent):
    # give the name of the file to the text field
    global path_1
    path_1 = e.files[0].path


def change_value_2(e: ft.FilePickerResultEvent):
    # give the name of the file to the text field
    global path_2
    path_2 = e.files[0].path


def add_data_to_db(
    id_1, id_2, match_percent, date, address, city, state, zip_code, country, telephone
):
    # connect to the mysql server
    connection = connect(host="localhost", user=user, password=password)
    try:
        # add the data to the database
        add_data_query = f"INSERT INTO main_db.main_table (id_1, id_2, match_percent, date, address, city, state, zip_code, country, telephone) VALUES ('{id_1}', '{id_2}', '{match_percent}', '{date}', '{address}', '{city}', '{state}', '{zip_code}', '{country}', '{telephone}')"
        with connection.cursor() as cursor:
            cursor.execute(add_data_query)
            connection.commit()
    except:
        print("Same data already exists in the database")

# query to print all tables of a database
# SELECT table_name FROM information_schema.tables WHERE table_schema = 'main_db' ORDER BY table_name;
file_1 = ft.FilePicker(on_result=change_value)
file_2 = ft.FilePicker(on_result=change_value_2)


def process_files(file_1, file_2, page):
    # open both excel files, and match from file one, start matching data using fuzzywuzzy, and if a match if found in file 2, then add the data to another output file
    # open the first file
    df_1 = pd.read_excel(file_1)
    df_2 = pd.read_excel(file_2)

    # loop through the first file
    final_df = []
    # compare the whole row with the second file
    for index, row in df_1.iterrows():
        matches = []
        rows = []
        for index_2, row_2 in df_2.iterrows():
            # match the row
            # convert the row to a string and then match
            row_1_str = ""
            for i in range(2, len(row)):
                row_1_str += str(row[i])
            row_2_str = ""
            for i in range(2, len(row_2)):
                row_2_str += str(row_2[i])
            match = fuzz.ratio(row_1_str, row_2_str)
            # store all matches and then find the highest match
            matches.append(match)
            rows.append(row_2[0])
        # find the highest match
        highest_match = max(matches)
        # find the index of the highest match
        highest_match_index = matches.index(highest_match)
        # now just get that row from the second file
        matched_row = rows[highest_match_index]
        # now compare each column, if they are not same store not same and if same store same, also store ids of the rows
        # store the ids of the rows
        id_1 = row[1]
        id_2 = df_2.iloc[highest_match_index][1]
        other_columns = []
        for i in range(2, len(row)):
            # convert timestamp to string
            if i == 2:
                row[i] = str(row[i])
            other_columns.append(row[i])

        # now store the data in a dataframe
        # make sure data is in the same order as the columns
        data = {
            "id_1": id_1,
            "id_2": id_2,
            "match": highest_match,
            "date": other_columns[0],
            "address": other_columns[1],
            "city": other_columns[2],
            "state": other_columns[3],
            "zip_code": other_columns[4],
            "country": other_columns[5],
            "telephone": other_columns[6],
        }
        # now append the data to the final dataframe
        final_df.append(data)
        # sort final_df by date
        final_df = sorted(final_df, key=lambda k: k["date"])

    # add the data to the database
    for data in final_df:
        add_data_to_db(
            data["id_1"],
            data["id_2"],
            data["match"],
            data["date"],
            data["address"],
            data["city"],
            data["state"],
            data["zip_code"],
            data["country"],
            data["telephone"],
        )
    # now convert the final_df to a dataframe
    final_df = pd.DataFrame(final_df)
    # now save the dataframe to an excel file
    final_df.to_excel("output.xlsx")

    def close_popup(e):
        dlg_modal.open = False
        page.update()

    # now show a popup that the file has been saved
    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Notice"),
        content=ft.Text(
            "The output file has been generated and database has been updated..."
        ),
        actions=[
            ft.ElevatedButton(
                text="Ok",
                on_click=lambda e: close_popup(e),
            )
        ],
    )
    page.dialog = dlg_modal
    dlg_modal.open = True
    page.update()


def main(page: ft.Page):
    main_page = ft.Card(
        width=408,
        height=612,
        elevation=13,
        opacity=100,
        content=ft.Container(
            height=620,
            bgcolor="#23262a",
            border_radius=3,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Divider(height=40, color="transparent"),
                    ft.Stack(
                        controls=[
                            AnimatedBox("#e9665a", None, 0),
                            AnimatedBox("#7df6dd", "#23262a", pi / 4),
                        ]
                    ),
                    ft.Divider(height=20, color="transparent"),
                    ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=5,
                        controls=[
                            ft.Text(
                                "Select Files",
                                size=22,
                                weight="bold",
                                color="white",
                            ),
                        ],
                    ),
                    ft.Divider(height=40, color="transparent"),
                    ft.Container(
                        width=320,
                        height=40,
                        border=ft.border.only(
                            bottom=ft.border.BorderSide(0.5, "white54")
                        ),
                        content=ft.Row(
                            spacing=20,
                            vertical_alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                # add the file picker here
                                ft.ElevatedButton(
                                    width=320,
                                    height=42,
                                    content=ft.Text(
                                        "Select File 1", size=13, weight="bold"
                                    ),
                                    style=ft.ButtonStyle(
                                        shape={
                                            "": ft.RoundedRectangleBorder(radius=8),
                                        },
                                        color={
                                            "": "black",
                                        },
                                        bgcolor={
                                            "": "#7df6dd",
                                        },
                                    ),
                                    on_click=lambda e: file_1.pick_files(
                                        allow_multiple=False
                                    ),
                                ),
                            ],
                        ),
                    ),
                    ft.Container(
                        width=320,
                        height=40,
                        border=ft.border.only(
                            bottom=ft.border.BorderSide(0.5, "white54")
                        ),
                        content=ft.Row(
                            spacing=20,
                            vertical_alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                # add the file picker here
                                ft.ElevatedButton(
                                    width=320,
                                    height=42,
                                    content=ft.Text(
                                        "Select File 2", size=13, weight="bold"
                                    ),
                                    style=ft.ButtonStyle(
                                        shape={
                                            "": ft.RoundedRectangleBorder(radius=8),
                                        },
                                        color={
                                            "": "black",
                                        },
                                        bgcolor={
                                            "": "#7df6dd",
                                        },
                                    ),
                                    on_click=lambda e: file_2.pick_files(
                                        allow_multiple=False
                                    ),
                                ),
                            ],
                        ),
                    ),
                    ft.Divider(height=10, color="transparent"),
                    ft.Container(
                        width=320,
                        height=40,
                        border=ft.border.only(
                            bottom=ft.border.BorderSide(0.5, "white54")
                        ),
                        content=ft.Row(
                            spacing=20,
                            vertical_alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                # add the file picker here
                                file_2,
                            ],
                        ),
                    ),
                    ft.Divider(height=50, color="transparent"),
                    ft.ElevatedButton(
                        width=320,
                        height=42,
                        content=ft.Text("Compare Files", size=13, weight="bold"),
                        style=ft.ButtonStyle(
                            shape={
                                "": ft.RoundedRectangleBorder(radius=8),
                            },
                            color={
                                "": "black",
                            },
                            bgcolor={
                                "": "#7df6dd",
                            },
                        ),
                        on_click=lambda e: process_files(path_1, path_2, page),
                    ),
                ],
            ),
        ),
    )

    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    page.bgcolor = "#1f262f"

    page.overlay.append(file_1)
    page.overlay.append(file_2)
    page.update()

    def animate_boxes():
        clock_wise_rotate = pi / 4
        counter_clock_wise_rotate = -pi * 2
        red_box = page.controls[0].content.content.controls[1].controls[0].controls[0]
        blue_box = page.controls[0].content.content.controls[1].controls[1].controls[0]
        counter = 0
        while True:
            if counter >= 0 and counter <= 4:
                red_box.rotate = ft.transform.Rotate(
                    counter_clock_wise_rotate, ft.alignment.center
                )
                blue_box.rotate = ft.transform.Rotate(
                    clock_wise_rotate, ft.alignment.center
                )

                red_box.update()
                blue_box.update()

                clock_wise_rotate += pi / 2
                counter_clock_wise_rotate -= pi / 2
                counter += 1
                time.sleep(0.7)
            if counter >= 5 and counter <= 10:
                clock_wise_rotate -= pi / 2
                counter_clock_wise_rotate += pi / 2
                red_box.rotate = ft.transform.Rotate(
                    counter_clock_wise_rotate, ft.alignment.center
                )
                blue_box.rotate = ft.transform.Rotate(
                    clock_wise_rotate, ft.alignment.center
                )

                red_box.update()
                blue_box.update()
                counter += 1
                time.sleep(0.7)
            if counter > 10:
                counter = 0

    # first we have to ask for login credentials of this program, and also we have to ask for the credentials of the database
    # page.add(
    #     ft.Card(
    #         width=408,
    #         height=612,
    #         elevation=13,
    #         opacity=100,
    #         content=
    #     )
    # )
    def sign_in(e):
        def close_dialog(e):
            dlg.open = False
            page.update()

        user = username.value
        passw = password.value
        dlg = ft.AlertDialog(
            title=ft.Text("Notice"),
            content=ft.Text("User and password has been updated..."),
            actions=[ft.ElevatedButton("Ok", on_click=close_dialog)],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        if os.path.exists("creds.txt") == False:
            user = encryption(user)
            passw = encryption(passw)
            with open("creds.txt", "w") as f:
                f.write(user + "\n" + passw)
            check = True
            page.dialog = dlg
            dlg.open = True
            page.update()
        else:
            check = False
            with open("creds.txt", "r") as f:
                creds = f.read().split("\n")
                user = decryption(creds[0])
                passw = decryption(creds[1])
                if user == username.value and passw == password.value:
                    check = True

        def close_otherdlg(e):
            dialog.open = False
            page.update()

        if check == False:
            dialog = ft.AlertDialog(
                title=ft.Text("Error"),
                content=ft.Text("Invalid Username or Password"),
                actions=[ft.ElevatedButton("Ok", on_click=close_otherdlg)],
                actions_alignment=ft.MainAxisAlignment.CENTER,
            )
            page.dialog = dialog
            dialog.open = True
            page.update()
        else:
            page.remove(login_card)
            page.add(main_page)
            page.update()
            animate_boxes()

    username = ft.TextField(
        hint_text="Username",
        hint_style=ft.TextStyle(size=13, color=ft.colors.WHITE),
        border_color="transparent",
        bgcolor="transparent",
        height=20,
        width=200,
        text_size=13,
        content_padding=3,
        cursor_color=ft.colors.WHITE,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
    )

    password = ft.TextField(
        hint_text="Password",
        hint_style=ft.TextStyle(size=13, color=ft.colors.WHITE),
        border_color="transparent",
        bgcolor="transparent",
        height=20,
        width=200,
        text_size=13,
        content_padding=3,
        cursor_color=ft.colors.WHITE,
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        password=True,
    )

    login_card = ft.Card(
        width=408,
        height=612,
        elevation=13,
        opacity=100,
        content=ft.Container(
            height=620,
            bgcolor="#23262a",
            border_radius=3,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Divider(height=40, color="transparent"),
                    ft.Divider(height=40, color="transparent"),
                    ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=5,
                        controls=[
                            ft.Text(
                                "Log In Below", size=22, weight="bold", color="white"
                            ),
                            ft.Text(
                                "Enter your credentials to continue",
                                size=13,
                                weight="bold",
                                color="white",
                            ),
                        ],
                    ),
                    ft.Divider(height=40, color="transparent"),
                    ft.Container(
                        width=320,
                        height=40,
                        border=ft.border.only(
                            bottom=ft.border.BorderSide(0.5, "white54")
                        ),
                        content=ft.Row(
                            spacing=20,
                            vertical_alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Icon(ft.icons.PERSON_ROUNDED, color="white54"),
                                username,
                            ],
                        ),
                    ),
                    ft.Divider(height=10, color="transparent"),
                    ft.Container(
                        width=320,
                        height=40,
                        border=ft.border.only(
                            bottom=ft.border.BorderSide(0.5, "white54")
                        ),
                        content=ft.Row(
                            spacing=20,
                            vertical_alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Icon(ft.icons.LOCK_OPEN, color="white54"),
                                password,
                            ],
                        ),
                    ),
                    ft.Divider(height=50, color="transparent"),
                    ft.ElevatedButton(
                        width=320,
                        height=42,
                        content=ft.Text("Log In", size=13, weight="bold"),
                        style=ft.ButtonStyle(
                            shape={
                                "": ft.RoundedRectangleBorder(radius=8),
                            },
                            color={
                                "": "black",
                            },
                            bgcolor={
                                "": "#7df6dd",
                            },
                        ),
                        on_click=sign_in,
                    ),
                ],
            ),
        ),
    )
    page.add(login_card)
    page.update()

user = "root"
password = "passwd"
create_db(user, password)
ft.app(target=main, view=ft.FLET_APP)
