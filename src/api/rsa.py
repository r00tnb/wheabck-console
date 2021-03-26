
import random
import decimal
decimal.getcontext().prec = decimal.MAX_PREC
decimal.getcontext().Emax = decimal.MAX_EMAX
decimal.getcontext().Emin = decimal.MIN_EMIN

class RSA:

    def __init__(self, bit_length=1024):
        self.bit_length = bit_length
        self.context = decimal.Context(decimal.MAX_PREC, Emax=decimal.MAX_EMAX, Emin=decimal.MIN_EMIN)

        self.__secret_key = None # 私钥
        self.__pub_key = None # 公钥
    
    @property
    def secret(self):
        if self.__secret_key is None:
            self.generate_key()
        return self.__secret_key
    
    @property
    def public(self):
        if self.__pub_key is None:
            self.generate_key()
        return self.__pub_key

    def _gcd(self, a:int, b:int)->int:
        '''使用欧几里得算法求a，b的最大公约数
        '''
        while b != 0:
            tmp = b
            b = self.context.power(a, 1, b)
            a = tmp

        return int(a)

    def _ex_gcd(self, a:int, b:int)->tuple:
        '''扩展欧几里得算法求ax+by=gcd(a,b)的一组整数解
        '''
        if b == 0:
            return 1, 0

        x, y = self._ex_gcd(b, self.context.power(a, 1, b))
        return int(y), int(x-self.context.multiply(self.context.divide_int(a, b), y))
        
    def generate_key(self):
        '''生成一对公钥和私钥
        '''
        p, q, n = self.__generate_necessary_num()
        eul = self.context.multiply(p-1, q-1)
        e = 65537
        while True:
            k = random.randint(2, eul-1)
            if self._gcd(k, eul) == 1:
                e = k
                break
        d, tmp = self._ex_gcd(e, eul)
        self.__pub_key = (n, e)
        self.__secret_key = (n, d)

    def encrypt(self, msg:bytes)->bytes:
        pass

    def __generate_necessary_num(self)-> list:
        '''生成必要的三个大整数:p, q, n 其中p，q为质数且不相等，n为pq的积且二进制位数为指定的位数self.bit_length
        '''
        p = [0, 0, 0]
        min_num = self.context.power(2, (self.bit_length-1)//2)
        max_num = self.context.power(2, round(self.bit_length/2))
        while True:
            for i in range(2):
                while True:
                    k = random.randint(min_num, max_num)
                    if p[i-1:i] and k == p[i-1]:
                        continue
                    if self.__miller_rabin(k):
                        p[i] = k
                        break
            p[2] = int(self.context.multiply(p[0], p[1]))
            if p[2].bit_length() == self.bit_length:
                break
        return p

    def __miller_rabin(self, n: int)-> bool:
        '''使用Miller-Rabin算法判断输入是否是一个质数
        '''
        test_time = 2
        bit_length = n.bit_length()
        if bit_length < 512:
            test_time = 50
        elif bit_length < 1024:
            test_time = 20
        elif bit_length < 2048:
            test_time = 8

        n = self.context.abs(n)
        if n in (1, 0) or n%2 == 0:
            return False
        elif n == 2:
            return True

        for j in range(test_time):
            a = random.randint(2, n-2)
            tmp = n-1
            s = 0
            while tmp%2 == 0:
                tmp = tmp/2
                s += 1
            d = tmp
            x = [0, 0]
            x[0] = self.context.power(a, d, n)
            for i in range(s):
                x[1] = self.context.power(x[0], 2, n)
                if x[1] == 1 and x[0] != 1 and x[0] != n-1:
                    return False
                x[0] = x[1]
            if x[1] != 1:
                return False

        return True


if __name__ == '__main__':
    a = RSA(255)
    print(a.public, a.secret)