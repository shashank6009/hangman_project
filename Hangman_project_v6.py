# Python HANGMAN Game using tkinter and MYSQL
# Class XII Computer Science Project - PSBB K K Nagar

from tkinter import *
from PIL import ImageTk, Image
from tkinter import messagebox
import os
import random
from os import environ

# pygame is used for background music creation if user opts for the same

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1' # Disable notification from PYGAME when invoked for first time

import pygame
import pyttsx3
import mysql.connector
from mysql.connector import errorcode

global score_count
global game_count

score_count = 0
game_count = 0

# Window settings
root = Tk()
root.title("HangMan")
root.iconbitmap("Hangman.ico")
root.geometry("800x400")
root.resizable(width=False, height=False)

def disable_event():
    pass
# root.protocol("WM_DELETE_WINDOW", disable_event)  # Disable window "X" (close) button

pygame.mixer.init()
music_state = False

def play_music():
    global music_state

    if music_state:
        pygame.mixer.music.stop()
    else:
        pygame.mixer.music.load("Lokiverse-Background-Score-Bgm.mp3")
        pygame.mixer.music.play(loops=0)
    music_state = not music_state

def main_menu_():
    root.deiconify()
    global main_menu_bg
    global letter_change
    letter_change = 1
    global word_change
    word_change = 2
    global score_count
    global game_count
    if score_count != 0:
        pass
    else:
        score_count = 0
     # Create canvas and add background
    canvas = Canvas(root, width="800", height="450")
    canvas.pack()

    main_menu_bg = ImageTk.PhotoImage(Image.open("game_bg.jpg").resize((800, 450), Image.Resampling.LANCZOS))
    canvas.background = main_menu_bg
    canvas.create_image(0, 0, anchor=NW, image=main_menu_bg)

    # Add buttons to canvas
    start_btn = Button(root, text="New Game", width=15, command=new_game, borderwidth=5)
    canvas.create_window(400, 150, anchor=CENTER, window=start_btn)

    score_btn = Button(root, text="Score Board", width=15, command=score_board, borderwidth=5)
    canvas.create_window(400, 210, anchor=CENTER, window=score_btn)

    quit_btn = Button(root, text="Quit", width=15, command=quit_game, borderwidth=5)
    canvas.create_window(400, 270, anchor=CENTER, window=quit_btn)

    music_btn = Button(root, text="Background Music", command=play_music, borderwidth=5)
    canvas.create_window(700, 380, anchor=CENTER, window=music_btn)

def new_game():
    root.withdraw()  # Hide root window, to make it visible again use root.deiconify()

    global new_game_bg
    global new_game_window

    new_game_window = Toplevel()
    new_game_window.title("HangMan")
    new_game_window.iconbitmap("Hangman.ico")
    new_game_window.geometry("800x400")
    new_game_window.resizable(width=False, height=False)
    new_game_window.protocol("WM_DELETE_WINDOW", disable_event)  # Disable window "X" (close) button
    # new_game_window.lift()
    new_game_window.attributes("-topmost", "true")

    # Create canvas and add background
    canvas_new_game = Canvas(new_game_window, width="800", height="450")
    canvas_new_game.pack()

    new_game_bg = ImageTk.PhotoImage(Image.open("game_bg.jpg").resize((800, 450), Image.Resampling.LANCZOS))
    canvas_new_game.background = new_game_bg
    canvas_new_game.create_image(0, 0, anchor=NW, image=new_game_bg)

    instructions_lbl = Label(new_game_window, text="There are 4 different categories.\n"
                                                   "Choose as many as you'd like,"
                                                   "\nbut do choose wisely, this is not going to be easy!",
                             bg="#a5a0b6",font=('Calibri', 10, 'bold'))
    canvas_new_game.create_window(400, 60, anchor=CENTER, window=instructions_lbl)

    # Will help knowing which categories were chosen
    opt_1 = StringVar(value="")
    opt_2 = StringVar(value="")
    opt_3 = StringVar(value="m")
    opt_4 = StringVar(value="")

    words_btn = Checkbutton(new_game_window, text="Words", variable=opt_1, onvalue="w", offvalue="")
    canvas_new_game.create_window(340, 120, anchor=CENTER, window=words_btn)
    games_btn = Checkbutton(new_game_window, text="Computer Games", variable=opt_2, onvalue="g", offvalue="")
    canvas_new_game.create_window(463, 120, anchor=CENTER, window=games_btn)
    movies_btn = Checkbutton(new_game_window, text="Movies", variable=opt_3, onvalue="m", offvalue="")
    canvas_new_game.create_window(340, 170, anchor=CENTER, window=movies_btn)
    scientist_btn = Checkbutton(new_game_window, text="Scientists", variable=opt_4, onvalue="s", offvalue="")
    canvas_new_game.create_window(440, 170, anchor=CENTER, window=scientist_btn)
    start_new_game_btn = Button(new_game_window, text="Start new game", width=15,
                                command=lambda: [prepare(opt_1.get() + opt_2.get() + opt_3.get() + opt_4.get())]
                                , borderwidth=5)
    canvas_new_game.create_window(390, 220, anchor=CENTER, window=start_new_game_btn)

    back_menu_btn = Button(new_game_window, text="Main Menu", width=15, command=lambda: [main_menu_(),
                                                                                         new_game_window.destroy()]
                           , borderwidth=5)
    canvas_new_game.create_window(390, 260, anchor=CENTER, window=back_menu_btn)

    music_btn = Button(new_game_window, text="Background Music", command=play_music, borderwidth=5)
    canvas_new_game.create_window(700, 380, anchor=CENTER, window=music_btn)

