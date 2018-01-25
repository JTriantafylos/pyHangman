import socket

# TCP server variables
TCP_PORT = 0
BUFFER_SIZE = 1024

# Global game variables
GAME_CATEGORY = ""
GAME_WORD_LENGTH = 0
GAME_WORD_PROGRESS = list("")
GAME_GUESSED_LETTERS = []
GAME_ATTEMPT = 0
GAME_SETUP = False
GAME_WIN = False


# Draws the current progress of the word guessing
def draw_progress():
    global GAME_SETUP
    global GAME_WORD_PROGRESS

    if not GAME_SETUP:
        counter = 0
        while counter < GAME_WORD_LENGTH:
            # Adds an underscore to the word progress string
            GAME_WORD_PROGRESS += "_"

            counter += 1

        GAME_SETUP = True
    # Returns the word progress as a string with spaces between each char
    return " ".join(GAME_WORD_PROGRESS)


# Draws out an ASCII hangman character,
# word progress and guessed letters.
# Takes attempt number as an argument
def draw_hangman(attempt):
    if attempt == 0:
        print(" _________     ")
        print("|         |    ")
        print("|              ")
        print("|              ")
        print("|              ")
        print("|              ")
        print("|              ")
        print("Word:", draw_progress())
        print("Guessed letters:", GAME_GUESSED_LETTERS)
    elif attempt == 1:
        print(" _________     ")
        print("|         |    ")
        print("|         0    ")
        print("|              ")
        print("|              ")
        print("|              ")
        print("|              ")
        print("Word:", draw_progress())
        print("Guessed letters:", GAME_GUESSED_LETTERS)
    elif attempt == 2:
        print(" _________     ")
        print("|         |    ")
        print("|         0    ")
        print("|         |    ")
        print("|              ")
        print("|              ")
        print("|              ")
        print("Word:", draw_progress())
        print("Guessed letters:", GAME_GUESSED_LETTERS)
    elif attempt == 3:
        print(" _________     ")
        print("|         |    ")
        print("|         0    ")
        print("|        /|    ")
        print("|              ")
        print("|              ")
        print("|              ")
        print("Word:", draw_progress())
        print("Guessed letters:", GAME_GUESSED_LETTERS)
    elif attempt == 4:
        print(" _________     ")
        print("|         |    ")
        print("|         0    ")
        print("|        /|\\  ")
        print("|              ")
        print("|              ")
        print("|              ")
        print("Word:", draw_progress())
        print("Guessed letters:", GAME_GUESSED_LETTERS)
    elif attempt == 5:
        print(" _________     ")
        print("|         |    ")
        print("|         0    ")
        print("|        /|\\  ")
        print("|        /     ")
        print("|              ")
        print("|              ")
        print("Word:", draw_progress())
        print("Guessed letters:", GAME_GUESSED_LETTERS)
    elif attempt == 6:
        print(" _________     ")
        print("|         |    ")
        print("|         0    ")
        print("|        /|\\  ")
        print("|        / \\  ")
        print("|              ")
        print("|              ")
        print("Word:", draw_progress())
        print("Guessed letters:", GAME_GUESSED_LETTERS)


# Creates the TCP socket for a potential MP game
host_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# OpCodes
# 0. Exit game with no warning
# 1. Setup game
# 2. Letter guess
# 3. Player win
# 4. Player lose


