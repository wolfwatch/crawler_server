from threading import Thread

# Thread가 실행할 함수
def func():
    pass
def func_a(a):
    pass
def func_ab(a, b):
    pass

# Thread 개체
# target: 스레드가 실행할 함수
# args: 함수의 매개변수 (iterable)
th = Thread(target=func)
th2 = Thread(target=func_a, args=(3,))
th3 = Thread(target=func_ab, args=(3, 4))

# python의 Thread는 직접 시작해줘야함
th.start()
th2.start()
th3.start()

# Thread 종료될 때까지 기다리기
th.join()
th2.join()
th3.join()

# 여러 Thread 생성 후 모두 종료될 때까지 기다리기
threads = []
for i in range(0, 100):
    thr = Thread(target=func)
    thr.start()
    threads.append(thr)

for t in threads:
    t.join()    # Thread t가 종료될 때까지 기다리기