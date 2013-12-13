

def make_uppercase(L):
    for i in range(len(L)):
        L[i] = L[i].upper()

L = ["a", "b", "c"]

print "Before:", L

L = make_uppercase(L)

print "After:", L