# choice variable will contain the user's wanted category for the game

def prepare(choice):  
 global count_lines
 # Create file of words from chosen categories from MySQL database

 try:
     cnx = mysql.connector.connect(user='shrihari', password='Hanuman5!',
                                  host='127.0.0.1',
                                  database='python_schema')
     cursor = cnx.cursor()
 except mysql.connector.Error as err:
     if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
     elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
     else:
        print(err)
 else:
    # Build the MySQL queries 
     mov_query = "SELECT movie_name FROM movies"
     gam_query = "SELECT Game_Name FROM games"
     sci_query = "SELECT Scientist_Name FROM scientists"
     word_query = "SELECT Word FROM words"
     categories = ""
     file = open("word_list.txt", "w")  # File which will contain words/names from chosen categories
     
     if "w" or "g" or "m" or "s" in choice:
        if "m" in choice:
            categories += "Movies / "
            cursor.execute(mov_query)
            for (movie_name) in cursor:
                file.write(str(movie_name[0])+"\n") # "\n" is not in the column movie_name
        if "g" in choice:
            categories += "Games / "
            cursor.execute(gam_query)
            for (Game_Name) in cursor:
                file.write(str(Game_Name[0]))
        if "s" in choice:
            categories += "Scientists / "
            cursor.execute(sci_query)
            for (Scientist_Name) in cursor:
                file.write(str(Scientist_Name[0]))
        if "w" in choice:
            categories += "Words / "
            cursor.execute(word_query)
            for (Word) in cursor:
                file.write(str(Word[0]))
     categories = categories[0:-3]  # Will go in label
     file.close()
     cnx.close()
     cursor.close()
 
# Get line count of the file with possible words to guess
     categories_file = open("word_list.txt", "r")
     count_lines = get_lines_count(categories_file)
     categories_file.close()

# Get random word for the user to guess
     random_num = random.randint(1, count_lines)  # Get a random integer
     word_to_guess = get_word(random_num)
     word_to_guess = word_to_guess[0:-1]  # Remove the "\n" char

# Count word chars
     chars_count = get_chars_count(list(word_to_guess))

# Create a variable same length as word to guess but made from _
     under_lines_guess = hide_word(word_to_guess)
     play(under_lines_guess, word_to_guess, chars_count)
     
def hide_word(word):
    hidden = ""
    for hide in range(len(word)):  # for 0 in (x-1)
        if word[hide] == " ":
            hidden += " "
        else:
            hidden += "_"
    return hidden

def get_chars_count(count_chars):
    counter_chars = 0
    for i in count_chars:
        if i != " ":
            counter_chars += 1
    return counter_chars

def get_lines_count(file): 
    count = 0
    for line in file:  # For each line count 1+1+...
        count = count+1
    return count    

def get_word(random_number):
    global count_lines
    f = open("word_list.txt", "r")
    lines = f.readlines()
    ret = lines[random_number - 1]
    f.close()
    f_new = open("word_list.txt", "w")
    for line in lines:  # Write all lines to the file except the one with the word used
        if line != lines[random_number - 1]:
            f_new.write(line)
    f_new.close()

    count_lines -= 1  # Since one line is gone (used and deleted)
    return ret

