h = 5
l = -9




print("Rialzistsa", abs(h) > abs(l*2))

print("Ribassista", abs(l) > abs(h*2))

apre = 1928095
chiude = 100
alto = 750
basso = -150


def isLittleBodyRib():
    return abs((apre + chiude) - apre) <= (abs((apre + alto)) -  abs((apre + chiude))) / 3

def isLittleBodyRalz():
    return abs((apre + chiude) - apre) <= (abs((apre + basso)) -  abs((apre + chiude))) / 3




print(isLittleBodyRib())