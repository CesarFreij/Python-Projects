#   ____                       _____         _  _ 
#  / ___|___  ___  __ _ _ __  |  ___| __ ___(_)(_)
# | |   / _ \/ __|/ _` | '__| | |_ | '__/ _ \ || |
# | |__|  __/\__ \ (_| | |    |  _|| | |  __/ || |
#  \____\___||___/\__,_|_|    |_|  |_|  \___|_|/ |
#                                            |__/

from random import randint

def Guess_number():
    num = randint(1, 10)
    mn = 1; mx = 10
    limit = 3
    out = False

    while limit != 0 and not out:
        try:
            print('#' * 40)
            print("###" + ' ' * 34 + "###")
            print('#' * 40)
            print(f"You only have {limit} tries" if limit > 1 else "Last try")
            g = int(input(f"Guess the number from {mn} => {mx}: "))
            if g > mx or g < mn:
                print(f"Must be between {mn} => {mx}")
                continue
            if num == g:
                out = True
                break
            else:
                if g < num:
                    print("The num is bigger")
                    mn = g + 1
                else:
                    print("The num is smaller")
                    mx = g - 1
                limit -= 1
        except ValueError:
            print("Must be an integer number")
        
    if out:
        print("You've won")
    else:
        print("You've lost")
        print(f"Number is {num}")

Guess_number()

while True:
    yes = input("Do you want to play again?\nyes or no: ")

    if yes.lower().strip() == "yes":
        Guess_number() 
    elif yes == "no":
        print("Thanks for paly") 
        quit()