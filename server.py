import socket

# TCP server variables
TCP_IP = '127.0.0.1'
TCP_PORT = 0
BUFFER_SIZE = 1024

# Global game variables
GAME_WORD = ""
GAME_CATEGORY = ""
GAME_OPPONENT_ATTEMPTS = 0

# OpCodes
# 0. Exit game with no warning
# 1. Setup game
# 2. Letter guess
# 3. Player win
# 4. Player lose


def handle_opcode(opcode):
    # Echo the opcode back to the client
    client_connection.send(opcode)

    # Close program opcode
    if bytes.decode(opcode) == "0":
        client_connection.close()
        quit()
    # Game setup opcode
    elif bytes.decode(opcode) == "1":
        global GAME_CATEGORY
        global GAME_WORD
        # Creates an empty data stream
        game_data = ""

        # Sets the word category and adds it to the data stream
        GAME_CATEGORY = input("Choose a category: ")
        while not GAME_CATEGORY.isalpha() or len(GAME_CATEGORY) < 1:
            print("That is not a valid category, please try again!")
            GAME_CATEGORY = input("Choose a category: ")
        game_data += GAME_CATEGORY

        game_data += ","

        # Sets the word and stores it in a global variable

        GAME_WORD = input("Choose a word: ").lower()
        while not GAME_WORD.isalpha() or len(GAME_WORD) < 1:
            print("That is not a valid word choice, please try again!")
            GAME_WORD = input("Choose a word: ").lower()

        # Adds the chosen words length to the data stream
        game_data += str(len(GAME_WORD))

        # Sends the data stream to the client
        client_connection.send(str.encode(game_data))
    # Letter guess received opcode
    elif bytes.decode(opcode) == "2":
        global GAME_OPPONENT_ATTEMPTS

        print("Waiting for your opponent to guess a letter...")

        while True:
            # Waits for additional data
            data_recv = client_connection.recv(BUFFER_SIZE)

            # Ran once data has been received
            if data_recv:
                # Decodes the received letter guess
                received_letter = bytes.decode(data_recv)

                # Tells the host what letter was guessed
                print("Your opponent guessed the letter:", received_letter)

                # Tells the user their guess was incorrect
                if GAME_OPPONENT_ATTEMPTS != 5:
                    print("Your opponent has",
                          5 - GAME_OPPONENT_ATTEMPTS, "attempts left!")
                else:
                    print("Your opponent has",
                          5 - GAME_OPPONENT_ATTEMPTS, "attempt left!")

                # Separator for formatting purposes
                print("----------------------------")

                # Checks if the guessed letter is in the chosen word
                if received_letter in GAME_WORD:
                    # Creates a list of all the indexes of the chosen word
                    # that contain the guessed letter
                    success_indexes = [
                                       i for i,
                                       letter in enumerate(GAME_WORD)
                                       if letter == received_letter
                                      ]

                    # Creates an empty data stream
                    game_data = ""

                    # Loops through each element in the successful
                    # indexes list
                    for x in range(0, len(success_indexes)):
                        # Adds each letter index to the data stream using
                        # commas as separators
                        game_data += str(success_indexes[x])
                        game_data += ","
                    # Sends the letter guess data to the client
                    client_connection.send(str.encode(game_data))
                # Returns false if the guessed letter is not
                # in the chosen word
                else:
                    # Adds one to the opponent attempt counter
                    GAME_OPPONENT_ATTEMPTS += 1

                    # Sends a false code to the client
                    client_connection.send(str.encode("false"))

                # Breaks out of the listening loop
                break
    # Player win opcode handling
    elif bytes.decode(opcode) == "3":
        # Tells the host that the opponent won
        print("Your opponent has won!")
        print("Thanks for playing!")

        # Sends a success response to client
        client_connection.send(str.encode("true"))
    # Player lose opcode handling
    elif bytes.decode(opcode) == "4":
        # Tells the host that the opponent lost
        print("Your opponent has ran out of guesses, you win!")
        print("Thanks for playing!")

        # Sends a success response to client
        client_connection.send(str.encode("true"))


# Welcome messages
print("Welcome to pyHangman!")
print("The goal of the game is to choose a word from a category that you "
      "choose and hope your opponent can't guess it within their 6 attempts.")

# Asks the host for a port and checks if it is valid
while TCP_PORT < 1024 or TCP_PORT > 65535:
    try:
        TCP_PORT = int(input("Choose a port between 1024 and 65535: "))
    except ValueError:
        pass

# Opens the server socket and binds to the given port
game_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
game_socket.bind((TCP_IP, TCP_PORT))
game_socket.listen(1)

print("Waiting for client connection...")

# game_socket.accept() returns two values, the connection and the addr info
# client_connection is set to the socket connection and client_address
# is set to the socket addr info
client_connection, client_address = game_socket.accept()

# Prints the client's connection IP
print('Client IP:', client_address[0])

# Listens for data as long as a client connection exists
while client_connection:
    # Stores received data in data variable
    data = client_connection.recv(BUFFER_SIZE)
    # Handles the received opcode
    handle_opcode(data)
# Closes the connection at the end of the program
client_connection.close()
