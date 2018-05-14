# Driver code
import argparse
from pyspark.sql import SparkSession
import thread as _thread
import time
from pyspark.accumulators import AccumulatorParam


class PasswordAccumulator(AccumulatorParam):
    def zero(self, v):
        return ""

    def addInPlace(self, variable, value):
        variable += value
        return variable


def checkPassword(threadName, accumulator, sc):
    while True:
        print("\n\n\n * * * * * * Thread in execution: " + threadName)
        time.sleep(300)
        if accumulator.value != "":
            for i in range(0, 30):
                print("Password Found: " + accumulator.value)
            sc.stop()
            return


def main():
    # Get arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--file", required=True,
                    help="handshake file")
    ap.add_argument("-s", "--SSID", required=True,
                    help="AP name")
    ap.add_argument("-d", "--dictionary", required=True,
                    help="Dictionary path")
    args = vars(ap.parse_args())

    # File which contains EAPOL packages
    handShakeFile = args['file']

    # SSID name
    ssid = args['SSID']

    # Complete path of the dictionary (HDFS, S3 ...)
    dictPath = args['dictionary']

    # Load Spark
    spark = SparkSession \
        .builder \
        .appName("NotASmurfCracker") \
        .getOrCreate()

    rdd = spark.sparkContext.textFile(dictPath).coalesce(30)
    accu = spark.sparkContext.accumulator("", PasswordAccumulator())

    numberPartitions = rdd.getNumPartitions()
    print("\n\n\n * * * * * *  Dictionary Number of Partitions: {0}".format(str(numberPartitions)))
    print("Got SSID %s handshake %s" % (ssid, handShakeFile))

    # Start the thread to check password accumulator
    _thread.start_new_thread(checkPassword, ("PasswordCheck", accu, spark.sparkContext))

    # Function executed by workers
    def crack(file, ssid, partition):
        import cracker.crack
        psswd = cracker.crack.runHashCat(file, ssid, partition)
        if psswd != False:
            accu.add(psswd)
        return

    try:
        rdd.foreachPartition(
            lambda partition: crack(handShakeFile, ssid, partition))
    except Exception:
        print("Driver Exception: Password Found?")

main()