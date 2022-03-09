import random
import statistics
import simpy

seed = 67
interval = 10.0
timePerProcess = []
quantity = 25
instructionsPerCycleRange = [1, 10]
ramRequiredRange = [1, 10]
cpuInstructionsPerCicle = 3
totalTime = 0


def process(env, id, cpu, ram, waiting, arriveTime):
    global totalTime
    global timePerProcess
    yield env.timeout(arriveTime)

    start = env.now
    end = 0
    print('Processs %d created at %s' % (id, start))

    instructions = random.randint(*instructionsPerCycleRange)
    ramRequired = random.randint(*ramRequiredRange)

    with ram.get(ramRequired) as rear:
        print('Process %d required %s ram and now is ready at %s' % (id, ramRequired, env.now))

        while instructions > 0:
            with cpu.request() as runningQueue:
                yield runningQueue
                print('Process %d is running at %s' % (id, env.now))
                yield env.timeout(1)
                instructions -= instructionsPerCycleRange

                if instructions <= 0:
                    instructions = 0
                    end = env.now
                    print('Process %d terminated at %s' % (id, end))
                else:
                    isWaiting = random.randint(1, 2)

                    if isWaiting == 1:
                        with waiting.request() as waitingQueue:
                            yield waitingQueue
                            yield env.timeout(1)

    processingDuration = end - start
    timePerProcess.append(processingDuration)
    totalTime = end


def entry(env, cpu, ram, waiting):
    for i in range(quantity):
        startTime = random.expovariate(1.0 / interval)
        env.process(process(env, i, cpu, ram, waiting, startTime))


if __name__ == '__main__':
    random.seed(seed)
    env = simpy.Environment
    ram = simpy.Container(env, init=100, capacity=100)
    cpu = simpy.Resource(env, capacity=1)
    waiting = simpy.Resource(env, capacity=1)

    entry(env, cpu, ram, waiting)
    env.run()

    averageTime = statistics.mean(timePerProcess)
    stdev = statistics.stdev(timePerProcess)

    print(
        "\n\n#############################################################\n Results: \n Execution time: %s \n Average time per process: %s \n Standard deviation: %s" % (
        totalTime, averageTime, stdev))
