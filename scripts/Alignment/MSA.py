from NW import Needleman_Wunsch

pairwise = Needleman_Wunsch()

a = 'öåöäöåöäöååöäö'
b = 'öåäöäöåäöäöåöä'
result = pairwise.run(a,b)

print(result)
print(result[0])
print(result[1])
print(result[2])