def my_answer():
    global chars_bank #Alredy guessed letters
    global wordd
    global counter
    global guesses
    global list_chars_bank
    global under_lines
    global word_change
    global letter_change
    global score_count
    global game_count
    
    if e.get()[0:1] in "\n =+-*/.`~!@#$%^&*()_,';:":
        messagebox.showwarning("Illegal input",
                               "Input is illegal. Enter a character in the range of (a-z) and (0-9)",parent=play_window)
        e.delete(0, "end")
        return
    if e.get()[0:1] in chars_bank:
        messagebox.showwarning("Illegal input",
                               "Input was used before.",parent=play_window)
        e.delete(0, "end")
        return
    else:
        len_align = (len(chars_bank) + 1) % 10
        if len_align == 0:
            chars_bank += "\n"
        chars_bank += e.get()[0:1]
        if e.get()[0:1].upper() in str(answer).upper():  # upper in order to ignore if the letter is written
            while e.get()[0:1].upper() in str(answer).upper():  # Check if its there more than once
                i = upper_word_list.index(e.get()[0:1].upper())  # Returns index of the letter guessed
                under_lines[i] = answer[i]
                answer[i] = " "
                upper_word_list[i] = " "
                counter -= 1
                if counter == 0:
                    game_count = game_count + 1
                    score_count = score_count + 1
                    # initialize Text-to-speech engine  
                    engine = pyttsx3.init()  
                    # convert this text to speech  
                    text = "Congratulations You win"  
                    engine.say(text)  
                    # play the speech  
                    engine.runAndWait()
                    messagebox.showinfo("WINNER", "Congratulations!!! - You win!!!",parent=play_window)
                    answer_ = messagebox.askyesno("HangMan", "Would you like to play again?",parent=play_window)
                    if answer_ == 0:
                        quit_game()
                    else:
                        if os.path.isfile("word_list.txt"):  # In case the file was created
                            os.remove("word_list.txt")  # Delete file (no longer needed)
                        new_game_window.destroy()
                        play_window.destroy()
                        root.deiconify()
                        # score_count += 1
        else:
            guesses -= 1
            if guesses == 4:
                play_bg4 = ImageTk.PhotoImage(Image.open("four_guesses.jpg").resize((800, 450), Image.Resampling.LANCZOS))
                canvas_play.background = play_bg4
                canvas_play.create_image(0, 0, anchor=NW, image=play_bg4)
            if guesses == 3:
                play_bg3 = ImageTk.PhotoImage(Image.open("three_guesses.jpg").resize((800, 450), Image.Resampling.LANCZOS))
                canvas_play.background = play_bg3
                canvas_play.create_image(0, 0, anchor=NW, image=play_bg3)
            if guesses == 2:
                play_bg2 = ImageTk.PhotoImage(Image.open("two_guesses.jpg").resize((800, 450), Image.Resampling.LANCZOS))
                canvas_play.background = play_bg2
                canvas_play.create_image(0, 0, anchor=NW, image=play_bg2)
            if guesses == 1:
                play_bg1 = ImageTk.PhotoImage(Image.open("one_guesses.jpg").resize((800, 450), Image.Resampling.LANCZOS))
                canvas_play.background = play_bg1
                canvas_play.create_image(0, 0, anchor=NW, image=play_bg1)
            if guesses == 0:
                play_bg0 = ImageTk.PhotoImage(Image.open("zero_guesses.jpg").resize((800, 450), Image.Resampling.LANCZOS))
                canvas_play.background = play_bg0
                canvas_play.create_image(0, 0, anchor=NW, image=play_bg0)
                game_count = game_count + 1
                # initialize Text-to-speech engine  
                engine = pyttsx3.init()  
                # convert this text to speech  
                text = "Sorry You loose. Please try again"  
                engine.say(text)  
                # play the speech  
                engine.runAndWait()
                messagebox.showinfo("SORRY", "You lose!\nThe correct answer was: " + wordd.upper(),parent=play_window)
                answer_ = messagebox.askyesno("HangMan", "Would you like to play again?",parent=play_window)
                if answer_ == 0:
                    quit_game()
                else:
                    word_change = 2
                    letter_change = 1
                    if os.path.isfile("word_list.txt"):  # In case the file was created
                        os.remove("word_list.txt")  # Delete file (no longer needed)
                    new_game_window.destroy()
                    play_window.destroy()
                    root.deiconify()

    e.delete(0, "end")

    list_chars_bank = list(chars_bank)
    bank_lbl = Label(play_window, text="Used characters bank:\n" + " ".join(list_chars_bank).upper(),bg="#FFB6C1") # bg -> colour code
    canvas_play.create_window(82, 270, anchor=CENTER, window=bank_lbl)

    underlines_lbl = Label(play_window, text=" ".join(under_lines),bg="#98FB98")
    canvas_play.create_window(400, 310, anchor=CENTER, window=underlines_lbl)

    guesses_lbl = Label(play_window, text="You have " + str(guesses) + " guesses left")
    canvas_play.create_window(400, 340, anchor=CENTER, window=guesses_lbl)

