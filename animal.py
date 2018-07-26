class Hunter:
    def __init__(self, name, animal):
        self.name = name
        self.animal = animal

    # 사냥꾼이 데리고 다니는 동물에게 사냥명령
    def hunt(self):
        print(f'{self.animal.name} 공격해라!')
        # 헌터는 애니멀에게 울라고 할뿐, 애니멀이 어떻게 우는지는 신경쓰지 않는다.(추상화)
        # 객체지향프로그램의 철학 -> 프로그래밍을 최대한 현실세계와 비슷하게
        self.animal.cry()

    # 추상화시키지 않은 막장코드
    # 만약 동물이 100마리면?
    def hunt_with_dog(self):
        print(f'{self.animal.name} 공격해라!')
        print(f'멍멍!')

    def hunt_with_eagle(self):
        print(f'{self.animal.name} 공격해라!')
        print(f'휘잉~')


# 고급 -> 상속
# 상속을 쓰지 않으면 Dog, Eagle이 정말 동물인지 아닌지(=같은 종류인지) 알 수 없다
class Animal:
    def __init__(self, name):
        self.name = name

    # 슈퍼클래스의 의미
    # 동물이라면 울 줄 알아야 한다?
    # 다른 언어에서는 상속받을때 반드시 오버라이딩해줘야 하는 메소드들이 있는데 파이썬은 모르겠음
    def cry(self):
        pass


# Dog는 Animal을 상속받음으로써 동물이 된다
class Dog(Animal):
    def __init__(self, name):
        super().__init__(name)

    # 상속받은 메소드를 다시 만들기 -> 오버라이딩
    def cry(self):
        print("멍멍!")

    # 모든 동물이 꼬리흔들기를 할 수 없다
    # 그러나 Dog는 꼬리흔들기를 할 수 있는 동물이다
    def 꼬리흔들기(self):
        pass


class Eagle(Animal):
    def __init__(self, name):
        super().__init__(name)

    def cry(self):
        print("휘잉~")

    # 모든 동물이 꼬리흔들기를 할 수 없다
    # 그러나 Dog는 꼬리흔들기를 할 수 있는 동물이다
    def 꼬리흔들기(self):
        pass

멍멍이 = Dog("멍멍이")
대머리독수리 = Eagle("대머리독수리")

lee = Hunter("너님", 대머리독수리)
kim = Hunter("나님", 멍멍이)

kim.hunt_with_dog()
lee.hunt_with_eagle()

kim.hunt()  # 간지나는 OOP 코드

print(isinstance(멍멍이, Dog)) # True

# 멍멍이, 대머리독수리 모두 동물이다(다형성)
print(isinstance(멍멍이, Animal))  # True
print(isinstance(대머리독수리, Animal))  # True
