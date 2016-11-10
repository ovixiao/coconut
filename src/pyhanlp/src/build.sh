rm -rf Hanlp.class

FILE_PATH=`pwd`/`dirname $0`
HANLP_LIB_PATH=${FILE_PATH}/../lib/hanlp-1.3.1.jar
PY4J_LIB_PATH=/usr/local/share/py4j/py4j0.10.4.jar
javac -cp ${HANLP_LIB_PATH}:${PY4J_LIB_PATH} Hanlp.java