# Send opcode as the initial message and extra data as additional messages
def send_opcode(opcode):
    # Try catch to properly send the opcode to the server
    try:
        # Sends the opcode
        host_connection.send(str.encode(opcode))

        # Continues looping until an opcode echo is received
        while True:
            # Waits for an opcode echo
            opcode_recv = host_connection.recv(BUFFER_SIZE)

            if bytes.decode(opcode_recv) == "0":
                # Shuts the server connection
                host_connection.close()
                break

            # Game setup opcode handling
            elif bytes.decode(opcode_recv) == "1":
                # Tells the user what data is being waited on
                print("Waiting for the host to choose a word and category...")

                # Continues looping until additional data is received
                while True:
                    # Waits for additional data
                    data_recv = host_connection.recv(BUFFER_SIZE)

                    # Ran once data has been received
                    if data_recv:
                        # Splits the additional data at the commas
                        data_recv = bytes.decode(data_recv).split(",")

                        # Stores the chosen word category in a global variable
                        global GAME_CATEGORY
                        GAME_CATEGORY = data_recv[0]

                        # Stores the chosen word length in a global variable
                        global GAME_WORD_LENGTH
                        GAME_WORD_LENGTH = int(data_recv[1])

                        # Tells the user what the word category is
                        print("The category of the word is:", GAME_CATEGORY)

                        # Breaks out of the listening loop
                        break
            # Letter guess opcode handling
            elif bytes.decode(opcode_recv) == "2":

                # References the global guessed letters list
                global GAME_GUESSED_LETTERS

                # Asks the user for a letter guess
                chosen_letter = str(input("Guess a letter: ")).lower()

                # Loops until the user guesses a valid letter
                while chosen_letter == "" \
                        or chosen_letter in GAME_GUESSED_LETTERS \
                        or not chosen_letter.isalpha()\
                        or len(chosen_letter) > 1:
                    # Tells the user that their guess is invalid
                    print("That is not a valid guess, please try again!")
                    # Asks the user to guess a letter
                    chosen_letter = str(input("Guess a letter: "))

                GAME_GUESSED_LETTERS += chosen_letter

                # Creates an empty data stream
                game_data = ""

                # Adds the guessed letter to the data stream
                game_data += chosen_letter

                # Sends the data stream to the server
                host_connection.send(str.encode(game_data))

                # Separator for formatting purposes
                print("----------------------------")

                # Continues looping until additional data is received
                while True:
                    # Waits for additional data
                    data_recv = host_connection.recv(BUFFER_SIZE)
                    # Ran once data has been received
                    if data_recv:
                        # Checks if the letter guess was correct
                        if bytes.decode(data_recv) != "false":
                            # Tells the user their guess was correct
                            print("Your guess was correct!")

                            # Splits the additional data at the commas
                            data_recv = bytes.decode(data_recv).split(",")

                            # Adds the chosen letter to the correct spaces
                            # in the progress word
                            for x in range(0, len(data_recv) - 1):
                                GAME_WORD_PROGRESS[int(data_recv[x])]\
                                    = chosen_letter

                            # Checks if the progress word contains
                            # any more underscores
                            if "_" not in GAME_WORD_PROGRESS:
                                # Sends the player win opcode
                                send_opcode("3")
                        else:
                            global GAME_ATTEMPT

                            # Adds one to the global attempts variable
                            GAME_ATTEMPT += 1

                            # Checks if the user is out of attempts yet
                            if GAME_ATTEMPT != 6:

                                # Tells the user their guess was incorrect
                                if GAME_ATTEMPT != 5:
                                    print("Your guess was incorrect, you have",
                                          6 - GAME_ATTEMPT, "attempts left!")
                                else:
                                    print("Your guess was incorrect, you have",
                                          6 - GAME_ATTEMPT, "attempt left!")
                            else:
                                # Sends the player lose opcode
                                send_opcode("4")
                        # Breaks out of the listening loop
                        break
            elif opcode == "3":
                # Sets the win variable to true
                global GAME_WIN
                GAME_WIN = True

                while True:
                    # Waits for additional data
                    data_recv = host_connection.recv(BUFFER_SIZE)
                    # Ran once data has been received
                    if data_recv:
                        break
            elif opcode == "4":
                while True:
                    # Waits for additional data
                    data_recv = host_connection.recv(BUFFER_SIZE)
                    # Ran once data has been received
                    if data_recv:
                        break
            # Ran once data has been received
            if opcode_recv:
                # Breaks out of the listening loop
                break

    # Exception catch for any socket exceptions
    except ConnectionError:
        # Kills the program if the server cannot be reached
        print("Error connecting to server!")
        quit()


# Welcome messages
print("Welcome to pyHangman!")
print("The goal of the game is to guess what word your "
      "opponent chooses for you letter by letter.")

# Asks the user for an IP and checks if it is valid
TCP_IP = input("Enter the IP of the host (127.0.0.1 for localhost): ")
try:
    socket.inet_aton(TCP_IP)
except socket.error:
    print("That is not a valid IP!")
    print("Exiting program!")
    quit()

# Asks the user for a port and checks if it is valid
while TCP_PORT < 1024 or TCP_PORT > 65535:
    try:
        TCP_PORT = int(input("Enter the port of the host: "))
    except ValueError:
        pass

while host_connection:
    # Try catch to handle socket connection exceptions
    try:
        # Connects to the game host
        host_connection.connect((TCP_IP, TCP_PORT))
    except ConnectionError:
        # Kills the program if it cannot connect to the server
        print("Unable to connect to server!")
        quit()
    break

# Sends the game setup opcode
send_opcode("1")

# Draws the empty hangman
draw_hangman(0)

# Checks if the user has any attempts yet and if they've won the game
while GAME_ATTEMPT < 6 and not GAME_WIN:
    # Sends the letter guess opcode
    send_opcode("2")
    # Draws the ASCII hangman as well as word progress
    # and guessed letters
    draw_hangman(GAME_ATTEMPT)

# Handles game win and lose and sends opcode "0" to
# close the connection after
if GAME_WIN:
    print("You guessed the word correctly, you win!")
    print("Thanks for playing!")
else:
    print("You ran out of guesses, you lose!")
    print("Thanks for playing!")
send_opcode("0")