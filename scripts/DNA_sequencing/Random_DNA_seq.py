def Random_DNA_seq(number):
    #Imports random module
    import random

    #A list of possible nucleotides
    list_of_nucleotides = ['A','T','G','C']

    #Input the sequence length and makes the input (string) into an integer
    length = number

    #Empty string used for the sequence
    sequence = ''

    #For loop, iterates for the length of the sequence
    for i in range(0, length):

        #Adds a random integer to the sequence string (25% for each nucleotide)
        sequence += random.choice(list_of_nucleotides)

    #Returns the sequence
    return sequence
