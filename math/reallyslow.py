def is_prime(num):
    if num <= 1:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True

for n in range(1, 201):
    num = 2**n - 1
    if is_prime(num):
        print(f"{n} is prime and 2^{n} - 1 is prime")
    else:
        print(f"{n} is prime but 2^{n} - 1 is not prime")

#suppose N is an integer larger than 1 and n is prime. Then 2^n - 1 is prime. 