def play(hidden, word, count):
    new_game_window.withdraw()
    global play_bg
    global play_window
    global canvas_play
    global chars_bank
    global e
    global answer
    global upper_word_list
    global under_lines
    global wordd
    wordd = word
    global guesses
    guesses = 5
    global counter
    counter = count
    global list_chars_bank
    chars_bank = ""
    list_chars_bank = list(chars_bank)

    global word_change

    global letter_change

    play_window = Toplevel()
    play_window.title("HangMan")
    play_window.iconbitmap("images/Hangman.ico")
    play_window.geometry("800x400")
    play_window.resizable(width=False, height=False)
    play_window.protocol("WM_DELETE_WINDOW", disable_event)  # Disable window "X" (close) button
    play_window.attributes("-topmost", "true")

    # Create canvas and add background
    canvas_play = Canvas(play_window, width="800", height="450")
    canvas_play.pack()

    play_bg = ImageTk.PhotoImage(Image.open("images/game_bg.jpg").resize((800, 450), Image.Resampling.LANCZOS))
    canvas_play.background = play_bg
    canvas_play.create_image(0, 0, anchor=NW, image=play_bg)

    under_lines = list(hidden)  # Will make it easier to change chars in string
    answer = list(word)  # When done, do - "".join(list to join as string)
    upper_word = word.upper()
    upper_word_list = list(upper_word)
    chars_bank = ""

    underlines_lbl = Label(play_window, text=" ".join(under_lines),bg="#98FB98")
    canvas_play.create_window(400, 210, anchor=CENTER, window=underlines_lbl)

    guesses_lbl = Label(play_window, text="You have " + str(guesses) + " guesses left")
    canvas_play.create_window(400, 240, anchor=CENTER, window=guesses_lbl)

    bank_lbl = Label(play_window, text="Used characters bank:\n" + " ".join(list_chars_bank).upper(),bg="#FFB6C1")
    canvas_play.create_window(82, 170, anchor=CENTER, window=bank_lbl)

    back_menu_btn_ = Button(play_window, text="Main Menu", borderwidth=5, width=15,
                            command=lambda: [main_menu_(),
                                             play_window.destroy(),
                                             new_game_window.destroy()])
    canvas_play.create_window(82, 270, anchor=CENTER, window=back_menu_btn_)

    e = Entry(play_window, width=4, borderwidth=2,bg="#FFE4E1")
    canvas_play.create_window(380, 150, anchor=CENTER, window=e)
    
    input_answer = Button(play_window, text="Confirm", command=my_answer, borderwidth=5)
    canvas_play.create_window(430, 150, anchor=CENTER, window=input_answer)

    music_btn = Button(play_window, text="Background Music", command=play_music, borderwidth=5)
    canvas_play.create_window(700, 370, anchor=CENTER, window=music_btn)
    # play_window.attributes("-topmost", "true")
    # canvas_play.focus_set()
    play_window.protocol("wm focusmodel active") # try to put focus on textbox after activating the parent window
    e.focus()
    e.insert(END,"")
    
def score_board():
    messagebox.showinfo('Score-Board', "Games Played  :             " + str(game_count) + "\n"+"Successul Guesses  :     " + str(score_count) + "\n"+"Unsuccessul Guesses : " + str(game_count - score_count))
    return

def quit_game():
    pygame.mixer.music.stop()
    if os.path.isfile("word_list.txt"):  # In case the file was created
        os.remove("word_list.txt")  # Delete file (no longer needed)
    root.destroy()

main_menu_()  # Start game
root.mainloop()

